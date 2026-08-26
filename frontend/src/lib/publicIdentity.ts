const INTERNAL_GUEST_NAME = /^guest-id<[^>]+>$/i;

export const isInternalGuestName = (value: string | undefined): boolean =>
  Boolean(value?.trim() && INTERNAL_GUEST_NAME.test(value.trim()));

/**
 * Runtime guest identifiers are useful for ownership and moderation, but are
 * not public-facing names. All discussion surfaces project them into the same
 * compact visitor label while keeping the stored identity unchanged.
 */
export const publicDisplayName = (
  value: string | undefined,
  visitorNumber: string | undefined,
  language: 'en' | 'zh',
): string => {
  const name = value?.trim() ?? '';
  if (name && !isInternalGuestName(name)) return name;
  const visitor = language === 'zh' ? '访客' : 'Guest';
  return visitorNumber ? `${visitor} ${visitorNumber}` : visitor;
};
