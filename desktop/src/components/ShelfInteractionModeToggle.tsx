import { Eye, Settings2 } from 'lucide-react';
import type { ShelfInteractionMode } from '../lib/shelfInteractionMode';

type ShelfInteractionModeToggleProps = {
  mode: ShelfInteractionMode;
  onToggle: () => void;
};

export function ShelfInteractionModeToggle({
  mode,
  onToggle,
}: ShelfInteractionModeToggleProps) {
  const managing = mode === 'manage';
  const label = managing
    ? 'Management mode. Switch to browse mode'
    : 'Browse mode. Switch to management mode';
  const Icon = managing ? Settings2 : Eye;

  return (
    <button
      type="button"
      className="dock-mode-toggle"
      data-mode={mode}
      aria-label={label}
      aria-pressed={managing}
      title={label}
      onClick={onToggle}
    >
      <Icon size={15} aria-hidden="true" />
    </button>
  );
}
