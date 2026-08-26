export type StartupOrbPointer = {
  nx: number;
  ny: number;
  activity?: number;
};

export type StartupOrbEye = {
  matrix: string;
  opacity: number;
  path: string;
};

export type StartupOrbFrame = {
  bodyTransform: string;
  eyes: StartupOrbEye[];
};

type Vec3 = [number, number, number];

type EyePose = {
  x: number;
  y: number;
  a: number;
  b: number;
  c: number;
  d: number;
  depth: number;
};

type EyeConfig = {
  width: number;
  height: number;
  tilt: number;
  open: number;
};

type OrbExpression = {
  gaze: { yaw: number; pitch: number; roll: number };
  split: number;
  eyes: [EyeConfig, EyeConfig];
};

type AffectAnchor = {
  x: number;
  y: number;
  expression: OrbExpression;
};

// These measured proportions and the spherical projection follow bloub's idle
// avatar. The startup intentionally uses only this resting body: the arrival's
// character comes from gaze, occlusion and blinking, not decorative shape swaps.
const EYE_WIDTH = 0.186;
const EYE_HEIGHT = 0.412;
const REST_GAZE = { yaw: 28.49, pitch: 28.62, roll: -13 };
const ORB_RADIUS = 100;
const EYE_TURN_DURATION_SECONDS = 1.5;
const FULL_TURN_DEGREES = 360;
const POINTER_YAW = 16;
const POINTER_PITCH = 13;

const eye = (width: number, height: number, tilt = 0, open = 1): EyeConfig => ({
  width,
  height,
  tilt,
  open,
});

// Bloub's measured expressions are landmarks in a continuous affect field.
// Every landmark contributes to every frame; none is ever selected as a state.
const AFFECT_FIELD: readonly AffectAnchor[] = [
  { x: -0.62, y: 0.72, expression: {
    gaze: { yaw: 16, pitch: -9, roll: -15 },
    split: 16.5,
    eyes: [eye(0.24, 0.46, -8), eye(0.2, 0.38, -8)],
  } },
  { x: 0.08, y: 0.82, expression: {
    gaze: { yaw: 4, pitch: 5, roll: -4 },
    split: 16,
    eyes: [eye(0.21, 0.44), eye(0.21, 0.44)],
  } },
  { x: -0.58, y: -0.18, expression: {
    gaze: { yaw: 12, pitch: 6, roll: -6 },
    split: 16,
    eyes: [eye(0.21, 0.4), eye(0.22, 0.15)],
  } },
  { x: 0.76, y: 0.68, expression: {
    gaze: { yaw: 5, pitch: 9, roll: 0 },
    split: 17,
    eyes: [eye(0.27, 0.17, -14), eye(0.27, 0.17, 14)],
  } },
  { x: 0.72, y: -0.24, expression: {
    gaze: { yaw: 5, pitch: 17, roll: 0 },
    split: 17,
    eyes: [eye(0.3, 0.15, -18), eye(0.3, 0.15, 18)],
  } },
  { x: 0, y: 0, expression: {
    gaze: REST_GAZE,
    split: 15.46,
    eyes: [eye(EYE_WIDTH, EYE_HEIGHT), eye(EYE_WIDTH, EYE_HEIGHT)],
  } },
];

const ATTENTIVE_EXPRESSION = AFFECT_FIELD[1].expression;

const clamp = (value: number, low = 0, high = 1) => (
  value < low ? low : value > high ? high : value
);
const lerp = (from: number, to: number, amount: number) => from + (to - from) * amount;
const radians = (degrees: number) => (degrees * Math.PI) / 180;
const round = (value: number) => Math.round(value * 100) / 100;
const easeInOutCubic = (value: number) => (
  value < 0.5 ? 4 * value ** 3 : 1 - (-2 * value + 2) ** 3 / 2
);
const easeOutQuint = (value: number) => 1 - (1 - value) ** 5;

function periodicNoise(time: number, period: number, seed = 0) {
  const phase = (time / period) * Math.PI * 2;
  return (
    0.55 * Math.sin(phase + seed)
    + 0.3 * Math.sin(2 * phase + seed * 1.7 + 1.1)
    + 0.15 * Math.sin(3 * phase + seed * 2.3 + 2.4)
  );
}

function rotateBasis(first: Vec3, second: Vec3, angle: number): [Vec3, Vec3] {
  const cosine = Math.cos(angle);
  const sine = Math.sin(angle);
  return [
    [
      first[0] * cosine + second[0] * sine,
      first[1] * cosine + second[1] * sine,
      first[2] * cosine + second[2] * sine,
    ],
    [
      second[0] * cosine - first[0] * sine,
      second[1] * cosine - first[1] * sine,
      second[2] * cosine - first[2] * sine,
    ],
  ];
}

