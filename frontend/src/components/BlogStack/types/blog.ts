import { ReactNode } from 'react';

export interface BlogLiker {
  actor_id?: string;
  kind: 'user' | 'visitor' | string;
  country_code?: string;
  visitor_number?: string;
  avatar_url?: string;
  label?: string;
}

export interface BlogResource {
  kind: 'website' | 'github' | 'paper' | 'doi' | 'documentation' | 'other' | string;
  label: string;
  url: string;
}

export interface BlogContent {
  id: string;
  type: 'text' | 'image' | 'video' | 'quote' | 'code' | 'heading' | 'markdown';
  content: string;
  metadata?: Record<string, any>;
  children?: ReactNode;
  // Heading specific properties
  level?: number; // 1-6 for h1-h6
  // Image specific properties
  caption?: string;
  // Code specific properties
  language?: string;
  // Annotation specific properties
  annotation?: string;
}

export interface BlogData {
  id: string;
  title: string;
  titleZh?: string;
  slug?: string;
  author: string;
  publishDate: string;
  updatedAt?: string;
  readTime: string;
  category: string;
  tags: string[];
  content: BlogContent[];
  likes: number;
  isLikedByUser?: boolean;
  likers?: BlogLiker[];
  views: number;
  summary: string;
  summaryZh?: string;
  /** Locale-indexed source covers returned by the API. */
  featuredImageUrls?: Partial<Record<'en' | 'zh', string>>;
  /** Cover resolved for the language used to load this record. */
  featuredImageUrl?: string;
  coverImage?: string;
  projectName?: string;
  publicationVenue?: string;
  projectUrl?: string;
  externalResources?: BlogResource[];
  type?: 'article' | 'vlog' | 'tutorial' | 'podcast' | 'episode' | 'series';
  // Vlog specific fields
  videoUrl?: string;
  videoDuration?: string;
  videoThumbnail?: string;
  vlogCover?: string; // Vlog cover image for display
  // Series specific fields
  seriesId?: string;
  seriesSlug?: string;
  seriesTitle?: string;
  seriesTitleZh?: string;
  seriesDescription?: string;
  seriesDescriptionZh?: string;
  episodeNumber?: number;
  totalEpisodes?: number;
  seriesImage?: string;
}

export interface Comment {
  id: string;
  blog_post_id: string;
  parent_id?: string;
  author_name: string;
  author_avatar_url?: string;
  content: string;
  created_at: string;
  can_delete: boolean;
  replies?: Comment[];
}

export interface UserAnnotation {
  text: string;
  selectedText: string;
  startOffset: number;
  endOffset: number;
  fingerprint?: string;
}

export interface Section {
  id: string;
  title: string;
  level: number;
}

export interface SelectedText {
  text: string;
  contentId: string;
  startOffset: number;
  endOffset: number;
} 
