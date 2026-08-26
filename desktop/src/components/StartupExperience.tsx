import React from 'react';
import { DesktopTitlebar } from './DesktopTitlebar';
import { VikingOrb } from './VikingOrb';
import { desktopWindowChromeClassName } from '../lib/desktopWindow';
import {
  STARTUP_ARRIVAL_DURATION_MS,
  STARTUP_LOADING_PHASE_DURATION_MS,
  STARTUP_REVEAL_AT_MS,
  STARTUP_REVEAL_DURATION_MS,
  STARTUP_SETTLE_DURATION_MS,
  startupLoadingPhases,
  type StartupSequenceStage,
} from '../lib/startupSequence';
import './StartupExperience.css';

const publishingLifecycle = [
  { step: '01', action: 'Capture', artifact: 'private/source' },
  { step: '02', action: 'Connect', artifact: 'typed/relations' },
  { step: '03', action: 'Review', artifact: 'proposal.diff' },
  { step: '04', action: 'Publish', artifact: 'verified/release' },
] as const;

export function StartupExperience({ children }: { children: React.ReactNode }) {
  const [stage, setStage] = React.useState<StartupSequenceStage>('arrival');
  const timersRef = React.useRef<number[]>([]);

  React.useEffect(() => {
    const primer = document.getElementById('boot-primer');
    if (!primer) return undefined;

    const handoffFrame = window.requestAnimationFrame(() => {
      primer.classList.add('is-handoff');
    });
    const removalTimer = window.setTimeout(() => primer.remove(), 620);
    return () => {
      window.cancelAnimationFrame(handoffFrame);
      window.clearTimeout(removalTimer);
    };
  }, []);

  const clearTimers = React.useCallback(() => {
    timersRef.current.forEach((timer) => window.clearTimeout(timer));
    timersRef.current = [];
  }, []);

  const reveal = React.useCallback(() => {
    clearTimers();
    setStage('reveal');
    timersRef.current.push(window.setTimeout(() => setStage('complete'), STARTUP_REVEAL_DURATION_MS));
  }, [clearTimers]);

  React.useEffect(() => {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reducedMotion) {
      const revealTimer = window.setTimeout(() => setStage('reveal'), 0);
      const completeTimer = window.setTimeout(() => setStage('complete'), 180);
      timersRef.current = [revealTimer, completeTimer];
      return clearTimers;
    }

    timersRef.current = [
      window.setTimeout(() => setStage('settle'), STARTUP_ARRIVAL_DURATION_MS),
      window.setTimeout(
        () => setStage('explain'),
        STARTUP_ARRIVAL_DURATION_MS + STARTUP_SETTLE_DURATION_MS,
      ),
      window.setTimeout(reveal, STARTUP_REVEAL_AT_MS),
    ];
    return clearTimers;
  }, [clearTimers, reveal]);

  React.useEffect(() => {
    if (stage === 'complete') return undefined;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key !== 'Escape' && event.key !== 'Enter') return;
      event.preventDefault();
      reveal();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [reveal, stage]);

  const introVisible = stage !== 'complete';

  return (
    <div className="startup-experience-host" data-stage={stage}>
      <div className="startup-experience-content" aria-hidden={introVisible || undefined}>
        {children}
      </div>

      {introVisible && (
        <div
          className={`startup-experience ${desktopWindowChromeClassName}`}
          data-stage={stage}
          role="dialog"
          aria-modal="true"
          aria-label="Silan Viking startup"
        >
          <DesktopTitlebar title="Silan Viking" showWorkspaceNavigation={false} />

          <main className="startup-canvas">
            <header className="startup-brandline" aria-hidden={stage === 'arrival'}>
              <div className="startup-wordmark">
                <strong>SILAN</strong>
                <span>VIKING</span>
              </div>
              <div className="startup-ownership-mark">
                <span>LOCAL FIRST</span>
                <i />
                <span>OWNER CONTROLLED</span>
              </div>
            </header>

            <div className="startup-scene">
              <section className="startup-avatar-stage">
                <div className="startup-avatar">
                  <VikingOrb />
                </div>
                <div
                  className="startup-loading-copy"
                  role="status"
                  aria-label="Loading the Silan Viking workspace"
                >
                  {startupLoadingPhases.map((phase, index) => (
                    <span
                      key={phase.message}
                      style={{
                        '--startup-loading-delay': `${index * STARTUP_LOADING_PHASE_DURATION_MS}ms`,
                        '--startup-loading-duration': `${STARTUP_LOADING_PHASE_DURATION_MS + 240}ms`,
                      } as React.CSSProperties}
                    >
                      {phase.message}
                    </span>
                  ))}
                </div>
                <span className="startup-avatar-coordinate" aria-hidden="true">CONTEXT / AWAKE</span>
              </section>

              <section className="startup-story" aria-live="polite" aria-atomic="true">
                <p className="startup-story-kicker"><span>Personal context system</span></p>
                <h1 aria-label="Your research has a memory.">
                  <span className="startup-story-line" aria-hidden="true"><span>Your research</span></span>
                  <span className="startup-story-line" aria-hidden="true"><span>has a</span></span>
                  <span className="startup-story-line" aria-hidden="true"><span>memory.</span></span>
                </h1>
                <div className="startup-story-body-mask">
                  <p className="startup-story-body">
                    Keep the first note, its evidence, and every public form connected — locally,
                    reviewably, and under your control.
                  </p>
                </div>
                <div className="startup-story-principle-mask">
                  <p className="startup-story-principle">
                    <span>Agents propose.</span>
                    <span>You decide.</span>
                  </p>
                </div>
              </section>
            </div>

            <footer className="startup-footer">
              <ol aria-label="Silan Viking research publishing lifecycle">
                {publishingLifecycle.map((item) => (
                  <li key={item.action}>
                    <span>{item.step}</span>
                    <strong>{item.action}</strong>
                    <code>{item.artifact}</code>
                  </li>
                ))}
              </ol>
              <button type="button" className="startup-skip" onClick={reveal}>
                <span>Enter workspace</span>
                <kbd>↵</kbd>
              </button>
            </footer>

            <div className="startup-ghost-wordmark" aria-hidden="true"><span>VIKING</span></div>
          </main>
        </div>
      )}
    </div>
  );
}
