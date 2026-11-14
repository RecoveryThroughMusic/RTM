const menu = document.querySelector('.menu');
const nav = document.querySelector('#navigation');
function closeMenu() { nav.classList.remove('open'); menu.setAttribute('aria-expanded', 'false'); }
menu.addEventListener('click', () => { const open = nav.classList.toggle('open'); menu.setAttribute('aria-expanded', String(open)); });
nav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => { if (event.key === 'Escape' && nav.classList.contains('open')) { closeMenu(); menu.focus(); } });
window.matchMedia('(min-width: 761px)').addEventListener('change', closeMenu);
// Native players are rendered only when real supplied recordings exist.
const recordings = [];
const container = document.querySelector('.recordings');
if (recordings.length) {
  container.replaceChildren();
  recordings.forEach(({ title, src }) => {
    const heading = document.createElement('h3'); heading.textContent = title;
    const audio = document.createElement('audio'); audio.controls = true; audio.preload = 'metadata'; audio.src = src; audio.setAttribute('aria-label', title); audio.style.width = '100%';
    audio.addEventListener('play', () => document.querySelectorAll('audio').forEach(other => { if (other !== audio) other.pause(); }));
    container.append(heading, audio);
  });
}
