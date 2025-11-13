// ethical_gradient.js – Lab 08
(function(){
  const canvas = document.getElementById('egCanvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;

  const skewSlider = document.getElementById('egSkew');
  const noiseSlider = document.getElementById('egNoise');
  const lrSlider = document.getElementById('egLR');
  const skewVal = document.getElementById('egSkewVal');
  const noiseVal = document.getElementById('egNoiseVal');
  const lrVal = document.getElementById('egLRVal');
  const resetBtn = document.getElementById('egReset');
  const logDiv = document.getElementById('egLog');

  let s = 0.5;
  let noiseAmp = 0.2;
  let alpha = 0.1;

  let x = 0;
  let y = 0;

  function log(msg){
    const d = document.createElement('div');
    d.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    logDiv.appendChild(d);
    logDiv.scrollTop = logDiv.scrollHeight;
  }

  function updateParams(){
    s = parseInt(skewSlider.value,10)/100;
    noiseAmp = parseInt(noiseSlider.value,10)/100;
    alpha = parseInt(lrSlider.value,10)/100;
    skewVal.textContent = s.toFixed(2);
    noiseVal.textContent = noiseAmp.toFixed(2);
    lrVal.textContent = alpha.toFixed(2);
  }

  skewSlider.addEventListener('input', updateParams);
  noiseSlider.addEventListener('input', updateParams);
  lrSlider.addEventListener('input', updateParams);
  updateParams();

  function resetPos(){
    x = (Math.random()-0.5)*2.5;
    y = (Math.random()-0.5)*2.5;
  }

  resetBtn.addEventListener('click', ()=>{ resetPos(); log('agent reset'); });
  resetPos();

  function U(x,y){
    return 0.5*(x*x+y*y) + s*x;
  }
  function gradU(x,y){
    return [x + s, y];
  }

  function toScreen(px,py){
    const sx = (px+2.5)/5 * W;
    const sy = (1 - (py+2.5)/5) * H;
    return [sx,sy];
  }

  function drawField(){
    const img = ctx.createImageData(W,H);
    const sampleStep = 2;
    for(let sy=0; sy<H; sy+=sampleStep){
      for(let sx=0; sx<W; sx+=sampleStep){
        const px = (sx/W)*5 - 2.5;
        const py = (1 - sy/H)*5 - 2.5;
        const v = U(px,py);
        const t = 1/(1+Math.exp(v)); // logistic compress
        const g = Math.floor(t*255);
        for(let dy=0; dy<sampleStep; dy++){
          for(let dx=0; dx<sampleStep; dx++){
            const ix = sx+dx;
            const iy = sy+dy;
            if(ix>=W || iy>=H) continue;
            const p = (iy*W + ix)*4;
            img.data[p] = 0;
            img.data[p+1] = g;
            img.data[p+2] = 40;
            img.data[p+3] = 255;
          }
        }
      }
    }
    ctx.putImageData(img,0,0);
  }

  function step(){
    const [gx,gy] = gradU(x,y);
    const nx = (Math.random()-0.5)*noiseAmp;
    const ny = (Math.random()-0.5)*noiseAmp;
    x -= alpha*gx + nx;
    y -= alpha*gy + ny;
  }

  function render(){
    drawField();
    const [sx,sy] = toScreen(x,y);
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(sx,sy,4,0,Math.PI*2);
    ctx.fill();
  }

  function loop(){
    step();
    render();
    requestAnimationFrame(loop);
  }

  log('ethical gradient initialized');
  requestAnimationFrame(loop);
})();
