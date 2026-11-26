import { test, expect } from '@playwright/test';

test.describe('Phase 5: Object Classifier & Complexity Scorer (T2)', () => {
  test('GET /api/v1/classify/run scores all objects 1-5 across Paths 1-7', async ({ request }) => {
    const runRes = await request.get('/api/v1/classify/run');
    expect(runRes.status()).toBe(200);
    const body = await runRes.json();
    expect(body.phase).toBe('T2');
    expect(body.status).toBe('completed');
    expect(body.total_classified).toBeGreaterThan(0);
    expect(body.avg_complexity).toBeGreaterThanOrEqual(1);
    expect(body.avg_complexity).toBeLessThanOrEqual(5);

    const summaryRes = await request.get('/api/v1/classify/summary');
    expect(summaryRes.status()).toBe(200);
    const summary = await summaryRes.json();
    expect(summary.total_objects).toBeGreaterThan(0);
  });
});
