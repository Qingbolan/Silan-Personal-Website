import React from 'react';
import {
  Cube,
  EnvelopeSimple,
  FacebookLogo,
  GithubLogo,
  Globe,
  GraduationCap,
  InstagramLogo,
  LinkedinLogo,
  TelegramLogo,
  XLogo,
  YoutubeLogo,
} from '@phosphor-icons/react';

// Monochrome Xiaohongshu wordmark, normalized to the same 24px canvas as
// the rest of this module's brand glyphs. Source: Simple Icons' Xiaohongshu SVG.
const XIAOHONGSHU_ICON_PATH = 'M22.405 9.879c.002.016.01.02.07.019h.725a.797.797 0 0 0 .78-.972.794.794 0 0 0-.884-.618.795.795 0 0 0-.692.794c0 .101-.002.666.001.777zm-11.509 4.808c-.203.001-1.353.004-1.685.003a2.528 2.528 0 0 1-.766-.126.025.025 0 0 0-.03.014L7.7 16.127a.025.025 0 0 0 .01.032c.111.06.336.124.495.124.66.01 1.32.002 1.981 0 .01 0 .02-.006.023-.015l.712-1.545a.025.025 0 0 0-.024-.036zM.477 9.91c-.071 0-.076.002-.076.01a.834.834 0 0 0-.01.08c-.027.397-.038.495-.234 3.06-.012.24-.034.389-.135.607-.026.057-.033.042.003.112.046.092.681 1.523.787 1.74.008.015.011.02.017.02.008 0 .033-.026.047-.044.147-.187.268-.391.371-.606.306-.635.44-1.325.486-1.706.014-.11.021-.22.03-.33l.204-2.616.022-.293c.003-.029 0-.033-.03-.034zm7.203 3.757a1.427 1.427 0 0 1-.135-.607c-.004-.084-.031-.39-.235-3.06a.443.443 0 0 0-.01-.082c-.004-.011-.052-.008-.076-.008h-1.48c-.03.001-.034.005-.03.034l.021.293c.076.982.153 1.964.233 2.946.05.4.186 1.085.487 1.706.103.215.223.419.37.606.015.018.037.051.048.049.02-.003.742-1.642.804-1.765.036-.07.03-.055.003-.112zm3.861-.913h-.872a.126.126 0 0 1-.116-.178l1.178-2.625a.025.025 0 0 0-.023-.035l-1.318-.003a.148.148 0 0 1-.135-.21l.876-1.954a.025.025 0 0 0-.023-.035h-1.56c-.01 0-.02.006-.024.015l-.926 2.068c-.085.169-.314.634-.399.938a.534.534 0 0 0-.02.191.46.46 0 0 0 .23.378.981.981 0 0 0 .46.119h.59c.041 0-.688 1.482-.834 1.972a.53.53 0 0 0-.023.172.465.465 0 0 0 .23.398c.15.092.342.12.475.12l1.66-.001c.01 0 .02-.006.023-.015l.575-1.28a.025.025 0 0 0-.024-.035zm-6.93-4.937H3.1a.032.032 0 0 0-.034.033c0 1.048-.01 2.795-.01 6.829 0 .288-.269.262-.28.262h-.74c-.04.001-.044.004-.04.047.001.037.465 1.064.555 1.263.01.02.03.033.051.033.157.003.767.009.938-.014.153-.02.3-.06.438-.132.3-.156.49-.419.595-.765.052-.172.075-.353.075-.533.002-2.33 0-4.66-.007-6.991a.032.032 0 0 0-.032-.032zm11.784 6.896c0-.014-.01-.021-.024-.022h-1.465c-.048-.001-.049-.002-.05-.049v-4.66c0-.072-.005-.07.07-.07h.863c.08 0 .075.004.075-.074V8.393c0-.082.006-.076-.08-.076h-3.5c-.064 0-.075-.006-.075.073v1.445c0 .083-.006.077.08.077h.854c.075 0 .07-.004.07.07v4.624c0 .095.008.084-.085.084-.37 0-1.11-.002-1.304 0-.048.001-.06.03-.06.03l-.697 1.519s-.014.025-.008.036c.006.01.013.008.058.008 1.748.003 3.495.002 5.243.002.03-.001.034-.006.035-.033v-1.539zm4.177-3.43c0 .013-.007.023-.02.024-.346.006-.692.004-1.037.004-.014-.002-.022-.01-.022-.024-.005-.434-.007-.869-.01-1.303 0-.072-.006-.071.07-.07l.733-.003c.041 0 .081.002.12.015.093.025.16.107.165.204.006.431.002 1.153.001 1.153zm2.67.244a1.953 1.953 0 0 0-.883-.222h-.18c-.04-.001-.04-.003-.042-.04V10.21c0-.132-.007-.263-.025-.394a1.823 1.823 0 0 0-.153-.53 1.533 1.533 0 0 0-.677-.71 2.167 2.167 0 0 0-1-.258c-.153-.003-.567 0-.72 0-.07 0-.068.004-.068-.065V7.76c0-.031-.01-.041-.046-.039H17.93s-.016 0-.023.007c-.006.006-.008.012-.008.023v.546c-.008.036-.057.015-.082.022h-.95c-.022.002-.028.008-.03.032v1.481c0 .09-.004.082.082.082h.913c.082 0 .072.128.072.128V11.19s.003.117-.06.117h-1.482c-.068 0-.06.082-.06.082v1.445s-.01.068.064.068h1.457c.082 0 .076-.006.076.079v3.225c0 .088-.007.081.082.081h1.43c.09 0 .082.007.082-.08v-3.27c0-.029.006-.035.033-.035l2.323-.003c.098 0 .191.02.28.061a.46.46 0 0 1 .274.407c.008.395.003.79.003 1.185 0 .259-.107.367-.33.367h-1.218c-.023.002-.029.008-.028.033.184.437.374.871.57 1.303a.045.045 0 0 0 .04.026c.17.005.34.002.51.003.15-.002.517.004.666-.01a2.03 2.03 0 0 0 .408-.075c.59-.18.975-.698.976-1.313v-1.981c0-.128-.01-.254-.034-.38 0 .078-.029-.641-.724-.998z';

