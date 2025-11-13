// entropy.js – Lab 03: Entropy sink toy

(function () {
  const canvas = document.getElementById('entCanvas');
  const ctx = canvas.getContext('2d');

  const leakSlider = document.getElementById('leakSlider');
  const jitSlider = document.getElementById('jitSlider');
  const leakVal = document.getElementById('leakVal');
  const jitVal = document.getElementById('jitVal');
  const startBtn = document.getElementById('startBtn');
  const stopBtn = document.getElementById('stopBtn');
  const resetEBtn = document.getElementById('resetEBtn');

  let leak = 0.05;
  let jitter = 0.2;
  let E = 1.0;
  let running = false;
  let t = 0;
  const maxT = 300;

  function updateParams() {
    leak = parseInt(leakSlider.value, 10) / 1000 * 10; // 0 - 0.3 approx but scaled
    jitter = parseInt(jitSlider.value, 10) / 100;
    leakVal.textContent = leak.toFixed(2);
    jitVal.textContent = jitter.toFixed(2);
  }

  leakSlider.addEventListener('input', updateParams);
  jitSlider.addEventListener('input', updateParams);

  startBtn.addEventListener('click', () => { running = true; });
  stopBtn.addEventListener('click', () => { running = false; });
  resetEBtn.addEventListener('click', () => { E = 1.0; t = 0; clearCanvas(); });

  updateParams();

  function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#33ff99';
    ctx.strokeRect(0, 0, canvas.width, canvas.height);
  }

  clearCanvas();

  function step() {
    const noise = (Math.random() - 0.5) * jitter;
    E = Math.max(0, E * (1 - leak) + noise);
    if (!running) return;
    t += 1;
    if (t > maxT) {
      t = 0;
      clearCanvas();
    }
  }

  function draw() {
    if (!running) return;
    const x = (t / maxT) * canvas.width;
    const y = canvas.height - E * (canvas.height - 4) - 2;
    ctx.fillStyle = '#66ffcc';
    ctx.fillRect(x, y, 2, 2);
  }

  function loop() {
    step();
    draw();
    requestAnimationFrame(loop);
  }

  requestAnimationFrame(loop);
})();
