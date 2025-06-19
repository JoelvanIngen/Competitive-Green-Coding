import '@testing-library/jest-dom/extend-expect';

/* ---------------------------------------------------------------------------
   Global fetch mock that each test can override.
--------------------------------------------------------------------------- */
import { vi } from 'vitest';

beforeAll(() => {
  if (!global.fetch) {
    // Provide a default implementation so tests don’t crash if they forget.
    global.fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) }) as any;
  }
});