function eyePoses(gaze: typeof REST_GAZE, split: number): [EyePose, EyePose] {
  let forward: Vec3 = [0, 0, 1];
  let right: Vec3 = [1, 0, 0];
  let down: Vec3 = [0, 1, 0];

  [forward, right] = rotateBasis(forward, right, radians(gaze.yaw));
  [down, forward] = rotateBasis(down, forward, radians(gaze.pitch));
  [right, down] = rotateBasis(right, down, radians(gaze.roll));

  const project = (side: number): EyePose => {
    const [eyeForward, eyeRight] = rotateBasis(forward, right, radians(split * side));
    return {
      x: eyeForward[0] * ORB_RADIUS,
      y: eyeForward[1] * ORB_RADIUS,
      a: eyeRight[0],
      b: eyeRight[1],
      c: down[0],
      d: down[1],
      depth: eyeForward[2],
    };
  };

  return [project(-1), project(1)];
}

const blinkStarts = [1.4, 3.82, 4.06, 7.28, 10.91];

function blinkAmount(time: number) {
  const localTime = time % 12;
  for (const start of blinkStarts) {
    const progress = (localTime - start) / 0.18;
    if (progress >= 0 && progress <= 1) {
      return progress < 0.45 ? 1 - progress / 0.45 : (progress - 0.45) / 0.55;
    }
  }
  return 1;
}

function eyeMatrix(pose: EyePose, config: EyeConfig, lid: number) {
  const tilt = radians(config.tilt);
  const cosine = Math.cos(tilt);
  const sine = Math.sin(tilt);
  const axisX = pose.a * cosine + pose.c * sine;
  const axisY = pose.b * cosine + pose.d * sine;
  const crossX = -pose.a * sine + pose.c * cosine;
  const crossY = -pose.b * sine + pose.d * cosine;
  const verticalScale = 0.06 + 0.94 * clamp(Math.min(lid, config.open));
  return `matrix(${round(axisX)},${round(axisY * verticalScale)},${round(crossX)},${round(crossY * verticalScale)},${round(pose.x)},${round(pose.y)})`;
}

export function startupOrbEyePath(config: Pick<EyeConfig, 'width' | 'height'> = {
  width: EYE_WIDTH,
  height: EYE_HEIGHT,
}) {
  const width = config.width * ORB_RADIUS;
  const height = config.height * ORB_RADIUS;
  const halfWidth = width / 2;
  const halfHeight = height / 2;
  const radius = Math.min(halfWidth, halfHeight);
  return (
    `M${round(-halfWidth)} ${round(-halfHeight + radius)}`
    + `A${round(radius)} ${round(radius)} 0 0 1 ${round(-halfWidth + radius)} ${round(-halfHeight)}`
    + `L${round(halfWidth - radius)} ${round(-halfHeight)}`
    + `A${round(radius)} ${round(radius)} 0 0 1 ${round(halfWidth)} ${round(-halfHeight + radius)}`
    + `L${round(halfWidth)} ${round(halfHeight - radius)}`
    + `A${round(radius)} ${round(radius)} 0 0 1 ${round(halfWidth - radius)} ${round(halfHeight)}`
    + `L${round(-halfWidth + radius)} ${round(halfHeight)}`
    + `A${round(radius)} ${round(radius)} 0 0 1 ${round(-halfWidth)} ${round(halfHeight - radius)}Z`
  );
}

function blendEye(from: EyeConfig, to: EyeConfig, amount: number): EyeConfig {
  return {
    width: lerp(from.width, to.width, amount),
    height: lerp(from.height, to.height, amount),
    tilt: lerp(from.tilt, to.tilt, amount),
    open: lerp(from.open, to.open, amount),
  };
}

function blendExpression(from: OrbExpression, to: OrbExpression, amount: number): OrbExpression {
  return {
    gaze: {
      yaw: lerp(from.gaze.yaw, to.gaze.yaw, amount),
      pitch: lerp(from.gaze.pitch, to.gaze.pitch, amount),
      roll: lerp(from.gaze.roll, to.gaze.roll, amount),
    },
    split: lerp(from.split, to.split, amount),
    eyes: [
      blendEye(from.eyes[0], to.eyes[0], amount),
      blendEye(from.eyes[1], to.eyes[1], amount),
    ] as [EyeConfig, EyeConfig],
  };
}

