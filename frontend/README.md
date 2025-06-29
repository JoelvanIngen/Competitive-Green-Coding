# Project Setup Instructions

## Prerequisites

- **Node.js** (download the newest version from [nodejs.org](https://nodejs.org/))
- ***For VS Code users:*** *install the "Tailwind CSS IntelliSense" extension*

## First Time Setup

1. Navigate to the `frontend` folder
2. Install dependencies: `npm install`. If npm complains about dependencies, just use `npm install --force`. I checked the dependencies already.
3. Start development server: `npm run dev`
4. Open [http://localhost:3000](http://localhost:3000/) in your browser

## Daily Development

- Start server: `npm run dev`
- Stop server: `Ctrl + C`

You can start editing the home page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

# Important links

- Shadcn component library: https://ui.shadcn.com/

## Common Commands

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Check code quality

## Troubleshooting

- If you see dependency warnings, use: `npm install --force`
- If the server won't start, try: `rm -rf node_modules && npm install`
- Make sure you're using Node.js 18+: `node --version`

## Project Structure

```
src/
├── app/             # Pages and routing
   ├── layout.tsx    # Layout, consistent on every page (like a navbar that is the same on every page)   
   ├── page.tsx      # Homepage
   ├── login/        # New route to www.website.com/login
        ├── page.tsx # the page to display at www.website.com/login
├── components/      # Reusable components
└── lib/             # Utilities and configurations
```

## Learn More
To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.
