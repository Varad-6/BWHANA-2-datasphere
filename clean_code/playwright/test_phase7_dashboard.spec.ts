import { test, expect } from '@playwright/test';

test.describe('Phase 7: BW Morph Home -> S21 Sync -> Unified 8-Stage Studio E2E', () => {
  test('Home connection/sync -> Open BW Migration Studio box -> Single-row 8-stage workflow', async ({ page }) => {
    await page.goto('http://127.0.0.1:8501', { waitUntil: 'networkidle', timeout: 30000 });

    // 1. BW Morph Home Launchpad
    await expect(page.getByText('BW Morph Migration Suite')).toBeVisible({ timeout: 20000 });
    await expect(page.getByText('Step 1 — SAP S21 Connection Details & Live Sync')).toBeVisible();
    await expect(page.getByText('BW Migration Studio (Unified 8-Stage Workspace)')).toBeVisible();

    // Accept Details & Sync Live S21
    await page.getByRole('button', { name: '✓ Accept Details & Sync Live S21' }).click();
    await expect(page.getByText('Connection accepted!')).toBeVisible({ timeout: 30000 });

    // Click Launchpad Box -> Opens Unified BW Migration Studio
    await page.getByRole('button', { name: 'Open BW Migration Studio' }).click();

    // Verify Object Selector Controls & SINGLE-row 8-Stage Stepper (no duplicates!)
    await expect(page.getByText('BW Object Type')).toBeVisible({ timeout: 15000 });
    await expect(page.getByText('Search Objects')).toBeVisible();
    await expect(page.getByText('Select BW Object to Migrate')).toBeVisible();
    expect(await page.getByRole('button', { name: '1. Discover' }).count()).toBe(1);
    expect(await page.getByText('1. Discover').count()).toBe(1);

    // Stage 1 -> Stage 8 E2E
    await expect(page.getByText('Stage 1: Discover')).toBeVisible();
    await page.getByRole('button', { name: 'Next: 2. Analyze →' }).click();

    await expect(page.getByText('Stage 2: Analyze Structure & Properties')).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: 'Next: 3. Explore Lineage →' }).click();

    await expect(page.getByText('Stage 3: Explore Lineage')).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: 'Next: 4. Assess →' }).click();

    await expect(page.getByText('Stage 4: Assess Compatibility & Migration Approach')).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: 'Next: 5. Map →' }).click();

    await expect(page.getByText('Stage 5: Map to SAP Datasphere Targets')).toBeVisible({ timeout: 15000 });
    await page.getByLabel('Target Entity / View Name').fill('Z_UNIFIED_TEST_TARGET');
    await page.getByRole('button', { name: 'Next: 6. Transform →' }).click();

    await expect(page.getByText('Stage 6: Transform & Generate Datasphere Artifacts')).toBeVisible({ timeout: 15000 });
    await expect(page.getByText('Z_UNIFIED_TEST_TARGET').first()).toBeVisible();
    await page.getByRole('button', { name: 'Next: 7. Validate →' }).click();

    await expect(page.getByText('Stage 7: Validate Mappings, Schema & Dependencies')).toBeVisible({ timeout: 15000 });
    await expect(page.getByText('All Pre-Import Validation Gates PASSED!')).toBeVisible();
    await page.getByRole('button', { name: 'Next: 8. Deliver →' }).click();

    await expect(page.getByText('Stage 8: Deliver Artifacts & Track Progress')).toBeVisible({ timeout: 15000 });
    await expect(page.getByRole('button', { name: '🚀 Save to Output & Mark Validated' })).toBeVisible();
  });
});
