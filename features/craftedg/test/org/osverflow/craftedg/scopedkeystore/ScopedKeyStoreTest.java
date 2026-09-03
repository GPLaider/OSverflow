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
import java.security.PublicKey;
import java.security.Security;
import java.security.UnrecoverableKeyException;
import java.security.cert.Certificate;
import java.security.cert.CertificateException;
import java.util.Arrays;
import java.util.Collections;
import java.util.Date;
import java.util.Enumeration;

public final class ScopedKeyStoreTest {
    private static final String PROVIDER_NAME = "CraftedG-stock-test";

    public static void main(String[] args) throws Exception {
        policyIsDefaultDenyAndExact();
        nonTargetLeavesProviderRegistryUntouched();
        System.out.println("CRAFTEDG_CHECKS_OK");
    }

    private static void policyIsDefaultDenyAndExact() {
        check(!ScopedKeyStore.isTarget(
                false,
                ScopedKeyStore.VerifiedPackage.GMS_CORE,
                "com.google.android.gms.unstable"));
        check(!ScopedKeyStore.isTarget(
                true, ScopedKeyStore.VerifiedPackage.GMS_CORE, null));
        check(!ScopedKeyStore.isTarget(
                true,
                ScopedKeyStore.VerifiedPackage.OTHER,
                "com.google.android.gms.unstable"));
        check(!ScopedKeyStore.isTarget(
                true,
                ScopedKeyStore.VerifiedPackage.GMS_CORE,
                "prefix.com.google.android.gms.unstable"));
        check(!ScopedKeyStore.isTarget(
                true,
                ScopedKeyStore.VerifiedPackage.GMS_CORE,
                "com.google.android.gms"));
        check(!ScopedKeyStore.isTarget(
                true,
                ScopedKeyStore.VerifiedPackage.PLAY_STORE,
                "com.google.android.gms.unstable"));
        check(ScopedKeyStore.isTarget(
                true,
                ScopedKeyStore.VerifiedPackage.GMS_CORE,
                "com.google.android.gms.unstable"));
        check(ScopedKeyStore.isTarget(
                true,
                ScopedKeyStore.VerifiedPackage.PLAY_STORE,
                "com.android.vending"));
    }

    private static void nonTargetLeavesProviderRegistryUntouched() throws Exception {
        Provider stockProvider = new StockProvider();
        check(Security.addProvider(stockProvider) > 0);
        try {
            Provider[] before = Security.getProviders();
            check(!ScopedKeyStore.installAndroidKeyStoreIfAllowed(
                    true,
                    ScopedKeyStore.VerifiedPackage.OTHER,
                    "com.google.android.gms.unstable",
                    null,
                    null));
            check(Arrays.equals(before, Security.getProviders()));
            check(Security.getProvider(PROVIDER_NAME) == stockProvider);

            expectThrows(
                    NullPointerException.class,
                    () -> ScopedKeyStore.installAndroidKeyStoreIfAllowed(
                            true,
                            ScopedKeyStore.VerifiedPackage.GMS_CORE,
                            "com.google.android.gms.unstable",
                            stockProvider,
                            null));
            check(Arrays.equals(before, Security.getProviders()));

            KeyStore stock = KeyStore.getInstance("AndroidKeyStore", stockProvider);
            stock.load(null, null);
            Certificate stockCertificate = stock.getCertificate("alpha");
            int stockSize = stock.size();

            StockSpi delegate = new StockSpi();
            check(ScopedKeyStore.installAndroidKeyStoreIfAllowed(
                    true,
                    ScopedKeyStore.VerifiedPackage.GMS_CORE,
                    "com.google.android.gms.unstable",
                    stockProvider,
                    delegate));

            Provider scopedProvider = Security.getProvider(PROVIDER_NAME);
            check(scopedProvider != null && scopedProvider != stockProvider);
            KeyStore scoped = KeyStore.getInstance("AndroidKeyStore", scopedProvider);
            scoped.load(null, null);
            check(scoped.size() == stockSize);
            check(scoped.getCertificate("alpha") == stockCertificate);
            check(scoped.getCertificateChain("alpha")[0] == stockCertificate);
            expectMessage(UnrecoverableKeyException.class, "stock failure",
                    () -> scoped.getKey("fail", null));
            scoped.deleteEntry("alpha");
            check(delegate.deleted);
        } finally {
            Security.removeProvider(PROVIDER_NAME);
        }
    }

