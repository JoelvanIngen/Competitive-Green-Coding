import { expect, vi, beforeAll } from 'vitest';
import '@testing-library/jest-dom/vitest';    // Vitest-specific setup

/* ---------------------------------------------------------------------------
   Global fetch mock that each test can override.
--------------------------------------------------------------------------- */
beforeAll(() => {
  if (!global.fetch) {
    global.fetch = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({}) }) as unknown as typeof fetch;
  }
});
