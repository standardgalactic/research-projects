// semantic_horizon.js – Lab 09
(function(){
  const canvas = document.getElementById('shCanvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;
  const cx = W/2;
  const cy = H/2;
  const R = Math.min(W,H)/2 - 10;

  const sigSlider = document.getElementById('shSig');
  const dampSlider = document.getElementById('shDamp');
  const sigVal = document.getElementById('shSigVal');
  const dampVal = document.getElementById('shDampVal');
  const pulseBtn = document.getElementById('shPulse');
  const resetBtn = document.getElementById('shReset');
  const logDiv = document.getElementById('shLog');

  const N = 128;
  let phi = new Float32Array(N);
  let sigma = 0.2;
  let alpha = 0.05;

  function log(msg){
    const d = document.createElement('div');
    d.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    logDiv.appendChild(d);
    logDiv.scrollTop = logDiv.scrollHeight;
  }

  function updateParams(){
    sigma = parseInt(sigSlider.value,10)/100;
    alpha = parseInt(dampSlider.value,10)/100;
    sigVal.textContent = sigma.toFixed(2);
    dampVal.textContent = alpha.toFixed(2);
  }

  sigSlider.addEventListener('input', updateParams);
  dampSlider.addEventListener('input', updateParams);
  updateParams();

  pulseBtn.addEventListener('click',()=>{
    phi[0] += 1.0;
    log('center pulse emitted');
  });

  resetBtn.addEventListener('click',()=>{
    phi.fill(0);
    ctx.clearRect(0,0,W,H);
    log('field reset');
  });

  function step(){
    const dt = 0.03;
    const newPhi = new Float32Array(N);
    for(let i=0;i<N;i++){
      let lap = -2*phi[i];
      const left = (i===0 ? phi[1] : phi[i-1]);
      const right = (i===N-1 ? phi[N-2] : phi[i+1]);
      lap += left + right;
      newPhi[i] = phi[i] + (sigma*lap - alpha*phi[i])*dt;
    }
    phi = newPhi;
  }

  function render(){
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle = '#001010';
    ctx.fillRect(0,0,W,H);

    for(let i=0;i<N;i++){
      const theta = (i/N)*Math.PI*2;
      const v = Math.max(0, Math.min(1, phi[i]+0.5));
      const g = Math.floor(v*255);
      const x = cx + R*Math.cos(theta);
      const y = cy + R*Math.sin(theta);
      ctx.fillStyle = `rgb(0,${g},80)`;
      ctx.beginPath();
      ctx.arc(x,y,3,0,Math.PI*2);
      ctx.fill();
    }
  }

  function loop(){
    step();
    render();
    requestAnimationFrame(loop);
  }

  log('semantic horizon initialized');
  requestAnimationFrame(loop);
})();
