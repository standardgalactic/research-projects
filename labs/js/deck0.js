// deck0.js – Lab 06: Deck 0 Reservoir
(function(){
  const canvas = document.getElementById('d0Canvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');

  const leakSlider = document.getElementById('d0Leak');
  const backSlider = document.getElementById('d0Back');
  const leakVal = document.getElementById('d0LeakVal');
  const backVal = document.getElementById('d0BackVal');
  const toggleBtn = document.getElementById('d0Toggle');
  const resetBtn = document.getElementById('d0Reset');
  const logDiv = document.getElementById('d0Log');

  let E_vis = 1.0;
  let E_hidden = 0.0;
  let leak = 0.05;
  let backAmp = 0.2;
  let leakOn = true;
  let t = 0;
  const maxT = 360;

  function log(msg){
    const line = document.createElement('div');
    line.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    logDiv.appendChild(line);
    logDiv.scrollTop = logDiv.scrollHeight;
  }

  function updateParams(){
    leak = parseInt(leakSlider.value,10)/100 * 0.5; // 0-0.15
    backAmp = parseInt(backSlider.value,10)/100;
    leakVal.textContent = leak.toFixed(2);
    backVal.textContent = backAmp.toFixed(2);
  }

  leakSlider.addEventListener('input', updateParams);
  backSlider.addEventListener('input', updateParams);
  updateParams();

  toggleBtn.addEventListener('click',()=>{
    leakOn = !leakOn;
    toggleBtn.textContent = leakOn ? 'leak: on' : 'leak: off';
    log(`leak ${leakOn?'enabled':'disabled'}`);
  });

  resetBtn.addEventListener('click',()=>{
    E_vis = 1.0;
    E_hidden = 0.0;
    t = 0;
    ctx.clearRect(0,0,canvas.width,canvas.height);
    log('reset reservoirs');
  });

  function step(){
    const dt = 0.03;
    if(leakOn){
      const d = leak * E_vis * dt;
      E_vis -= d;
      E_hidden += d;
    }
    const back = (Math.random()-0.5) * backAmp * dt;
    const usableBack = Math.max(-E_hidden, back);
    E_hidden -= usableBack;
    E_vis += usableBack;

    if(E_vis<0) E_vis=0;
    if(E_hidden<0) E_hidden=0;

    t += 1;
    if(t>maxT){
      t = 0;
      ctx.clearRect(0,0,canvas.width,canvas.height);
    }
  }

  function render(){
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0,0,w,h);

    // Bars
    ctx.fillStyle = '#004422';
    ctx.fillRect(0,0,w,h);
    const barW_vis = Math.max(0, Math.min(w, E_vis*w));
    const barW_hid = Math.max(0, Math.min(w, E_hidden*w));

    ctx.fillStyle = '#33ff99';
    ctx.fillRect(0,10, barW_vis, 30);
    ctx.fillStyle = '#228866';
    ctx.fillRect(0,h-40, barW_hid, 30);

    ctx.fillStyle = '#b9ffb9';
    ctx.font = '10px Courier New';
    ctx.fillText('visible', 4, 8+10);
    ctx.fillText('deck 0', 4, h-40+20);

    // Time trace of E_vis
    const x = (t/maxT)*w;
    const y = h/2 - E_vis*(h/2-10);
    ctx.fillStyle = '#66ffcc';
    ctx.fillRect(x,y,2,2);
  }

  function loop(){
    step();
    render();
    requestAnimationFrame(loop);
  }
  log('deck 0 reservoir initialized');
  requestAnimationFrame(loop);
})();
