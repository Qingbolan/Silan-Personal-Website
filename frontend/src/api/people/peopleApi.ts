import { formatLanguage, get } from '../utils';

export type PublicActorKind = 'user' | 'visitor';
export type PublicActorActivityKind = 'comment' | 'like';

export interface PublicActorActivity {
  id: string;
  kind: PublicActorActivityKind;
  entity_type: 'moment' | 'blog' | 'project' | 'episode' | string;
  entity_id: string;
  entity_slug?: string;
  entity_title?: string;
  entity_path?: string;
  content?: string;
  created_at: string;
}

export interface PublicActorProfile {
  actor_id: string;
  kind: PublicActorKind;
  display_name: string;
  avatar_url?: string;
  country_code?: string;
  region_name?: string;
  visitor_number?: string;
  joined_at?: string;
  activities: PublicActorActivity[];
}

export const fetchPublicActor = (
  actorId: string,
  language: 'en' | 'zh',
): Promise<PublicActorProfile> =>
  get(`/api/v1/people/${encodeURIComponent(actorId)}`, {
    lang: formatLanguage(language),
  });
