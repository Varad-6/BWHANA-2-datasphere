import { test, expect } from '@playwright/test';

test.describe('Phase 4: Dependency Graph & Wave Planner (T1)', () => {
  test('GET /api/v1/graph/build produces topological waves and valid DOT', async ({ request }) => {
    const buildRes = await request.get('/api/v1/graph/build');
    expect(buildRes.status()).toBe(200);
    const body = await buildRes.json();
    expect(body.phase).toBe('T1');
    expect(body.status).toBe('completed');
    expect(body.nodes_count).toBeGreaterThan(0);
    expect(body.waves_count).toBeGreaterThan(0);
    expect(Array.isArray(body.waves)).toBe(true);

    const dotRes = await request.get('/api/v1/graph/dot');
    expect(dotRes.status()).toBe(200);
    const dotBody = await dotRes.json();
    expect(dotBody.dot).toContain('digraph BW_Migration_Graph');
  });
});
