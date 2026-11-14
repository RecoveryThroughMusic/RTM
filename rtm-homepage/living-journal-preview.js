// Each .notebook is an independent spread; fragment buttons reuse this viewer.
const viewer=document.querySelector('.fragment-view');
const detail=viewer.querySelector('.fragment-detail');
let origin;
document.querySelectorAll('.fragment').forEach(button=>button.addEventListener('click',()=>{origin=button;detail.replaceChildren(button.querySelector('svg').cloneNode(true));viewer.showModal();}));
viewer.querySelector('.close-view').addEventListener('click',()=>viewer.close());
viewer.addEventListener('click',event=>{if(event.target===viewer){const r=viewer.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)viewer.close();}});
viewer.addEventListener('close',()=>origin?.focus());

// The original spread remains untouched; this controller switches sibling articles.
const stage=document.querySelector('.journal-stage');
const spreads=[...stage.querySelectorAll(':scope > .notebook')];
const previous=document.querySelector('.previous-spread');
const next=document.querySelector('.next-spread');
const status=document.querySelector('.spread-status');
const hint=document.querySelector('.journal-hint');
let current=0,turning=false;
function controls(){previous.disabled=turning||current===0;next.disabled=turning||current===spreads.length-1;status.textContent=`Spread ${current+1} of ${spreads.length}`;hint.hidden=current!==0;}
async function turnTo(target){
 if(turning||target<0||target>=spreads.length||target===current)return;
 turning=true;controls();
 const old=spreads[current],incoming=spreads[target],forward=target>current;
 old.querySelectorAll('audio').forEach(audio=>audio.pause());
 if(viewer.open)viewer.close();
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const mobile=matchMedia('(max-width:700px)').matches;
 let leaf;
 if(!reduced&&!mobile){
  leaf=document.createElement('div');leaf.className=`turning-leaf ${forward?'forward':'backward'}`;leaf.setAttribute('aria-hidden','true');leaf.inert=true;
  for(const [name,page] of [['front',old.children[forward?1:0]],['back',incoming.children[forward?0:1]]]){
   const face=document.createElement('div');face.className=`turn-face ${name}`;const copy=page.cloneNode(true);
   copy.querySelectorAll('[id]').forEach(el=>el.removeAttribute('id'));copy.querySelectorAll('audio').forEach(el=>el.remove());face.append(copy);leaf.append(face);
  }
  stage.append(leaf);
 }
 old.hidden=true;incoming.hidden=false;
 try{
  if(leaf)await leaf.animate([{transform:'rotateY(0deg)'},{transform:`rotateY(${forward?'-':''}180deg)`}],{duration:950,easing:'cubic-bezier(.25,.65,.25,1)',fill:'forwards'}).finished;
  else if(!reduced)await incoming.animate([{opacity:.4,transform:'translateX(8px)'},{opacity:1,transform:'translateX(0)'}],{duration:260,easing:'ease-out'}).finished;
 }finally{leaf?.remove();current=target;turning=false;controls();if(document.activeElement?.disabled)(current===0?next:previous).focus();}
}
previous.addEventListener('click',()=>turnTo(current-1));next.addEventListener('click',()=>turnTo(current+1));

// Progressive enhancement: retain native audio controls if this setup is unavailable.
const recording=document.querySelector('#paul-recording');
const inkPlayer=document.querySelector('.ink-player');
const playButton=inkPlayer.querySelector('.ink-play');
const seek=inkPlayer.querySelector('.ink-seek');
const elapsed=inkPlayer.querySelector('.elapsed');
const durationLabel=inkPlayer.querySelector('.duration');
const audioMessage=document.querySelector('.audio-message');
function clockTime(seconds){if(!Number.isFinite(seconds))return '—:—';const whole=Math.max(0,Math.floor(seconds));return `${Math.floor(whole/60)}:${String(whole%60).padStart(2,'0')}`;}
function syncAudio(){
 const duration=Number.isFinite(recording.duration)&&recording.duration>0?recording.duration:0;
 const time=Number.isFinite(recording.currentTime)?recording.currentTime:0;
 seek.disabled=!duration;seek.max=String(duration);seek.value=String(time);
 seek.style.setProperty('--progress',`${duration?Math.min(100,time/duration*100):0}%`);
 seek.setAttribute('aria-valuetext',`${clockTime(time)} of ${clockTime(duration||NaN)}`);
 elapsed.textContent=clockTime(time);durationLabel.textContent=clockTime(duration||NaN);
 const playing=!recording.paused&&!recording.ended;
 playButton.dataset.playing=String(playing);playButton.setAttribute('aria-label',`${playing?'Pause':'Play'} What Makes You Tick`);
}
playButton.addEventListener('click',async()=>{
 audioMessage.textContent='';
 if(!recording.paused&&!recording.ended){recording.pause();return;}
 try{if(recording.ended)recording.currentTime=0;await recording.play();}
 catch{audioMessage.textContent='Unable to play the recording. Please try again.';syncAudio();}
});
seek.addEventListener('input',()=>{if(Number.isFinite(recording.duration)&&recording.duration>0){recording.currentTime=Math.min(recording.duration,Math.max(0,Number(seek.value)));syncAudio();}});
['loadedmetadata','durationchange','timeupdate','play','pause','ended','emptied','seeked'].forEach(event=>recording.addEventListener(event,syncAudio));
recording.addEventListener('error',()=>{audioMessage.textContent='The recording could not be loaded. Please reload the preview and try again.';syncAudio();});
syncAudio();recording.controls=false;recording.hidden=true;inkPlayer.hidden=false;
