// -----------------------------------------------------------------------------
// Shared types for the user profile page
//
// This file defines TypeScript interfaces and types used by the user profile page
// and its components, such as ProfileData, RecentItem, and LanguageStat. These types
// ensure type safety and consistency across the profile UI.
// -----------------------------------------------------------------------------

export interface LanguageStat {
  language: string;
  solved: number;
}

export type RecentItem = {
  id: string;
  title: string;
  when: string;        // e.g. "2 hours ago"
};

export interface ProfileData {
  username: string;
  avatarUrl: string;
  rank?: number;
  greenScore?: number;

  solved: {
    total: number;
    easy: number;
    medium: number;
    hard: number;
  };

  recentSubmissions: RecentItem[];
  recentDiscussions?: RecentItem[];
  languageStats: LanguageStat[];
}
