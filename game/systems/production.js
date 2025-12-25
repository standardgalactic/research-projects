export function yearlyProduction(p, race) {
  if (p.population <= 0) return;

  const maxF = Math.floor((p.population / 10000) * 10);
  const maxM = Math.floor((p.population / 10000) * 10);

  p.installations.factories = Math.min(p.installations.factories, maxF);
  p.installations.mines = Math.min(p.installations.mines, maxM);

  p.resources += Math.floor(p.population / 1000);
}
