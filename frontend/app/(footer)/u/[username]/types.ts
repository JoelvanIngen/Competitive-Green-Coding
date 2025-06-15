// -----------------------------------------------------------------------------
// Shared profile-page types
// -----------------------------------------------------------------------------

export interface LanguageStat {
  language: string;
  solved: number;
}

export type RecentItem = {
  id: string;
  title: string;
  when: string;        // e.g. “2 hours ago”
};

export interface ProfileData {
  username: string;
  avatarUrl: string;
  rank: number;
  greenScore: number;

  solved: {
    total: number;
    easy: number;
    medium: number;
    hard: number;
  };

  recentSubmissions: RecentItem[];
  recentDiscussions: RecentItem[];
  languageStats: LanguageStat[];
}
