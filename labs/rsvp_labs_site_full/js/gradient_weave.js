// gradient_weave.js – Lab 05: Gradient Weave
(function(){
  const canvas = document.getElementById('gwCanvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;

  const COLS = 48;
  const ROWS = 32;
  const cellW = W / COLS;
  const cellH = H / ROWS;

  let Phi = new Float32Array(COLS*ROWS);
  let Vx  = new Float32Array(COLS*ROWS);
  let Vy  = new Float32Array(COLS*ROWS);

  const lambdaSlider = document.getElementById('gwLambda');
  const nuSlider     = document.getElementById('gwNu');
  const delaySlider  = document.getElementById('gwDelay');
  const lambdaVal    = document.getElementById('gwLambdaVal');
  const nuVal        = document.getElementById('gwNuVal');
  const delayVal     = document.getElementById('gwDelayVal');
  const logDiv       = document.getElementById('gwLog');
  const resetBtn     = document.getElementById('gwReset');
  const kickBtn      = document.getElementById('gwKick');

  let lambda = parseFloat(lambdaSlider.value);
  let nu     = parseFloat(nuSlider.value);
  let delaySteps = parseInt(delaySlider.value, 10);

  const idx = (x,y)=> y*COLS + x;

  function log(msg){
    const t = new Date().toLocaleTimeString();
    const line = document.createElement('div');
    line.textContent = `[${t}] ${msg}`;
    logDiv.appendChild(line);
    logDiv.scrollTop = logDiv.scrollHeight;
  }

  function clearFields(){
    Phi.fill(0);
    Vx.fill(0);
    Vy.fill(0);
  }

  function randomKick(){
    for(let n=0;n<40;n++){
      const x = Math.floor(Math.random()*COLS);
      const y = Math.floor(Math.random()*ROWS);
      const i = idx(x,y);
      Phi[i] += (Math.random()-0.5)*2.0;
      Vx[i]  += (Math.random()-0.5)*0.8;
      Vy[i]  += (Math.random()-0.5)*0.8;
    }
  }

  function divergenceV(x,y){
    let dx=0, dy=0;
    if(x>0 && x<COLS-1) dx = (Vx[idx(x+1,y)] - Vx[idx(x-1,y)])/(2*cellW);
    if(y>0 && y<ROWS-1) dy = (Vy[idx(x,y+1)] - Vy[idx(x,y-1)])/(2*cellH);
    return dx+dy;
  }

  function gradPhiFrom(arr,x,y){
    let gx=0, gy=0;
    if(x>0 && x<COLS-1) gx = (arr[idx(x+1,y)] - arr[idx(x-1,y)])/(2*cellW);
    if(y>0 && y<ROWS-1) gy = (arr[idx(x,y+1)] - arr[idx(x,y-1)])/(2*cellH);
    return [gx,gy];
  }

  const maxDelay = 60;
  const buffer = [];
  for(let i=0;i<maxDelay;i++){
    buffer.push(new Float32Array(COLS*ROWS));
  }
  let writePtr = 0;

  const dt = 0.03;
  let last = performance.now();

  function step(dt){
    buffer[writePtr].set(Phi);
    writePtr = (writePtr+1) % maxDelay;
    const d = Math.max(0, Math.min(maxDelay-1, delaySteps));
    const readPtr = (writePtr - d + maxDelay) % maxDelay;
    const PhiDelayed = buffer[readPtr];

    const newPhi = new Float32Array(COLS*ROWS);
    const newVx  = new Float32Array(COLS*ROWS);
    const newVy  = new Float32Array(COLS*ROWS);

    for(let y=0;y<ROWS;y++){
      for(let x=0;x<COLS;x++){
        const i = idx(x,y);
        const divV = divergenceV(x,y);
        newPhi[i] = Phi[i] + (-divV)*dt;

        const [gx,gy] = gradPhiFrom(PhiDelayed,x,y);
        const dvx = (-lambda*gx - nu*Vx[i])*dt;
        const dvy = (-lambda*gy - nu*Vy[i])*dt;
        newVx[i] = (Vx[i] + dvx)*0.999;
        newVy[i] = (Vy[i] + dvy)*0.999;
      }
    }

    Phi = newPhi;
    Vx  = newVx;
    Vy  = newVy;
  }

  function render(){
    const img = ctx.createImageData(W,H);
    for(let y=0;y<ROWS;y++){
      for(let x=0;x<COLS;x++){
        const i = idx(x,y);
        const v = Math.tanh(Phi[i]*0.4);
        const g = Math.floor((v*0.5+0.5)*255);
        const sx = Math.floor(x*cellW);
        const sy = Math.floor(y*cellH);
        for(let py=sy; py<sy+Math.ceil(cellH); py++){
          if(py<0 || py>=H) continue;
          for(let px=sx; px<sx+Math.ceil(cellW); px++){
            if(px<0 || px>=W) continue;
            const p = (py*W + px)*4;
            img.data[p] = 0;
            img.data[p+1] = g;
            img.data[p+2] = 40;
            img.data[p+3] = 255;
          }
        }
      }
    }
    ctx.putImageData(img,0,0);

    // draw arrows
    ctx.save();
    ctx.strokeStyle = 'rgba(0,255,160,0.9)';
    ctx.fillStyle   = 'rgba(0,255,160,0.9)';
    ctx.lineWidth   = 1;
    for(let y=2;y<ROWS-2;y+=3){
      for(let x=2;x<COLS-2;x+=3){
        const i = idx(x,y);
        const px = x*cellW + cellW/2;
        const py = y*cellH + cellH/2;
        const vx = Vx[i];
        const vy = Vy[i];
        const s = 10;
        const bx = px + vx*s;
        const by = py + vy*s;
        ctx.beginPath();
        ctx.moveTo(px,py);
        ctx.lineTo(bx,by);
        ctx.stroke();

        const ang = Math.atan2(by-py,bx-px);
        ctx.beginPath();
        ctx.moveTo(bx,by);
        ctx.lineTo(bx - 4*Math.cos(ang-0.4), by - 4*Math.sin(ang-0.4));
        ctx.lineTo(bx - 4*Math.cos(ang+0.4), by - 4*Math.sin(ang+0.4));
        ctx.closePath();
        ctx.fill();
      }
    }
    ctx.restore();
  }

  lambdaSlider.addEventListener('input',e=>{
    lambda = parseFloat(e.target.value);
    lambdaVal.textContent = lambda.toFixed(2);
  });
  nuSlider.addEventListener('input',e=>{
    nu = parseFloat(e.target.value);
    nuVal.textContent = nu.toFixed(2);
  });
  delaySlider.addEventListener('input',e=>{
    delaySteps = parseInt(e.target.value,10);
    delayVal.textContent = delaySteps.toString();
  });

  resetBtn.addEventListener('click',()=>{ clearFields(); log('reset fields'); });
  kickBtn.addEventListener('click',()=>{ randomKick(); log('random kick'); });

  clearFields();
  randomKick();
  log('gradient weave initialized');

  function loop(now){
    const dtNow = (now-last)/1000;
    last = now;
    let acc = dtNow;
    while(acc>0){
      const stepDt = Math.min(0.03, acc);
      step(stepDt);
      acc -= stepDt;
    }
    render();
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
})();
