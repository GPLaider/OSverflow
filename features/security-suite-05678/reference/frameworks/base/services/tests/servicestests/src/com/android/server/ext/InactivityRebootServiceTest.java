/*
 * SPDX-FileCopyrightText: 2026 The OSverflow Project
 * SPDX-License-Identifier: Apache-2.0
 */

package com.android.server.ext;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class InactivityRebootServiceTest {
    @Test
    public void policyOnlyArmsForLockedSecureAfuDevice() {
        int timeout = InactivityRebootService.ONE_HOUR_MS;

        assertFalse(InactivityRebootService.shouldArm(0, true, true, true));
        assertFalse(InactivityRebootService.shouldArm(timeout, false, true, true));
        assertFalse(InactivityRebootService.shouldArm(timeout, true, false, true));
        assertFalse(InactivityRebootService.shouldArm(timeout, true, true, false));
        assertTrue(InactivityRebootService.shouldArm(timeout, true, true, true));
    }

    @Test
    public void timeoutWhitelistRejectsUntrustedValues() {
        assertEquals(0, InactivityRebootService.normalizeTimeout(-1, true));
        assertEquals(0, InactivityRebootService.normalizeTimeout(1234, true));
        assertEquals(InactivityRebootService.ONE_HOUR_MS,
                InactivityRebootService.normalizeTimeout(
                        InactivityRebootService.ONE_HOUR_MS, false));
        assertEquals(0, InactivityRebootService.normalizeTimeout(
                InactivityRebootService.TEST_TIMEOUT_MS, false));
        assertEquals(InactivityRebootService.TEST_TIMEOUT_MS,
                InactivityRebootService.normalizeTimeout(
                        InactivityRebootService.TEST_TIMEOUT_MS, true));
    }
}
