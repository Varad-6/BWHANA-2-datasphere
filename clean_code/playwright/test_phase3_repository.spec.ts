import { test, expect } from '@playwright/test';

test.describe('Phase 3: Shared Metadata Repository API', () => {
  test('GET /api/v1/repository/stats and paginated objects work', async ({ request }) => {
    const statsRes = await request.get('/api/v1/repository/stats');
    expect(statsRes.status()).toBe(200);
    const stats = await statsRes.json();
    expect(stats.total_objects).toBeGreaterThan(0);
    expect(stats).toHaveProperty('by_path');
    expect(stats).toHaveProperty('by_type');

    const objsRes = await request.get('/api/v1/repository/objects?page=1&limit=5');
    expect(objsRes.status()).toBe(200);
    const objs = await objsRes.json();
    expect(objs.items.length).toBeGreaterThan(0);

    const firstTechName = objs.items[0].tech_name;
    const singleRes = await request.get(`/api/v1/repository/object/${encodeURIComponent(firstTechName)}`);
    expect(singleRes.status()).toBe(200);
    const single = await singleRes.json();
    expect(single.tech_name).toBe(firstTechName);

    const phasesRes = await request.get('/api/v1/repository/phases');
    expect(phasesRes.status()).toBe(200);
    const phases = await phasesRes.json();
    expect(phases.phases.length).toBe(6);
  });
});
