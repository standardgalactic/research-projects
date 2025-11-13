// plenum_oscillator.js – Lab 07
(function(){
  const canvas = document.getElementById('oscCanvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');

  const kSlider = document.getElementById('oscK');
  const etaSlider = document.getElementById('oscEta');
  const noiseSlider = document.getElementById('oscNoise');
  const kVal = document.getElementById('oscKVal');
  const etaVal = document.getElementById('oscEtaVal');
  const noiseVal = document.getElementById('oscNoiseVal');
  const resetBtn = document.getElementById('oscReset');
  const logDiv = document.getElementById('oscLog');

  let k = 1.0;
  let eta = 0.3;
  let noiseAmp = 0.2;
  let phi = 0.0;
  let vel = 0.0;
  let t = 0;
  const maxT = canvas.width;

  function log(msg){
    const d = document.createElement('div');
    d.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    logDiv.appendChild(d);
    logDiv.scrollTop = logDiv.scrollHeight;
  }

  function updateParams(){
    k = parseInt(kSlider.value,10)/100;
    eta = parseInt(etaSlider.value,10)/100;
    noiseAmp = parseInt(noiseSlider.value,10)/100;
    kVal.textContent = k.toFixed(2);
    etaVal.textContent = eta.toFixed(2);
    noiseVal.textContent = noiseAmp.toFixed(2);
  }

  kSlider.addEventListener('input', updateParams);
  etaSlider.addEventListener('input', updateParams);
  noiseSlider.addEventListener('input', updateParams);
  updateParams();

  resetBtn.addEventListener('click',()=>{
    phi = 0.0;
    vel = 0.0;
    t = 0;
    ctx.clearRect(0,0,canvas.width,canvas.height);
    log('oscillator reset');
  });

  function step(){
    const dt = 0.03;
    const acc = -eta*vel - k*phi + (Math.random()-0.5)*noiseAmp;
    vel += acc*dt;
    phi += vel*dt;
    t += 1;
    if(t>maxT){
      t = 0;
      ctx.clearRect(0,0,canvas.width,canvas.height);
    }
  }

  function render(){
    const x = t;
    const mid = canvas.height/2;
    const scale = (canvas.height/2) * 0.8;
    const y = mid - phi*scale;
    ctx.fillStyle = '#66ffcc';
    ctx.fillRect(x,y,1,1);
  }

  function loop(){
    step();
    render();
    requestAnimationFrame(loop);
  }

  log('plenum oscillator initialized');
  requestAnimationFrame(loop);
})();
