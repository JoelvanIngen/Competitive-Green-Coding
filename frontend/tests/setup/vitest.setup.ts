import { expect, vi } from 'vitest';
import * as matchers from '@testing-library/jest-dom/matchers';    // types + runtime

//  Extend Vitest's expect with jest-dom matchers
expect.extend(matchers);

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
