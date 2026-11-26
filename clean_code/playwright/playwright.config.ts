import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  workers: 1,
  timeout: 60000,
  use: {
    baseURL: 'http://127.0.0.1:8001',
    headless: true,
  },
  reporter: [['list']],
});
