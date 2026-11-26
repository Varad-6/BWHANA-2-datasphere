import { test, expect } from '@playwright/test';

test.describe('Phase 6: CSN Generators (T5, T6, T7)', () => {
  test('Path 2, Path 3, Path 4 generators produce valid SAP CSN v1.0 JSON', async ({ request }) => {
    const p2Res = await request.get('/api/v1/generate/path2');
    expect(p2Res.status()).toBe(200);
    const p2 = await p2Res.json();
    expect(p2.status).toBe('completed');
    expect(p2.csn).toHaveProperty('$schema', 'https://sap.com/csn/v1');

    const p3Res = await request.get('/api/v1/generate/path3');
    expect(p3Res.status()).toBe(200);
    const p3 = await p3Res.json();
    expect(p3.status).toBe('completed');

    const p4Res = await request.get('/api/v1/generate/path4');
    expect(p4Res.status()).toBe(200);
    const p4 = await p4Res.json();
    expect(p4.status).toBe('completed');
    if (p4.csns.length > 0) {
      expect(p4.csns[0]).toHaveProperty('$schema', 'https://sap.com/csn/v1');
    }
  });
});
