import React from 'react';
import type { WorkspaceLocation } from '../lib/workspaceNavigation';

export type WorkspaceTitlebarTab = {
  id: string;
  label: string;
  kind: WorkspaceLocation['kind'];
  dirty?: boolean;
};

type WorkspaceTabStripProps = {
  tabs: WorkspaceTitlebarTab[];
  activeTabId: string;
  onTabSelect: (tabId: string) => void;
  onTabClose: (tabId: string) => void;
  onNewTab: () => void;
};

function WorkspaceTabGlyph({ kind }: { kind: WorkspaceLocation['kind'] }) {
  return (
    <svg
      className="workspace-tab-glyph"
      width="14"
      height="14"
      viewBox="0 0 20 20"
      fill="none"
      aria-hidden="true"
      focusable="false"
    >
      {kind === 'dashboard' && (
        <>
          <rect x="3.25" y="3.25" width="5.25" height="5.25" rx="1" />
          <rect x="11.5" y="3.25" width="5.25" height="5.25" rx="1" />
          <rect x="3.25" y="11.5" width="5.25" height="5.25" rx="1" />
          <rect x="11.5" y="11.5" width="5.25" height="5.25" rx="1" />
        </>
      )}
      {(kind === 'shelf' || kind === 'series') && (
        <>
          <path d="M3.25 6.25h13.5v9.5a1 1 0 0 1-1 1H4.25a1 1 0 0 1-1-1v-9.5Z" />
          <path d="M3.25 6.25V4.5a1 1 0 0 1 1-1h4l1.5 1.75h6a1 1 0 0 1 1 1" />
        </>
      )}
      {kind === 'editor' && (
        <>
          <path d="M5 2.75h6l4 4v10.5H5V2.75Z" />
          <path d="M11 2.75v4h4M7.5 10h5M7.5 13h5" />
        </>
      )}
      {kind === 'settings' && (
        <>
          <circle cx="10" cy="10" r="2.5" />
          <path d="M8.8 2.75h2.4l.45 2a6 6 0 0 1 1.65.95l1.95-.6 1.2 2.08-1.5 1.4a6 6 0 0 1 0 1.9l1.5 1.4-1.2 2.08-1.95-.6a6 6 0 0 1-1.65.95l-.45 2H8.8l-.45-2a6 6 0 0 1-1.65-.95l-1.95.6-1.2-2.08 1.5-1.4a6 6 0 0 1 0-1.9l-1.5-1.4 1.2-2.08 1.95.6a6 6 0 0 1 1.65-.95l.45-2Z" />
        </>
      )}
    </svg>
  );
}

function CloseGlyph() {
  return (
    <svg width="12" height="12" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="m4.5 4.5 7 7M11.5 4.5l-7 7" />
    </svg>
  );
}

function AddGlyph() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M8 3.25v9.5M3.25 8h9.5" />
    </svg>
  );
}

export function WorkspaceTabStrip({
  tabs,
  activeTabId,
  onTabSelect,
  onTabClose,
  onNewTab,
}: WorkspaceTabStripProps) {
  const canClose = tabs.length > 1;

  return (
    <div className="desktop-titlebar-tabs">
      <div className="workspace-tab-list" role="tablist" aria-label="Open workspace tabs">
        {tabs.map((tab) => {
          const active = tab.id === activeTabId;
          return (
            <div
              className="workspace-tab"
              data-active={active ? 'true' : undefined}
              key={tab.id}
            >
              <button
                type="button"
                className="workspace-tab-select"
                role="tab"
                aria-selected={active}
                title={tab.label}
                onClick={() => onTabSelect(tab.id)}
                onAuxClick={(event) => {
                  if (event.button !== 1 || !canClose) return;
                  event.preventDefault();
                  onTabClose(tab.id);
                }}
              >
                <WorkspaceTabGlyph kind={tab.kind} />
                <span>{tab.label}</span>
                {tab.dirty && <i className="workspace-tab-dirty" aria-label="Unsaved changes" />}
              </button>
              {canClose && (
                <button
                  type="button"
                  className="workspace-tab-close"
                  aria-label={`Close ${tab.label}`}
                  title={`Close ${tab.label}`}
                  onClick={() => onTabClose(tab.id)}
                >
                  <CloseGlyph />
                </button>
              )}
            </div>
          );
        })}
      </div>
      <button
        type="button"
        className="workspace-tab-new"
        onClick={onNewTab}
        aria-label="New workspace tab"
        title="New workspace tab"
      >
        <AddGlyph />
      </button>
    </div>
  );
}