const XiaohongshuIcon: React.FC = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false">
    <path d={XIAOHONGSHU_ICON_PATH} />
  </svg>
);

/** npm's wordmark rendered as a compact, theme-coloured filled glyph. */
const NpmIcon: React.FC = () => {
  const maskId = React.useId();

  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <defs>
        <mask id={maskId}>
          <rect width="24" height="24" fill="white" />
          <text
            x="12"
            y="14.45"
            fill="black"
            textAnchor="middle"
            fontFamily="var(--font-app)"
            fontSize="5.8"
            fontWeight="800"
            letterSpacing="-0.65"
          >
            npm
          </text>
        </mask>
      </defs>
      <rect x="2" y="7" width="20" height="10" rx="1.25" fill="currentColor" mask={`url(#${maskId})`} />
    </svg>
  );
};

/**
 * Resolving a social link to its platform — by URL first, name second.
 *
 * A `social_links` entry carries a `platform` label and a `url`. The label
 * is author-typed ("GitHub", "github", "GH", …) so it cannot be matched
 * exactly; the URL host is reliable. This module identifies the platform
 * from the URL host, falling back to the label, so a link always shows the
 * right icon instead of a generic globe.
 */

/** A recognised social platform. `website` is the catch-all. */
export type SocialPlatform =
  | 'github'
  | 'linkedin'
  | 'twitter'
  | 'youtube'
  | 'instagram'
  | 'facebook'
  | 'telegram'
  | 'xiaohongshu'
  | 'scholar'
  | 'pypi'
  | 'npm'
  | 'email'
  | 'website';

