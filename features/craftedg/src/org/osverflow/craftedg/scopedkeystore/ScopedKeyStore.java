/*
 * SPDX-FileCopyrightText: 2026 GPLaider
 * SPDX-License-Identifier: Apache-2.0
 */
package org.osverflow.craftedg.scopedkeystore;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.security.Key;
import java.security.KeyStore;
import java.security.KeyStoreException;
import java.security.KeyStoreSpi;
import java.security.NoSuchAlgorithmException;
import java.security.Provider;
import java.security.ProviderException;
import java.security.Security;
import java.security.UnrecoverableEntryException;
import java.security.UnrecoverableKeyException;
import java.security.cert.Certificate;
import java.security.cert.CertificateException;
import java.util.Date;
import java.util.Enumeration;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicReference;

/** Process-local, stock-preserving AndroidKeyStore provider indirection. */
public final class ScopedKeyStore {
    public enum VerifiedPackage {
        GMS_CORE,
        PLAY_STORE,
        OTHER
    }

    private static final String GMS_CORE_PROCESS = "com.google.android.gms.unstable";
    private static final String PLAY_STORE_PROCESS = "com.android.vending";
    private static final Object INSTALL_LOCK = new Object();

    private ScopedKeyStore() {}

    /**
     * {@code verifiedPackage} must come from a framework-verified package identity, never from
     * app-supplied package text. {@code compatEnabled} must already exclude privileged GMS.
     */
    public static boolean isTarget(
            boolean compatEnabled, VerifiedPackage verifiedPackage, String processName) {
        if (!compatEnabled || verifiedPackage == null || processName == null) {
            return false;
        }
        return switch (verifiedPackage) {
            case GMS_CORE -> GMS_CORE_PROCESS.equals(processName);
            case PLAY_STORE -> PLAY_STORE_PROCESS.equals(processName);
            case OTHER -> false;
        };
    }

    /**
     * Replaces a stock provider only inside the current JVM. A denied target returns before
     * inspecting or mutating provider state. Any target-side setup failure preserves or restores
     * the stock provider and reports failure.
     */
    public static boolean installAndroidKeyStoreIfAllowed(
            boolean compatEnabled,
            VerifiedPackage verifiedPackage,
            String processName,
            Provider stockProvider,
            KeyStoreSpi stockSpi) {
        if (!isTarget(compatEnabled, verifiedPackage, processName)) {
            return false;
        }

        Objects.requireNonNull(stockProvider, "stockProvider");
        Objects.requireNonNull(stockSpi, "stockSpi");

        synchronized (INSTALL_LOCK) {
            String providerName = stockProvider.getName();
            if (Security.getProvider(providerName) != stockProvider) {
                return false;
            }
            if (stockProvider.getService("KeyStore", "AndroidKeyStore") == null) {
                throw new ProviderException("Stock provider has no AndroidKeyStore service");
            }

            int position = providerPosition(stockProvider);
            if (position < 1) {
                return false;
            }

            Provider scopedProvider = new ScopedProvider(stockProvider);
            DelegatingSpi.bind(stockSpi);
            try {
                Security.removeProvider(providerName);
                if (Security.insertProviderAt(scopedProvider, position) < 1) {
                    throw new ProviderException("Unable to install scoped provider");
                }
                return true;
            } catch (RuntimeException failure) {
                Provider current = Security.getProvider(providerName);
                if (current instanceof ScopedProvider) {
                    Security.removeProvider(providerName);
                }
                if (Security.getProvider(providerName) == null) {
                    Security.insertProviderAt(stockProvider, position);
                }
                DelegatingSpi.unbind(stockSpi);
                if (Security.getProvider(providerName) != stockProvider) {
                    throw new ProviderException("Stock provider restoration failed", failure);
                }
                throw failure;
            }
        }
    }

    private static int providerPosition(Provider provider) {
        Provider[] providers = Security.getProviders();
        for (int i = 0; i < providers.length; i++) {
            if (providers[i] == provider) {
                return i + 1;
            }
        }
        return -1;
    }

    private static final class ScopedProvider extends Provider {
        private static final long serialVersionUID = 1L;

        @SuppressWarnings("deprecation")
        ScopedProvider(Provider stockProvider) {
            super(
                    stockProvider.getName(),
                    stockProvider.getVersion(),
                    "CraftedG scoped wrapper for " + stockProvider.getInfo());
            putAll(stockProvider);
            put("KeyStore.AndroidKeyStore", DelegatingSpi.class.getName());
        }
    }

