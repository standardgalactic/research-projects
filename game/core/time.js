export const YEAR_SECONDS = 10;
let accumulator = 0;

export function updateTime(dt, onYear) {
  accumulator += dt;
  if (accumulator >= YEAR_SECONDS) {
    accumulator = 0;
    onYear();
  }
}
