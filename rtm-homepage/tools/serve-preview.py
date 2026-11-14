"""Loopback-only review server. Serves dist and the unchanged local video; no submissions."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import re
root=Path(__file__).resolve().parents[1]
class Preview(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root/'dist'),**kwargs)
 def do_GET(self):
  if urlsplit(self.path).path=='/media/RTM-website.mp4':self.video(False)
  else:super().do_GET()
 def do_HEAD(self):
  if urlsplit(self.path).path=='/media/RTM-website.mp4':self.video(True)
  else:super().do_HEAD()
 def video(self,head):
  file=root/'assets/video/RTM-website.mp4';size=file.stat().st_size;start=0;end=size-1
  value=self.headers.get('Range') if not head else None
  if value:
   match=re.fullmatch(r'bytes=(\d*)-(\d*)',value)
   if not match or not any(match.groups()):self.send_error(416);return
   start=int(match[1]) if match[1] else max(0,size-int(match[2]))
   end=min(int(match[2]),size-1) if match[1] and match[2] else size-1
   if start>end or start>=size:self.send_error(416);return
  self.send_response(206 if value else 200)
  self.send_header('Content-Type','video/mp4');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
  if value:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers()
  if not head:
   try:
    with file.open('rb') as stream:
     stream.seek(start);remaining=end-start+1
     while remaining:
      block=stream.read(min(65536,remaining))
      if not block:break
      self.wfile.write(block);remaining-=len(block)
   except (BrokenPipeError,ConnectionResetError):pass
print('Local review only: http://127.0.0.1:8766',flush=True)
ThreadingHTTPServer(('127.0.0.1',8766),Preview).serve_forever()
