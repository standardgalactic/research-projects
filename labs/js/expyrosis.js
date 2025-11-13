// expyrosis.js – Lab 10
(function(){
  const canvas = document.getElementById('exCanvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;

  const freezeSlider = document.getElementById('exFreeze');
  const seedSlider = document.getElementById('exSeed');
  const freezeVal = document.getElementById('exFreezeVal');
  const seedVal = document.getElementById('exSeedVal');
  const resetBtn = document.getElementById('exReset');
  const logDiv = document.getElementById('exLog');

  const N = 120;
  let x = new Float32Array(N);
  let y = new Float32Array(N);
  let vx = new Float32Array(N);
  let vy = new Float32Array(N);

  let freezeRate = 0.02;
  let seedAmp = 1.0;

  function log(msg){
    const d = document.createElement('div');
    d.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    logDiv.appendChild(d);
    logDiv.scrollTop = logDiv.scrollHeight;
  }

  function updateParams(){
    freezeRate = parseInt(freezeSlider.value,10)/100;
    seedAmp = parseInt(seedSlider.value,10)/100;
    freezeVal.textContent = freezeRate.toFixed(2);
    seedVal.textContent = seedAmp.toFixed(2);
  }

  freezeSlider.addEventListener('input', updateParams);
  seedSlider.addEventListener('input', updateParams);
  updateParams();

  function initPoints(){
    for(let i=0;i<N;i++){
      x[i] = Math.random()*W;
      y[i] = Math.random()*H;
      vx[i] = (Math.random()-0.5)*2;
      vy[i] = (Math.random()-0.5)*2;
    }
  }

  resetBtn.addEventListener('click',()=>{
    initPoints();
    log('system reset');
  });

  initPoints();

  function step(){
    const dt = 0.05;
    let KE = 0;
    for(let i=0;i<N;i++){
      // freeze friction
      vx[i] *= (1 - freezeRate*dt);
      vy[i] *= (1 - freezeRate*dt);

      x[i] += vx[i];
      y[i] += vy[i];

      if(x[i]<0) x[i]+=W;
      if(x[i]>=W) x[i]-=W;
      if(y[i]<0) y[i]+=H;
      if(y[i]>=H) y[i]-=H;

      KE += 0.5*(vx[i]*vx[i] + vy[i]*vy[i]);
    }

    // Expyrotic reset: if kinetic energy too low, kick one point
    const threshold = 5;
    if(KE < threshold){
      const j = Math.floor(Math.random()*N);
      vx[j] += (Math.random()-0.5)*seedAmp*4;
      vy[j] += (Math.random()-0.5)*seedAmp*4;
      log('frozen → seed kick');
    }
  }

  function render(){
    ctx.fillStyle = '#000000';
    ctx.fillRect(0,0,W,H);
    ctx.fillStyle = '#66ffcc';
    for(let i=0;i<N;i++){
      ctx.fillRect(x[i],y[i],2,2);
    }
  }

  function loop(){
    step();
    render();
    requestAnimationFrame(loop);
  }

  log('expyrosis reset initialized');
  requestAnimationFrame(loop);
})();
