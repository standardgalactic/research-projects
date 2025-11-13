// mediator.js – Lab 02: Mediator stratum toy

(function () {
  const canvas = document.getElementById('medCanvas');
  const ctx = canvas.getContext('2d');

  const lmSlider = document.getElementById('lmSlider');
  const muSlider = document.getElementById('muSlider');
  const mdSlider = document.getElementById('mdSlider');
  const lmVal = document.getElementById('lmVal');
  const muVal = document.getElementById('muVal');
  const mdVal = document.getElementById('mdVal');
  const pulseBtn = document.getElementById('pulseBtn');
  const clearBtn = document.getElementById('clearBtn');

  let lm = 0.6;
  let mu = 0.4;
  let md = 0.8;

  let state = [0, 0, 0]; // [lower, mediator, upper]
  let t = 0;

  function updateParams() {
    lm = parseInt(lmSlider.value, 10) / 100;
    mu = parseInt(muSlider.value, 10) / 100;
    md = parseInt(mdSlider.value, 10) / 100;
    lmVal.textContent = lm.toFixed(2);
    muVal.textContent = mu.toFixed(2);
    mdVal.textContent = md.toFixed(2);
  }

  lmSlider.addEventListener('input', updateParams);
  muSlider.addEventListener('input', updateParams);
  mdSlider.addEventListener('input', updateParams);

  pulseBtn.addEventListener('click', () => {
    state[0] = 1.0; // pulse at lower
  });

  clearBtn.addEventListener('click', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    state = [0, 0, 0];
    t = 0;
  });

  updateParams();

  function step() {
    const [L, M, U] = state;

    const newL = L * 0.5;
    const newM = md * (M + lm * L);
    const newU = 0.9 * (U + mu * M);

    state = [newL, newM, newU];
    t += 1;
  }

  function draw() {
    const colWidth = 4;
    const x = (t % (canvas.width / colWidth)) * colWidth;
    if (x === 0) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    const heights = [2, 1, 0]; // row index (y bands)
    const bandHeight = canvas.height / 3.0;

    for (let i = 0; i < 3; i++) {
      const v = Math.max(0, Math.min(1, state[i]));
      const g = Math.floor(40 + v * 215);
      ctx.fillStyle = `rgb(0, ${g}, 60)`;
      const y = heights[i] * bandHeight;
      ctx.fillRect(x, y, colWidth, bandHeight);
    }
  }

  function loop() {
    step();
    draw();
    requestAnimationFrame(loop);
  }

  requestAnimationFrame(loop);
})();
