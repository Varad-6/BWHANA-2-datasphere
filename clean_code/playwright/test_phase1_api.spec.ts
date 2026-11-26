import { test, expect } from '@playwright/test';

test.describe('Phase 1: FastAPI Foundation & Health Check', () => {
  test('GET /api/v1/health returns 200 with valid schema and SAP S21 reachability', async ({ request }) => {
    const response = await request.get('/api/v1/health');
    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body).toHaveProperty('status', 'ok');
    expect(body).toHaveProperty('service', 'BW Morph Migration Accelerator API');
    expect(body).toHaveProperty('version', '1.0.0');
    expect(body).toHaveProperty('db_connected', true);
    expect(body).toHaveProperty('sap_host', '192.168.1.55');
    expect(body).toHaveProperty('sap_sid', 'S21');
    expect(body).toHaveProperty('sap_read_only', true);
    expect(body).toHaveProperty('sap_reachable', true);
    expect(typeof body.timestamp).toBe('string');
  });

  test('GET /openapi.json exposes OpenAPI specification', async ({ request }) => {
    const response = await request.get('/openapi.json');
    expect(response.status()).toBe(200);
    const schema = await response.json();
    expect(schema.info.title).toBe('BW Morph Migration Accelerator API');
    expect(schema.paths).toHaveProperty('/api/v1/health');
  });
});
