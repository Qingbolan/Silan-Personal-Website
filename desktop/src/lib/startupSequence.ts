export const startupSequenceStages = ['arrival', 'settle', 'explain'] as const;

export type StartupNarrativeStage = typeof startupSequenceStages[number];
export type StartupSequenceStage = StartupNarrativeStage | 'reveal' | 'complete';

export const STARTUP_ARRIVAL_DURATION_MS = 1_600;
export const STARTUP_SETTLE_DURATION_MS = 1_050;
export const STARTUP_EXPLAIN_DURATION_MS = 1_850;
export const STARTUP_REVEAL_DURATION_MS = 640;

export const STARTUP_REVEAL_AT_MS = (
  STARTUP_ARRIVAL_DURATION_MS
  + STARTUP_SETTLE_DURATION_MS
  + STARTUP_EXPLAIN_DURATION_MS
);

export const STARTUP_TOTAL_DURATION_MS = STARTUP_REVEAL_AT_MS + STARTUP_REVEAL_DURATION_MS;

export const startupLoadingPhases = [
  { message: 'Reading the local source' },
  { message: 'Reconnecting notes and evidence' },
  { message: 'Restoring review boundaries' },
  { message: 'Preparing the workspace' },
] as const;

export const STARTUP_LOADING_PHASE_DURATION_MS = (
  STARTUP_REVEAL_AT_MS / startupLoadingPhases.length
);

export function startupLoadingPhaseAt(elapsedMs: number) {
  const phaseIndex = Math.min(
    startupLoadingPhases.length - 1,
    Math.floor(Math.max(0, elapsedMs) / STARTUP_LOADING_PHASE_DURATION_MS),
  );
  return { ...startupLoadingPhases[phaseIndex], index: phaseIndex };
}

/** A deterministic arrival lifecycle shared by the visual and accessibility paths. */
export function startupSequenceStageAt(elapsedMs: number): StartupSequenceStage {
  const elapsed = Math.max(0, elapsedMs);
  if (elapsed < STARTUP_ARRIVAL_DURATION_MS) return 'arrival';
  if (elapsed < STARTUP_ARRIVAL_DURATION_MS + STARTUP_SETTLE_DURATION_MS) return 'settle';
  if (elapsed < STARTUP_REVEAL_AT_MS) return 'explain';
  if (elapsed < STARTUP_TOTAL_DURATION_MS) return 'reveal';
  return 'complete';
}

export const startupSequenceTransitions: ReadonlyArray<{
  stage: StartupSequenceStage;
  at: number;
}> = [
  { stage: 'settle', at: STARTUP_ARRIVAL_DURATION_MS },
  { stage: 'explain', at: STARTUP_ARRIVAL_DURATION_MS + STARTUP_SETTLE_DURATION_MS },
  { stage: 'reveal', at: STARTUP_REVEAL_AT_MS },
  { stage: 'complete', at: STARTUP_TOTAL_DURATION_MS },
];
