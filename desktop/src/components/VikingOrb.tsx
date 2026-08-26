import React from 'react';
import { startupOrbFrameAt, type StartupOrbPointer } from '../lib/startupOrb';

const PAPER = '#f9f9f9';
const BODY = '#0a0a0c';

export function VikingOrb() {
  const maskId = React.useId().replace(/:/g, '');
  const [frame, setFrame] = React.useState(() => startupOrbFrameAt(0));
  const targetRef = React.useRef<StartupOrbPointer>({ nx: 0, ny: 0, activity: 0 });
  const smoothedRef = React.useRef<StartupOrbPointer>({ nx: 0, ny: 0, activity: 0 });

  React.useEffect(() => {
    let animationFrame = 0;
    let lastFrame = 0;
    let clock = 0;

    const handlePointerMove = (event: PointerEvent) => {
      if (event.pointerType === 'touch') return;
      const next = {
        nx: Math.max(-1, Math.min(1, (event.clientX - window.innerWidth / 2) / Math.max(1, window.innerWidth / 2))),
        ny: Math.max(-1, Math.min(1, (event.clientY - window.innerHeight / 2) / Math.max(1, window.innerHeight / 2))),
      };
      const distance = Math.hypot(
        next.nx - targetRef.current.nx,
        next.ny - targetRef.current.ny,
      );
      targetRef.current = {
        ...next,
        activity: Math.min(1, (targetRef.current.activity ?? 0) + 0.18 + distance * 1.8),
      };
    };

    const tick = (now: number) => {
      const delta = lastFrame ? Math.min((now - lastFrame) / 1_000, 0.064) : 0;
      lastFrame = now;
      clock += delta;

      targetRef.current.activity = (targetRef.current.activity ?? 0) * Math.exp(-delta / 0.72);
      const catchUp = 1 - Math.exp(-delta / 0.24);
      const attentionCatchUp = 1 - Math.exp(-delta / 0.16);
      smoothedRef.current = {
        nx: smoothedRef.current.nx + (targetRef.current.nx - smoothedRef.current.nx) * catchUp,
        ny: smoothedRef.current.ny + (targetRef.current.ny - smoothedRef.current.ny) * catchUp,
        activity: (smoothedRef.current.activity ?? 0) + (
          (targetRef.current.activity ?? 0) - (smoothedRef.current.activity ?? 0)
        ) * attentionCatchUp,
      };
      setFrame(startupOrbFrameAt(clock * 1_000, smoothedRef.current));
      animationFrame = window.requestAnimationFrame(tick);
    };

    window.addEventListener('pointermove', handlePointerMove);
    animationFrame = window.requestAnimationFrame(tick);
    return () => {
      window.cancelAnimationFrame(animationFrame);
      window.removeEventListener('pointermove', handlePointerMove);
    };
  }, []);

  return (
    <svg
      className="viking-orb"
      viewBox="-150 -150 300 300"
      role="img"
      aria-label="Silan Viking, awake and looking around"
    >
      <defs>
        <mask id={maskId} maskUnits="userSpaceOnUse" x="-150" y="-150" width="300" height="300">
          <circle cx="0" cy="0" r="100" fill="#fff" />
          {frame.eyes.map((eye, index) => (
            <path
              key={index}
              d={eye.path}
              transform={eye.matrix}
              opacity={eye.opacity}
              fill="#000"
            />
          ))}
        </mask>
      </defs>
      <g transform={frame.bodyTransform}>
        <circle cx="0" cy="0" r="100" fill={PAPER} />
        <circle cx="0" cy="0" r="100" fill={BODY} mask={`url(#${maskId})`} />
      </g>
    </svg>
  );
}
