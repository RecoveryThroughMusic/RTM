"""Local packaging only. Does not contact Cloudflare or publish anything."""
from pathlib import Path
import shutil, re, hashlib, json, datetime
root=Path(__file__).resolve().parents[1]
prep=root.parent/'publication-preparation'
prep.mkdir(exist_ok=True)
out=root/'dist'
if out.exists():
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    shutil.move(str(out), str(prep/('previous-dist-'+stamp)))
out.mkdir()
pages=['index.html','about.html','what-we-do.html','our-music.html','from-the-room.html','get-involved.html','living-journal-preview.html']
for name in pages:
    text=(root/name).read_text()
    if name!='living-journal-preview.html':
        text=re.sub(r'<p class="prototype-note">.*?</p>', '', text, flags=re.S)
        text=text.replace('<p>Local review prototype · Not published</p>', '')
        text=text.replace('href="index.html#involved">Get Involved', 'href="get-involved.html">Get Involved')
        text=text.replace('href="#involved">Get Involved', 'href="get-involved.html">Get Involved')
    else:
        text=text.replace('The Living Journal — RTM preview','The Living Journal — Recovery Through Music')
        text=text.replace(' <small> / experimental spread</small>','')
        text=text.replace('<p class="draft-status">Local draft · permissions pending for spread two</p>','')
        # Approved notebook articles, styles, scripts and media are not transformed.
    if name=='index.html':
        text=text.replace('assets/video/RTM-website.mp4','/media/RTM-website.mp4')
        for number,anchor in [('01','join-in'),('02','refer-someone'),('03','work-with-rtm'),('04','support-rtm')]:
            text=text.replace('href="#contact"'+(' id="support"' if number=='04' else '')+'><span>'+number,
                              'href="get-involved.html#'+anchor+'"'+(' id="support"' if number=='04' else '')+'><span>'+number)
    if name=='get-involved.html':
        # Source forms remain intact for later development; never ship hidden fields.
        text=re.sub(r'<form\b.*?</form>', '', text, flags=re.S)
        text=re.sub(r'<span class="text-link invitation-action invitation-pending".*?</span>', '', text, flags=re.S)
        text=text.replace('Tell us a little about the person, what has brought you to RTM, and anything that might help us make their first contact easier.', 'Please contact us first to discuss how to make an introduction. Do not send sensitive personal information by email.')
    text=text.replace('</head>','<meta name="robots" content="noindex, nofollow"><meta http-equiv="Content-Security-Policy" content="form-action \'none\'; object-src \'none\'; base-uri \'self\'"></head>')
    (out/name).write_text(text)
for pattern in ['*.css','*.js','favicon.svg']:
    for source in root.glob(pattern): shutil.copy2(source,out/source.name)
# Only referenced assets are shipped, not unused mock-ups, reference sheets or backups.
pending=list(out.glob('*.html'))+list(out.glob('*.css'))+list(out.glob('*.js'))
assets=set()
from urllib.parse import unquote
from html import unescape
for file in pending:
    for rel in re.findall(r'''assets/[^"<>\n]+?\.(?:png|jpe?g|svg|webp|mp3|mpeg|mp4)(?=["')])''',file.read_text()):
        rel=unquote(unescape(rel))
        if rel.startswith('assets/video/'): continue
        assets.add(rel)
for rel in sorted(assets):
    source=root/rel
    if not source.is_file(): raise RuntimeError('Missing asset: '+rel)
    target=out/rel; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target)
(out/'_headers').write_text("/*\n  X-Robots-Tag: noindex, nofollow\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Content-Security-Policy: form-action 'none'; frame-ancestors 'none'; object-src 'none'; base-uri 'self'\n")
(out/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
(out/'404.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Page not found — RTM</title><h1>Page not found</h1><p><a href="/">Return to Recovery Through Music</a></p></html>')
(out/'_routes.json').write_text(json.dumps({'version':1,'include':['/media/RTM-website.mp4'],'exclude':[]}))
video=root/'assets/video/RTM-website.mp4'
r2=prep/'r2-upload'; r2.mkdir(exist_ok=True)
shutil.copy2(video,r2/video.name)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(video)==digest(r2/video.name)
manifest={str(p.relative_to(out)):{'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(out.rglob('*')) if p.is_file()}
assert all(v['bytes']<=25*1024*1024 for v in manifest.values())
(prep/'build-manifest.json').write_text(json.dumps(manifest,indent=2))
(prep/'r2-upload-manifest.json').write_text(json.dumps({'key':video.name,'contentType':'video/mp4','bytes':video.stat().st_size,'sha256':digest(video),'binding':'RTM_MEDIA','publicAccess':False},indent=2))
print(f'Local build: {len(manifest)} files; {len(assets)} referenced assets. Video staged separately and checksum verified. Nothing uploaded.')
