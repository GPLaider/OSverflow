/*
 * SPDX-FileCopyrightText: 2026 The OSverflow Project
 * SPDX-License-Identifier: Apache-2.0
 */

package android.ext.compat;

import static android.content.pm.PackageManager.CERT_INPUT_SHA256;
import static android.content.pm.PackageManager.MATCH_ANY_USER;

import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.os.Environment;

import java.io.File;
import java.io.IOException;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.StringJoiner;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.regex.Pattern;

/** @hide */
public final class CompatibilityProfileConfig {
    private static final String RELATIVE_PATH =
            "etc/osverflow/compatibility_profiles.properties";
    private static final Pattern PACKAGE_NAME = Pattern.compile(
            "[A-Za-z_][A-Za-z0-9_]*(\\.[A-Za-z_][A-Za-z0-9_]*)+");
    private static final Pattern SHA256 = Pattern.compile("[0-9a-fA-F]{64}");

    private CompatibilityProfileConfig() {}

    public enum SecurityImpact {
        NONE,
        REDUCES_APP_SECURITY,
        REDUCES_PLATFORM_SECURITY,
    }

    public enum Applicability {
        ACTIVE,
        RETIRED,
        EXPIRED,
        NOT_INSTALLED,
        SIGNER_MISMATCH,
        VERSION_MISMATCH,
    }

    public record Profile(
            String packageName,
            String signerSha256,
            long minVersionCode,
            long maxVersionCode,
            long expiresAtMillis,
            SecurityImpact securityImpact,
            String reason,
            boolean retired,
            Set<Long> ownedChangeIds,
            Map<Long, Boolean> overrides) {

        public String toPlatformConfigString() {
            StringJoiner result = new StringJoiner(",", signerSha256 + "~", "");
            overrides.forEach((changeId, enabled) -> result.add(changeId + ":"
                    + minVersionCode + ":" + maxVersionCode + ":" + enabled));
            return result.toString();
        }

        public Applicability getApplicability(PackageManager pm, long nowMillis) {
            if (retired) {
                return Applicability.RETIRED;
            }
            if (nowMillis >= expiresAtMillis) {
                return Applicability.EXPIRED;
            }

            final ApplicationInfo appInfo;
            try {
                appInfo = pm.getApplicationInfo(packageName, MATCH_ANY_USER);
            } catch (PackageManager.NameNotFoundException e) {
                return Applicability.NOT_INSTALLED;
            }
            if (!pm.hasSigningCertificate(packageName, decodeSha256(signerSha256),
                    CERT_INPUT_SHA256)) {
                return Applicability.SIGNER_MISMATCH;
            }
            if (appInfo.longVersionCode < minVersionCode
                    || appInfo.longVersionCode > maxVersionCode) {
                return Applicability.VERSION_MISMATCH;
            }
            return Applicability.ACTIVE;
        }
    }

    public static File getSystemFile() {
        return new File(Environment.getRootDirectory(), RELATIVE_PATH);
    }

    public static List<Profile> loadSystem() throws IOException {
        return load(getSystemFile());
    }

    public static List<Profile> load(File file) throws IOException {
        Properties properties = new Properties();
        try (Reader reader = Files.newBufferedReader(file.toPath(), StandardCharsets.UTF_8)) {
            properties.load(reader);
        }

        String profileList = properties.getProperty("profiles");
        if (profileList == null) {
            throw new IllegalArgumentException("missing profiles property");
        }

        List<Profile> result = new ArrayList<>();
        Set<String> packages = new LinkedHashSet<>();
        Set<String> allowedKeys = new HashSet<>();
        allowedKeys.add("profiles");
        if (!profileList.trim().isEmpty()) {
            for (String value : profileList.split(",", -1)) {
                String packageName = value.trim();
                if (!PACKAGE_NAME.matcher(packageName).matches()) {
                    throw new IllegalArgumentException("invalid package name: " + packageName);
                }
                if (!packages.add(packageName)) {
                    throw new IllegalArgumentException("duplicate package: " + packageName);
                }
                result.add(parseProfile(properties, packageName, allowedKeys));
            }
        }

        for (String key : properties.stringPropertyNames()) {
            if (!allowedKeys.contains(key)) {
                throw new IllegalArgumentException("unknown property: " + key);
            }
        }
        return Collections.unmodifiableList(result);
    }

