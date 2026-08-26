export type ShelfInteractionMode = 'browse' | 'manage';

export type ShelfInteractionModeEvent =
  | { type: 'browse' }
  | { type: 'manage' }
  | { type: 'toggle' };

export const initialShelfInteractionMode: ShelfInteractionMode = 'browse';

export const transitionShelfInteractionMode = (
  mode: ShelfInteractionMode,
  event: ShelfInteractionModeEvent,
): ShelfInteractionMode => {
  switch (event.type) {
    case 'browse':
      return 'browse';
    case 'manage':
      return 'manage';
    case 'toggle':
      return mode === 'browse' ? 'manage' : 'browse';
    default: {
      const unreachable: never = event;
      throw new Error(`Unsupported shelf interaction event: ${String(unreachable)}`);
    }
  }
};

export const managementControlsVisible = (mode: ShelfInteractionMode) => mode === 'manage';
