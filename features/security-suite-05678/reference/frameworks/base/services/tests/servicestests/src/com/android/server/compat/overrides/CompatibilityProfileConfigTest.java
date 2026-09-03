/*
 * SPDX-FileCopyrightText: 2026 The OSverflow Project
 * SPDX-License-Identifier: Apache-2.0
 */

package com.android.server.compat.overrides;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import android.ext.compat.CompatibilityProfileConfig;

import androidx.test.ext.junit.runners.AndroidJUnit4;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;
import org.junit.runner.RunWith;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.List;

@RunWith(AndroidJUnit4.class)
public class CompatibilityProfileConfigTest {
    private static final String SIGNER =
            "0000000000000000000000000000000000000000000000000000000000000000";

    @Rule public final TemporaryFolder mTemp = new TemporaryFolder();

    @Test
    public void parsesBoundedProfile() throws Exception {
        var profiles = CompatibilityProfileConfig.load(write(validProfile()));

        assertEquals(1, profiles.size());
        var profile = profiles.get(0);
        assertEquals("com.example.app", profile.packageName());
        assertEquals(3, profile.ownedChangeIds().size());
        assertEquals(2, profile.overrides().size());
        assertEquals(SIGNER + "~123:10:20:false,456:10:20:true",
                profile.toPlatformConfigString());
    }

    @Test
    public void rejectsUnboundedOrAmbiguousProfiles() throws Exception {
        String valid = validProfile();
        for (String invalid : List.of(
                valid.replace("profiles=com.example.app",
                        "profiles=com.example.app,com.example.app"),
                valid.replace("expires_at_millis=4102444800000", "expires_at_millis=0"),
                valid.replace("security_impact=reduces_app_security",
                        "security_impact=unknown"),
                valid.replace("owned_change_ids=123,456,789",
                        "owned_change_ids=123,123,789"),
                valid.replace("overrides=123:false,456:true", "overrides=999:false"),
                valid.replace("overrides=123:false,456:true", "overrides="),
                valid.replace("signer_sha256=" + SIGNER + "\n", ""),
                valid + "com.example.app.typo=true\n")) {
            assertRejected(invalid);
        }
    }

    private void assertRejected(String contents) throws Exception {
        try {
            CompatibilityProfileConfig.load(write(contents));
            fail("invalid profile was accepted");
        } catch (IllegalArgumentException expected) {
        }
    }

    private File write(String contents) throws Exception {
        File file = mTemp.newFile();
        Files.writeString(file.toPath(), contents, StandardCharsets.UTF_8);
        return file;
    }

    private static String validProfile() {
        return "profiles=com.example.app\n"
                + "com.example.app.signer_sha256=" + SIGNER + "\n"
                + "com.example.app.min_version_code=10\n"
                + "com.example.app.max_version_code=20\n"
                + "com.example.app.expires_at_millis=4102444800000\n"
                + "com.example.app.security_impact=reduces_app_security\n"
                + "com.example.app.reason=Compatibility test\n"
                + "com.example.app.retired=false\n"
                + "com.example.app.owned_change_ids=123,456,789\n"
                + "com.example.app.overrides=123:false,456:true\n";
    }
}
