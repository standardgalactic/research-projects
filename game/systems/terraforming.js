export function terraformStep(p, race) {
  const r = race.modifiers.terraforming || 0;
  function shift(v, i, s) {
    return v < i ? Math.min(v + s, i) : Math.max(v - s, i);
  }
  p.env.gravity = shift(p.env.gravity, race.ideal.gravity, 0.01 * r);
  p.env.temp = shift(p.env.temp, race.ideal.temp, 0.5 * r);
  p.env.rad = shift(p.env.rad, race.ideal.rad, 0.5 * r);
}
