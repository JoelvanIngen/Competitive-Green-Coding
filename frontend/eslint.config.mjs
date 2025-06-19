import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const config = [
  // ⬅️  keep the standard Next.js / TypeScript rules
  ...compat.extends("next/core-web-vitals", "next/typescript"),

  // -----------------------------------------------------------------
  // Override ONLY for test files
  // -----------------------------------------------------------------
  {
    files: ["**/*.test.{ts,tsx}", "tests/**/*.{ts,tsx}"],
    rules: {
      "@typescript-eslint/no-explicit-any":   "off",
      "@typescript-eslint/no-require-imports":"off",
      "@next/next/no-img-element":            "off",
      "jsx-a11y/alt-text":                    "off",
    },
  },
];

// ✅ Assign before exporting
export default config;