    /** Public for JCA construction; callers should use the installer above. */
    public static final class DelegatingSpi extends KeyStoreSpi {
        private static final AtomicReference<KeyStoreSpi> STOCK = new AtomicReference<>();

        public DelegatingSpi() {}

        private static void bind(KeyStoreSpi stockSpi) {
            if (!STOCK.compareAndSet(null, stockSpi)) {
                throw new ProviderException("AndroidKeyStore delegate is already bound");
            }
        }

        private static void unbind(KeyStoreSpi stockSpi) {
            STOCK.compareAndSet(stockSpi, null);
        }

        private static KeyStoreSpi stock() {
            KeyStoreSpi result = STOCK.get();
            if (result == null) {
                throw new ProviderException("AndroidKeyStore delegate is not bound");
            }
            return result;
        }

        @Override
        public Key engineGetKey(String alias, char[] password)
                throws NoSuchAlgorithmException, UnrecoverableKeyException {
            return stock().engineGetKey(alias, password);
        }

        @Override
        public Certificate[] engineGetCertificateChain(String alias) {
            return stock().engineGetCertificateChain(alias);
        }

        @Override
        public Certificate engineGetCertificate(String alias) {
            return stock().engineGetCertificate(alias);
        }

        @Override
        public Date engineGetCreationDate(String alias) {
            return stock().engineGetCreationDate(alias);
        }

        @Override
        public void engineSetKeyEntry(
                String alias, Key key, char[] password, Certificate[] chain)
                throws KeyStoreException {
            stock().engineSetKeyEntry(alias, key, password, chain);
        }

        @Override
        public void engineSetKeyEntry(String alias, byte[] key, Certificate[] chain)
                throws KeyStoreException {
            stock().engineSetKeyEntry(alias, key, chain);
        }

        @Override
        public void engineSetCertificateEntry(String alias, Certificate cert)
                throws KeyStoreException {
            stock().engineSetCertificateEntry(alias, cert);
        }

        @Override
        public void engineDeleteEntry(String alias) throws KeyStoreException {
            stock().engineDeleteEntry(alias);
        }

        @Override
        public Enumeration<String> engineAliases() {
            return stock().engineAliases();
        }

        @Override
        public boolean engineContainsAlias(String alias) {
            return stock().engineContainsAlias(alias);
        }

        @Override
        public int engineSize() {
            return stock().engineSize();
        }

        @Override
        public boolean engineIsKeyEntry(String alias) {
            return stock().engineIsKeyEntry(alias);
        }

        @Override
        public boolean engineIsCertificateEntry(String alias) {
            return stock().engineIsCertificateEntry(alias);
        }

        @Override
        public String engineGetCertificateAlias(Certificate cert) {
            return stock().engineGetCertificateAlias(cert);
        }

        @Override
        public void engineStore(OutputStream stream, char[] password)
                throws IOException, NoSuchAlgorithmException, CertificateException {
            stock().engineStore(stream, password);
        }

        @Override
        public void engineStore(KeyStore.LoadStoreParameter param)
                throws IOException, NoSuchAlgorithmException, CertificateException {
            stock().engineStore(param);
        }

        @Override
        public void engineLoad(InputStream stream, char[] password)
                throws IOException, NoSuchAlgorithmException, CertificateException {
            stock().engineLoad(stream, password);
        }

        @Override
        public void engineLoad(KeyStore.LoadStoreParameter param)
                throws IOException, NoSuchAlgorithmException, CertificateException {
            stock().engineLoad(param);
        }

        @Override
        public KeyStore.Entry engineGetEntry(
                String alias, KeyStore.ProtectionParameter protectionParameter)
                throws KeyStoreException, NoSuchAlgorithmException, UnrecoverableEntryException {
            return stock().engineGetEntry(alias, protectionParameter);
        }

        @Override
        public void engineSetEntry(
                String alias,
                KeyStore.Entry entry,
                KeyStore.ProtectionParameter protectionParameter)
                throws KeyStoreException {
            stock().engineSetEntry(alias, entry, protectionParameter);
        }

        @Override
        public boolean engineEntryInstanceOf(
                String alias, Class<? extends KeyStore.Entry> entryClass) {
            return stock().engineEntryInstanceOf(alias, entryClass);
        }

        @Override
        public boolean engineProbe(InputStream stream) throws IOException {
            return stock().engineProbe(stream);
        }
    }
}