    private static void check(boolean condition) {
        if (!condition) {
            throw new AssertionError();
        }
    }

    private static void expectThrows(
            Class<? extends Throwable> expected, ThrowingRunnable runnable) {
        expectMessage(expected, null, runnable);
    }

    private static void expectMessage(
            Class<? extends Throwable> expected, String message, ThrowingRunnable runnable) {
        try {
            runnable.run();
        } catch (Throwable actual) {
            check(expected.isInstance(actual));
            if (message != null) {
                check(message.equals(actual.getMessage()));
            }
            return;
        }
        throw new AssertionError("Expected " + expected.getName());
    }

    @FunctionalInterface
    private interface ThrowingRunnable {
        void run() throws Exception;
    }

    public static final class StockProvider extends Provider {
        private static final long serialVersionUID = 1L;

        @SuppressWarnings("deprecation")
        StockProvider() {
            super(PROVIDER_NAME, 1.0, "stock test provider");
            put("KeyStore.AndroidKeyStore", StockSpi.class.getName());
        }
    }

    public static final class StockSpi extends KeyStoreSpi {
        static final Certificate CERTIFICATE = new TestCertificate();
        boolean deleted;

        public StockSpi() {}

        @Override
        public Key engineGetKey(String alias, char[] password)
                throws UnrecoverableKeyException {
            if ("fail".equals(alias)) {
                throw new UnrecoverableKeyException("stock failure");
            }
            return null;
        }

        @Override
        public Certificate[] engineGetCertificateChain(String alias) {
            return new Certificate[] {CERTIFICATE};
        }

        @Override
        public Certificate engineGetCertificate(String alias) {
            return CERTIFICATE;
        }

        @Override
        public Date engineGetCreationDate(String alias) {
            return new Date(1L);
        }

        @Override
        public void engineSetKeyEntry(
                String alias, Key key, char[] password, Certificate[] chain) {}

        @Override
        public void engineSetKeyEntry(String alias, byte[] key, Certificate[] chain) {}

        @Override
        public void engineSetCertificateEntry(String alias, Certificate cert) {}

        @Override
        public void engineDeleteEntry(String alias) {
            deleted = true;
        }

        @Override
        public Enumeration<String> engineAliases() {
            return Collections.enumeration(Collections.singleton("alpha"));
        }

        @Override
        public boolean engineContainsAlias(String alias) {
            return "alpha".equals(alias);
        }

        @Override
        public int engineSize() {
            return 1;
        }

        @Override
        public boolean engineIsKeyEntry(String alias) {
            return "alpha".equals(alias);
        }

        @Override
        public boolean engineIsCertificateEntry(String alias) {
            return false;
        }

        @Override
        public String engineGetCertificateAlias(Certificate cert) {
            return cert == CERTIFICATE ? "alpha" : null;
        }

        @Override
        public void engineStore(OutputStream stream, char[] password)
                throws IOException, NoSuchAlgorithmException, CertificateException {}

        @Override
        public void engineLoad(InputStream stream, char[] password)
                throws IOException, NoSuchAlgorithmException, CertificateException {}
    }

    private static final class TestCertificate extends Certificate {
        private static final long serialVersionUID = 1L;

        TestCertificate() {
            super("CraftedG-test");
        }

        @Override
        public byte[] getEncoded() {
            return new byte[] {1};
        }

        @Override
        public void verify(PublicKey key) {}

        @Override
        public void verify(PublicKey key, String sigProvider) {}

        @Override
        public String toString() {
            return "CraftedG test certificate";
        }

        @Override
        public PublicKey getPublicKey() {
            return null;
        }
    }
}
