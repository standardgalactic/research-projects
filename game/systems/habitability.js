export function habitabilityScore(env, race) {
  function s(v, i, r) {
    return Math.max(0, 1 - Math.abs(v - i) / r);
  }
  return s(env.gravity, race.ideal.gravity, race.range.gravity) *
         s(env.temp, race.ideal.temp, race.range.temp) *
         s(env.rad, race.ideal.rad, race.range.rad);
}