    private static Profile parseProfile(Properties properties, String packageName,
            Set<String> allowedKeys) {
        String prefix = packageName + ".";
        String signer = required(properties, prefix, "signer_sha256", allowedKeys)
                .toLowerCase(Locale.ROOT);
        if (!SHA256.matcher(signer).matches()) {
            throw new IllegalArgumentException("invalid SHA-256 for " + packageName);
        }

        long minVersion = nonNegativeLong(required(properties, prefix, "min_version_code",
                allowedKeys), prefix + "min_version_code");
        long maxVersion = nonNegativeLong(required(properties, prefix, "max_version_code",
                allowedKeys), prefix + "max_version_code");
        if (minVersion > maxVersion) {
            throw new IllegalArgumentException("reversed version range for " + packageName);
        }

        long expiry = positiveLong(required(properties, prefix, "expires_at_millis", allowedKeys),
                prefix + "expires_at_millis");
        SecurityImpact impact;
        try {
            impact = SecurityImpact.valueOf(required(properties, prefix, "security_impact",
                    allowedKeys).toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("invalid security impact for " + packageName, e);
        }

        String reason = required(properties, prefix, "reason", allowedKeys);
        if (reason.length() > 512) {
            throw new IllegalArgumentException("reason is too long for " + packageName);
        }
        boolean retired = strictBoolean(required(properties, prefix, "retired", allowedKeys),
                prefix + "retired");
        Set<Long> ownedIds = parseOwnedIds(required(properties, prefix, "owned_change_ids",
                allowedKeys), packageName);
        Map<Long, Boolean> overrides = parseOverrides(
                requiredAllowEmpty(properties, prefix, "overrides", allowedKeys), packageName);

        if (!ownedIds.containsAll(overrides.keySet())) {
            throw new IllegalArgumentException("override is not owned by " + packageName);
        }
        if (retired == !overrides.isEmpty()) {
            throw new IllegalArgumentException(retired
                    ? "retired profile has overrides: " + packageName
                    : "active profile has no overrides: " + packageName);
        }
        return new Profile(packageName, signer, minVersion, maxVersion, expiry, impact, reason,
                retired, Collections.unmodifiableSet(ownedIds),
                Collections.unmodifiableMap(overrides));
    }

    private static String required(Properties properties, String prefix, String field,
            Set<String> allowedKeys) {
        String value = requiredAllowEmpty(properties, prefix, field, allowedKeys).trim();
        if (value.isEmpty()) {
            throw new IllegalArgumentException("empty property: " + prefix + field);
        }
        return value;
    }

    private static String requiredAllowEmpty(Properties properties, String prefix, String field,
            Set<String> allowedKeys) {
        String key = prefix + field;
        allowedKeys.add(key);
        String value = properties.getProperty(key);
        if (value == null) {
            throw new IllegalArgumentException("missing property: " + key);
        }
        return value;
    }

    private static long nonNegativeLong(String value, String key) {
        long result = parseLong(value, key);
        if (result < 0) {
            throw new IllegalArgumentException("negative property: " + key);
        }
        return result;
    }

    private static long positiveLong(String value, String key) {
        long result = parseLong(value, key);
        if (result <= 0) {
            throw new IllegalArgumentException("non-positive property: " + key);
        }
        return result;
    }

    private static long parseLong(String value, String key) {
        try {
            return Long.parseLong(value);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("invalid long property: " + key, e);
        }
    }

    private static boolean strictBoolean(String value, String key) {
        if (!"true".equalsIgnoreCase(value) && !"false".equalsIgnoreCase(value)) {
            throw new IllegalArgumentException("invalid boolean property: " + key);
        }
        return Boolean.parseBoolean(value);
    }

    private static Set<Long> parseOwnedIds(String value, String packageName) {
        Set<Long> result = new TreeSet<>();
        for (String item : value.split(",", -1)) {
            long id = positiveLong(item.trim(), packageName + ".owned_change_ids");
            if (!result.add(id)) {
                throw new IllegalArgumentException("duplicate owned change ID for " + packageName);
            }
        }
        return result;
    }

    private static Map<Long, Boolean> parseOverrides(String value, String packageName) {
        Map<Long, Boolean> result = new TreeMap<>();
        if (value.trim().isEmpty()) {
            return result;
        }
        for (String item : value.split(",", -1)) {
            String[] fields = item.trim().split(":", -1);
            if (fields.length != 2) {
                throw new IllegalArgumentException("invalid override for " + packageName);
            }
            long id = positiveLong(fields[0], packageName + ".overrides");
            Boolean old = result.put(id, strictBoolean(fields[1], packageName + ".overrides"));
            if (old != null) {
                throw new IllegalArgumentException("duplicate override for " + packageName);
            }
        }
        return result;
    }

    private static byte[] decodeSha256(String value) {
        byte[] result = new byte[32];
        for (int i = 0; i < result.length; i++) {
            int offset = i * 2;
            result[i] = (byte) Integer.parseInt(value.substring(offset, offset + 2), 16);
        }
        return result;
    }
}
