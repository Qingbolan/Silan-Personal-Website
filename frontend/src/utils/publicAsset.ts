const trimTrailingSlash = (value: string): string => value.replace(/\/+$/, '');

export const PUBLIC_ORIGIN = trimTrailingSlash(import.meta.env.VITE_PUBLIC_ORIGIN || 'https://silan.tech');
export const CANONICAL_ORIGIN = trimTrailingSlash(import.meta.env.VITE_CANONICAL_ORIGIN || PUBLIC_ORIGIN);

export const PUBLIC_BASE = `/${(import.meta.env.BASE_URL || '/').replace(/^\/+|\/+$/g, '')}`;
export const CANONICAL_BASE = `/${(import.meta.env.VITE_CANONICAL_BASE || PUBLIC_BASE).replace(/^\/+|\/+$/g, '')}`;

const normalizedBase = PUBLIC_BASE === '/' ? '' : PUBLIC_BASE;
const normalizedCanonicalBase = CANONICAL_BASE === '/' ? '' : CANONICAL_BASE;

export const siteUrl = (path: string = '/'): string => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  if (
    normalizedCanonicalBase &&
    (normalizedPath === normalizedCanonicalBase || normalizedPath.startsWith(`${normalizedCanonicalBase}/`))
  ) {
    return `${CANONICAL_ORIGIN}${normalizedPath}`;
  }
  if (normalizedPath === '/') return `${CANONICAL_ORIGIN}${normalizedCanonicalBase || '/'}`;
  return `${CANONICAL_ORIGIN}${normalizedCanonicalBase}${normalizedPath}`;
};

export const publicAssetUrl = (path: string): string => {
  if (/^(https?:)?\/\//i.test(path) || path.startsWith('data:') || path.startsWith('blob:')) {
    return path;
  }
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  if (normalizedBase && (normalizedPath === normalizedBase || normalizedPath.startsWith(`${normalizedBase}/`))) {
    return normalizedPath;
  }
  return `${normalizedBase}${normalizedPath}` || '/';
};
