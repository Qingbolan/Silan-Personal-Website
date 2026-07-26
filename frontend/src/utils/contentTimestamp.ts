export const normalizeContentTimestamp = (value: unknown): string | undefined => {
  if (typeof value !== 'string' || !value) return undefined;

  const date = new Date(value);
  if (Number.isNaN(date.getTime()) || date.getUTCFullYear() <= 1) return undefined;

  return value;
};
