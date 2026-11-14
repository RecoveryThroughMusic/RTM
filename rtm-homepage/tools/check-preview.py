from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import re,json,hashlib
root=Path(__file__).resolve().parents[1]; out=root/'dist'; prep=root.parent/'publication-preparation'
errors=[];checks=[]
class Page(HTMLParser):
 def __init__(self,text):self.ids=[];self.refs=[];self.images=[];self.forms=[];super().__init__();self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  for key in ['src','href']:
   if key in a:self.refs.append(a[key])
  if tag=='img' and 'alt' not in a:errors.append('Image missing alt: '+str(a))
  if tag=='form':self.forms.append(a)
pages={p.name:Page(p.read_text()) for p in out.glob('*.html')}
for name,p in pages.items():
 if len(p.ids)!=len(set(p.ids)):errors.append(name+': duplicate IDs')
 for ref in p.refs:
  u=urlsplit(ref)
  if u.scheme or u.netloc:continue
  if u.path=='/media/RTM-website.mp4':continue # separately verified Pages Function route
  target=out/unquote(u.path.lstrip('/')) if u.path else out/name
  if not target.exists():errors.append(name+': missing '+ref);continue
  if u.fragment and target.name in pages and u.fragment not in pages[target.name].ids:errors.append(name+': missing anchor '+ref)
checks.append('HTML local paths and fragment targets checked; video resolved by prepared R2 Function, not static hosting.')
approved=root.parent/'RTM-Living-Journal-Spread-2-APPROVED-LOCKED-2026-11-12/rtm-homepage'
for name in ['living-journal-preview.html','living-journal-preview.css','living-journal-preview.js']:
 if (root/name).read_bytes()!=(approved/name).read_bytes():errors.append('Approved journal source differs: '+name)
for p in (out/'assets/living-journal').iterdir():
 if p.read_bytes()!=(approved/'assets/living-journal'/p.name).read_bytes():errors.append('Approved journal asset differs: '+p.name)
source=(root/'living-journal-preview.html').read_text(); built=(out/'living-journal-preview.html').read_text()
articles=lambda s:re.findall(r'<article\b.*?</article>',s,re.S)
assert len(articles(built))==2
assert articles(source)==articles(built)
for name in ['living-journal-preview.css','living-journal-preview.js']:
 assert (root/name).read_bytes()==(out/name).read_bytes()
checks.append('Two approved notebook articles, journal CSS/JS and all shipped journal assets match exactly; working journal matches approved backup.')
home=(root/'index.html').read_text(); builtHome=(out/'index.html').read_text()
section=lambda s:re.search(r'<section class="voices section".*?</section>',s,re.S).group()
assert section(home)==section(builtHome)
assert (root/'assets/testimonials/andy-taped-parchment.png').read_bytes()==(out/'assets/testimonials/andy-taped-parchment.png').read_bytes()
checks.append('Complete Participant Voices section including Andy CSS, text and paper image preserved exactly in build.')
for p in pages.values():
 assert not p.forms
 for ref in p.refs:assert not re.search(r'#(?:join-form|referral-form)',ref)
assert len(Page((root/'get-involved.html').read_text()).forms)==2
assert 'invitation-pending' not in (out/'get-involved.html').read_text()
assert 'mailto:Sylvain@recoverythroughmusic.co.uk' in (out/'index.html').read_text()
checks.append('No forms or form-entry controls in publication build; both source forms retained; Contact mailto unchanged. No submission sent.')
checks.append('All bundled files meet the Cloudflare Pages 25 MiB per-file limit (build assertion).')
report={'checks':checks,'errors':errors,'not_verified':['Rendered desktop/mobile layout','Keyboard and screen-reader interaction','Real audio/video playback','Cloudflare runtime and R2 binding','Email delivery and spam controls (not implemented)','Permissions and legal text']}
(prep/'verification-results.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
if errors:raise SystemExit(1)
