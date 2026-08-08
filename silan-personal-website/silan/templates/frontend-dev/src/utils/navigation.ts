/**
 * Canonical internal links use trailing slashes for route-like URLs. That
 * matches the prerendered directory layout and avoids crawler-visible
 * `/blog -> /blog/` redirects from generated navigation.
 */
export const canonicalInternalPath = (pathname: string): string => {
  const [path, suffix = ''] = pathname.split(/(?=[?#])/, 2);
  if (!path || path === '/') return `/${suffix}`;
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${normalized.endsWith('/') ? normalized : `${normalized}/`}${suffix}`;
};

/**
 * Resolve a concrete URL to its primary information-architecture route.
 * Episodes are authored as their own content type, but visitors discover and
 * navigate them through Writing/Blog.
 */
export const primaryNavigationPath = (pathname: string): string =>
  pathname.startsWith('/episodes/')
    ? '/blog'
    : pathname === '/ideas' || pathname.startsWith('/ideas/')
      ? '/moments'
      : pathname;

export const isNavigationPathActive = (pathname: string, routePath: string): boolean => {
  const effectivePath = primaryNavigationPath(pathname);
  return routePath === '/'
    ? effectivePath === '/'
    : effectivePath === routePath || effectivePath.startsWith(`${routePath}/`);
};
