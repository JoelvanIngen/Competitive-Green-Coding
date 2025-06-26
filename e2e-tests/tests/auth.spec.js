import { test } from '@playwright/test';

// Two ways of navigating to Log in,
// just remove first line if you want standalone function
['Log in', 'Start Here'].forEach(entryPoint => {
  test(`${entryPoint} button: user can register and login`, async ({ page }) => {
    await page.goto('http://localhost:3000/');
    await page.click(`text=${entryPoint}`);
    await page.click('text=Sign up');
    await page.fill('input[name="username"]', 'barungz');
    await page.fill('input[name="email"]', 'barungzboy@gmail.com');
    await page.fill('input[name="password"]', 'kaas1234');
    await page.fill('input[name="confirm-password"]', 'kaas1234');
    await page.click('text=Register');

    // not sure if this line should be needed
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="username"]', 'barungz');
    await page.fill('input[name="password"]', 'kaas1234');
    await page.click('text=Login');
  });
});