function autonomousExpressionAt(time: number): OrbExpression {
  const x = periodicNoise(time, 8.7, 0.6) * 0.76 + periodicNoise(time, 3.8, 2.4) * 0.12;
  const y = periodicNoise(time, 6.9, 1.7) * 0.7 + periodicNoise(time, 4.4, 0.2) * 0.1;
  const weights = AFFECT_FIELD.map((anchor) => {
    const distanceSquared = (x - anchor.x) ** 2 + (y - anchor.y) ** 2;
    return Math.exp(-distanceSquared / 0.34) + 0.012;
  });
  const totalWeight = weights.reduce((sum, weight) => sum + weight, 0);
  const sample = (selector: (expression: OrbExpression) => number) => AFFECT_FIELD.reduce(
    (sum, anchor, index) => sum + selector(anchor.expression) * weights[index],
    0,
  ) / totalWeight;
  const sampleEye = (index: 0 | 1): EyeConfig => ({
    width: clamp(sample((expression) => expression.eyes[index].width), 0.14, 0.34),
    height: clamp(sample((expression) => expression.eyes[index].height), 0.12, 0.5),
    tilt: clamp(sample((expression) => expression.eyes[index].tilt), -22, 22),
    open: clamp(sample((expression) => expression.eyes[index].open), 0.72, 1),
  });
  const asymmetry = periodicNoise(time, 4.6, 0.9) * 0.008;
  const left = sampleEye(0);
  const right = sampleEye(1);

  return {
    gaze: {
      yaw: sample((expression) => expression.gaze.yaw),
      pitch: sample((expression) => expression.gaze.pitch),
      roll: sample((expression) => expression.gaze.roll),
    },
    split: sample((expression) => expression.split),
    eyes: [
      { ...left, width: left.width + asymmetry, height: left.height - asymmetry },
      { ...right, width: right.width - asymmetry, height: right.height + asymmetry },
    ],
  };
}

function expressionAt(time: number, pointerActivity: number) {
  const autonomous = autonomousExpressionAt(time);
  const attention = easeOutQuint(clamp(pointerActivity)) * 0.72;
  return blendExpression(autonomous, ATTENTIVE_EXPRESSION, attention);
}

export function startupOrbFrameAt(
  elapsedMs: number,
  pointer: StartupOrbPointer = { nx: 0, ny: 0 },
): StartupOrbFrame {
  const time = Math.max(0, elapsedMs) / 1_000;
  const expression = expressionAt(time, pointer.activity ?? 0);
  const turnProgress = easeInOutCubic(clamp(time / EYE_TURN_DURATION_SECONDS));
  const spin = FULL_TURN_DEGREES * (1 - turnProgress);
  const follow = easeOutQuint(clamp(time / 0.6));
  const nx = clamp(pointer.nx, -1, 1);
  const ny = clamp(pointer.ny, -1, 1);

  const driftYaw = periodicNoise(time, 11.3, 0.4) * 5.5 + periodicNoise(time, 3.7, 2.1) * 1.6;
  const driftPitch = periodicNoise(time, 9.1, 1.3) * 4.2 + periodicNoise(time, 4.3, 0.7) * 1.3;
  const driftRoll = periodicNoise(time, 13.7, 3.2) * 2.2;
  const gaze = {
    yaw: expression.gaze.yaw + nx * POINTER_YAW * follow + driftYaw - spin,
    pitch: expression.gaze.pitch - ny * POINTER_PITCH * follow + driftPitch,
    roll: expression.gaze.roll + driftRoll,
  };

  const lid = blinkAmount(time);
  const driftX = periodicNoise(time, 7.9, 1.9) * 0.9 + nx * 1.2;
  const driftY = periodicNoise(time, 5.3, 0.3) * 1.1 + ny * 0.8;
  const breath = Math.sin((time / 3.4) * Math.PI * 2) * 0.009;
  const squash = periodicNoise(time, 4.7, 2.7) * 0.004;
  const bodyRoll = periodicNoise(time, 5.9, 1.5) * 1.25 + nx * 0.8;
  const eyes = eyePoses(gaze, expression.split)
    .map((pose, index) => ({ pose, config: expression.eyes[index] }))
    .filter(({ pose }) => pose.depth > 0.02)
    .map(({ pose, config }) => ({
      matrix: eyeMatrix(pose, config, lid),
      opacity: clamp(pose.depth / 0.12),
      path: startupOrbEyePath(config),
    }));

  return {
    bodyTransform: `translate(${round(driftX)} ${round(driftY)}) rotate(${round(bodyRoll)}) scale(${round(1 + squash)} ${round(1 + breath - squash)})`,
    eyes,
  };
}
