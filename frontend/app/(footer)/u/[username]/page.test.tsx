// -----------------------------------------------------------------------------
// page.test.tsx
//
// Vitest + React-Testing-Library tests for ProfilePage:
// verifies header, solved-ring and tab rendering with mocked UI components.
// -----------------------------------------------------------------------------

import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { vi } from 'vitest';
import type { ProfileData } from './types';
import ProfilePage from './page';


// ───── Mock shadcn / Radix ────────────────────────────────────────────
vi.mock('@/components/ui/avatar', () => ({
  Avatar:        ({ children }: { children: React.ReactNode }) => <div data-testid="avatar">{children}</div>,
  AvatarImage:   (props: React.ImgHTMLAttributes<HTMLImageElement>) => <img data-testid="avatar-img" {...props} alt="" />,
  AvatarFallback:({ children }: { children: React.ReactNode }) => <span>{children}</span>,
}));

vi.mock('@/components/ui/card', () => ({
  Card:        ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CardHeader:  ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CardContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CardTitle:   ({ children }: { children: React.ReactNode }) => <h2>{children}</h2>,
}));

vi.mock('@/components/ui/tabs', () => ({
  Tabs:        ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  TabsList:    ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  TabsTrigger: ({ children }: { children: React.ReactNode }) => (
    <button role="tab">{children}</button>
  ),
  TabsContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));
// ───────────────────────────────────────────────────────────────────────

// ---------- Fixture ----------
const fixture: ProfileData = {
  username: 'alice',
  avatarUrl: '/avatars/a.png',
  rank: 4242,
  greenScore: 371,
  solved: { total: 120, easy: 80, medium: 30, hard: 10 },
  recentSubmissions: [
    { id: '1', title: 'Two Sum', when: '2 h ago' },
    { id: '2', title: 'Reverse Linked List', when: '1 d ago' },
  ],
  recentDiscussions: [],
  languageStats: [
    { language: 'TypeScript', solved: 70 },
    { language: 'Rust', solved: 30 },
    { language: 'Go', solved: 20 },
  ],
};

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    json: async () => fixture,
  }));
  process.env.NEXT_PUBLIC_SITE_URL = 'http://localhost:3000';
});

it('renders profile header, solved ring and tabs', async () => {
  let result: React.ReactElement | null = null;

  await act(async () => {
    result = await ProfilePage({ params: { username: 'alice' } });
  });

  render(result!);

  expect(await screen.findByText('alice')).toBeInTheDocument();
  expect(screen.getByText(/\/\s*120\s*solved/i)).toBeInTheDocument();
  expect(screen.getByRole('tab', { name: /recent\s+submissions/i })).toBeVisible();
});
