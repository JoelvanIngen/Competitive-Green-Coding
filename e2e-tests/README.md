# E2E Testing with Playwright

Quick guide for teammates to get started with end-to-end testing using Playwright.

## Setup

1. Install dependencies:
```bash
npm init -y
bashnpm install @playwright/test
npx playwright install
```

2. Make sure your main application is running on `http://localhost:3000` before running tests

## Configuration file (`playwright.config.js`)

Some info about settings:

- **Headless mode**: Set `headless: true` to run tests without opening browser windows, or `headless: false` to see the browser in action
- **Browser support**: Currently configured for Chromium only. You can add Firefox by adding another project:
  ```js
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } }
  ]
  ```
- **Timeout**: Set to 30 seconds (`timeout: 30000`).

## Running Tests

```bash
# Run all tests
npx playwright test

# Run tests with visible browser
npx playwright test --headed

# Run specific test file
npx playwright test auth.spec.js

# Run tests in debug mode
npx playwright test --debug
```

## Writing Tests

Tests are located in the `./tests` directory.
See auth.spec.js for basic test structure

Other useful functions:
```js
// Add assertions
await expect(page).toHaveURL('expected-url');
```

### Common Playwright Actions

- `page.goto(url)` - Navigate to URL
- `page.click('selector')` - Click element
- `page.fill('input[name="field"]', 'value')` - Fill form fields
- `page.waitForSelector('selector')` - Wait for element to appear
- `expect(page).toHaveURL()` - Assert current URL
- `expect(page.locator('selector')).toBeVisible()` - Assert element visibility


## Debugging Tips

- Screenshots should be saved in `test-results/`, not working currently
- Add `await page.pause()` to pause execution and inspect the page