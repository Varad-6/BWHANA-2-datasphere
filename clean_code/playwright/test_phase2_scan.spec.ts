import { test, expect } from '@playwright/test';

test.describe('Phase 2: SAP S21 Live OData Scan (T0)', () => {
  test('GET /api/v1/scan/start?mode=live extracts live objects from S21 without mutation', async ({ request }) => {
    const startRes = await request.get('/api/v1/scan/start?mode=live&limit=25');
    expect(startRes.status()).toBe(200);

    const body = await startRes.json();
    expect(body.phase).toBe('T0');
    expect(body.status).toBe('completed');
    expect(body.mode).toBe('live');
    expect(body.sap_sid).toBe('S21');
    expect(body.total_scanned).toBeGreaterThan(0);

    const statusRes = await request.get('/api/v1/scan/status');
    expect(statusRes.status()).toBe(200);
    const statusBody = await statusRes.json();
    expect(statusBody.status).toBe('completed');
    expect(statusBody.total_objects).toBeGreaterThan(0);

    const objsRes = await request.get('/api/v1/scan/objects?page=1&limit=10');
    expect(objsRes.status()).toBe(200);
    const objsBody = await objsRes.json();
    expect(objsBody.items.length).toBeGreaterThan(0);
  });
});
