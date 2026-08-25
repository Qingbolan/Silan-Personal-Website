import {
  BookOpen,
  ExternalLink,
  FileText,
  Github,
  Globe2,
  Link2,
  Paperclip,
} from 'lucide-react';
import type { BlogResource } from '../types/blog';

const resourceIcon = (kind: string) => {
  switch (kind) {
    case 'github':
      return Github;
    case 'paper':
    case 'doi':
      return FileText;
    case 'website':
      return Globe2;
    case 'documentation':
      return BookOpen;
    default:
      return Link2;
  }
};

export function ArticleResourceStrip({
  projectName,
  publicationVenue,
  resources,
  language,
}: {
  projectName?: string;
  publicationVenue?: string;
  resources: BlogResource[];
  language: string;
}) {
  if (!projectName && !publicationVenue && resources.length === 0) return null;

  return (
    <aside
      data-ds
      aria-label={language === 'zh' ? '文章外部资源' : 'Article resources'}
      className="mt-8 overflow-hidden rounded-ds-lg border border-ds-border bg-ds-surface"
    >
      <div className="flex min-w-0 flex-col lg:flex-row lg:items-stretch">
        <div className="flex min-w-0 items-center gap-3 border-b border-ds-border px-5 py-4 lg:min-w-[17rem] lg:border-b-0 lg:border-r">
          <span className="grid size-9 shrink-0 place-items-center rounded-ds-md bg-ds-primary/10 text-ds-primary">
            <Paperclip className="size-[17px]" aria-hidden />
          </span>
          <span className="min-w-0">
            <span className="block font-mono text-ds-2xs font-semibold uppercase tracking-[0.14em] text-ds-fg-subtle">
              {language === 'zh' ? '项目附件' : 'Project attachments'}
            </span>
            {projectName && (
              <strong className="mt-0.5 block truncate text-ds-sm font-semibold text-ds-fg">
                {projectName}
              </strong>
            )}
            {publicationVenue && (
              <span className="block text-ds-xs text-ds-fg-muted">{publicationVenue}</span>
            )}
          </span>
        </div>
        <div className="flex min-w-0 flex-1 snap-x gap-1 overflow-x-auto p-2">
          {resources.map((resource) => {
            const Icon = resourceIcon(resource.kind);
            return (
              <a
                key={`${resource.kind}:${resource.url}`}
                href={resource.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex min-w-[10.5rem] snap-start items-center gap-3 rounded-ds-md px-3 py-2.5 text-ds-fg transition hover:bg-ds-surface-2"
              >
                <Icon className="size-[17px] shrink-0 text-ds-fg-subtle transition group-hover:text-ds-primary" aria-hidden />
                <span className="min-w-0 flex-1">
                  <span className="block font-mono text-ds-2xs font-semibold uppercase tracking-[0.12em] text-ds-fg-subtle">
                    {resource.kind}
                  </span>
                  <span className="block truncate text-ds-sm font-semibold">{resource.label}</span>
                </span>
                <ExternalLink className="size-[13px] shrink-0 text-ds-fg-subtle" aria-hidden />
              </a>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