/** Per-platform host fragments and the filled brand glyph to render. */
const PLATFORMS: {
  id: SocialPlatform;
  label: string;
  hosts: string[];
  aliases?: string[];
  icon: React.ReactNode;
}[] = [
  { id: 'github', label: 'GitHub', hosts: ['github.com', 'github.io'], icon: <GithubLogo weight="fill" /> },
  { id: 'linkedin', label: 'LinkedIn', hosts: ['linkedin.com', 'linked.in'], icon: <LinkedinLogo weight="fill" /> },
  { id: 'twitter', label: 'X', hosts: ['twitter.com', 'x.com'], icon: <XLogo weight="fill" /> },
  { id: 'youtube', label: 'YouTube', hosts: ['youtube.com', 'youtu.be'], icon: <YoutubeLogo weight="fill" /> },
  { id: 'instagram', label: 'Instagram', hosts: ['instagram.com'], icon: <InstagramLogo weight="fill" /> },
  { id: 'facebook', label: 'Facebook', hosts: ['facebook.com', 'fb.com'], icon: <FacebookLogo weight="fill" /> },
  { id: 'telegram', label: 'Telegram', hosts: ['t.me', 'telegram.me'], icon: <TelegramLogo weight="fill" /> },
  {
    id: 'xiaohongshu',
    label: '小红书',
    hosts: ['xiaohongshu.com', 'xhslink.com', 'rednote.com'],
    aliases: ['xhs', 'rednote', 'red note'],
    icon: <XiaohongshuIcon />,
  },
  { id: 'scholar', label: 'Google Scholar', hosts: ['scholar.google.com', 'scholar.google.'], icon: <GraduationCap weight="fill" /> },
  { id: 'pypi', label: 'PyPI', hosts: ['pypi.org', 'pythonhosted.org'], icon: <Cube weight="fill" /> },
  { id: 'npm', label: 'npm', hosts: ['npmjs.com'], icon: <NpmIcon /> },
];

const matchesPlatformName = (name: string, candidate: string) => {
  const normalizedCandidate = candidate.toLowerCase();
  const isShortAsciiAlias = normalizedCandidate.length <= 3 && /^[a-z0-9]+$/.test(normalizedCandidate);
  if (!isShortAsciiAlias) return name.includes(normalizedCandidate);

  const escapedCandidate = normalizedCandidate.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`(^|[^a-z0-9])${escapedCandidate}([^a-z0-9]|$)`).test(name);
};

/**
 * Identify a social link's platform.
 *
 * `url` is checked first — its host is the reliable signal. If the URL is
 * absent or unrecognised, `name` (the author-typed platform label) is matched
 * against the platform aliases. Short ASCII aliases such as X and XHS match
 * complete tokens so one cannot accidentally capture the other.
 */
export function identifySocialPlatform(url?: string, name?: string): SocialPlatform {
  const u = (url || '').toLowerCase();
  if (u.startsWith('mailto:') || u.includes('@')) {
    // A bare email or a mailto link.
    if (u.startsWith('mailto:') || /^[^/]+@[^/]+\.[^/]+$/.test(u)) return 'email';
  }
  for (const p of PLATFORMS) {
    if (p.hosts.some((h) => u.includes(h))) return p.id;
  }
  // Fall back to the typed label.
  const n = (name || '').toLowerCase().trim();
  if (n) {
    for (const p of PLATFORMS) {
      const aliases = [p.id, p.label.toLowerCase(), ...(p.aliases ?? [])];
      if (aliases.some((alias) => matchesPlatformName(n, alias))) return p.id;
    }
    if (n.includes('mail') || n.includes('email')) return 'email';
    if (n.includes('scholar')) return 'scholar';
  }
  return 'website';
}

/** The filled icon element for a resolved platform. */
export function socialPlatformIcon(platform: SocialPlatform): React.ReactNode {
  if (platform === 'email') return <EnvelopeSimple weight="fill" />;
  if (platform === 'website') return <Globe weight="fill" />;
  return PLATFORMS.find((p) => p.id === platform)?.icon ?? <Globe weight="fill" />;
}

/** A clean display label for a resolved platform. */
export function socialPlatformLabel(platform: SocialPlatform): string {
  if (platform === 'email') return 'Email';
  if (platform === 'website') return 'Website';
  return PLATFORMS.find((p) => p.id === platform)?.label ?? 'Website';
}

/**
 * One-shot helper: resolve a link's icon and label from its url + name.
 * `preferTypedLabel` keeps the author's own label when it is non-empty —
 * useful where the label is shown verbatim (e.g. "Personal Site").
 */
export function resolveSocialLink(
  url?: string,
  name?: string,
): { platform: SocialPlatform; icon: React.ReactNode; label: string } {
  const platform = identifySocialPlatform(url, name);
  return {
    platform,
    icon: socialPlatformIcon(platform),
    label: socialPlatformLabel(platform),
  };
}
