export class HUD {
  constructor() {
    this.el = document.createElement("pre");
    this.el.style.position = "fixed";
    this.el.style.bottom = "10px";
    this.el.style.left = "10px";
    this.el.style.padding = "10px";
    this.el.style.background = "rgba(0,0,0,0.7)";
    this.el.style.color = "#0f0";
    this.el.style.fontFamily = "monospace";
    this.el.style.fontSize = "13px";
    document.body.appendChild(this.el);

    window.addEventListener("keydown", e => this.handleKey(e));
  }

  handleKey(e) {
    const p = window.__selectedPlanet;
    if (!p || window.__landingState !== "landed") return;

    switch (e.key.toLowerCase()) {
      case "f":
        p.buildQueue.factories++;
        break;
      case "m":
        p.buildQueue.mines++;
        break;
      case "t":
        p.buildQueue.terraform = !p.buildQueue.terraform;
        break;
    }
  }

  update() {
    const p = window.__selectedPlanet;
    const race = window.__race;
    const state = window.__landingState || "flying";

    if (!p) {
      this.el.textContent = "FLYING\nSelect a planet";
      return;
    }

    const m = p.getMetrics(race);
    const crowd = m.population / m.maxPop;

    this.el.textContent =
`PLANET ${p.name} — ${state.toUpperCase()}

Class: ${m.class}
Habitability: ${(m.habitability * 100).toFixed(1)}%

Population: ${fmt(m.population)} / ${fmt(m.maxPop)}
Crowding: ${crowd > 1 ? "OVERCROWDED" : crowd > 0.9 ? "HIGH" : "OK"}

Resources: ${fmt(m.resources)}

Installations:
  Factories: ${m.installations.factories}
  Mines:     ${m.installations.mines}

Build Queue:
  +Factories [F]: ${m.queue.factories}
  +Mines     [M]: ${m.queue.mines}

Terraforming [T]: ${m.queue.terraform ? "ACTIVE" : "OFF"}

Environment:
  Gravity ${m.env.gravity}
  Temp    ${m.env.temp}
  Rad     ${m.env.rad}

(Orders execute at year end)`;
  }
}

function fmt(n) {
  return n.toLocaleString();
}
