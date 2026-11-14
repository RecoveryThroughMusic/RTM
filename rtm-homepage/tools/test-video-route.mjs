import { readFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
const source = await readFile(new URL('../functions/media/RTM-website.mp4.js', import.meta.url),'utf8');
const { onRequest } = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
const bytes = new TextEncoder().encode('0123456789');
const env = { RTM_MEDIA: { head: async () => ({size:10,httpEtag:'"test"'}), get: async (_, opts) => ({body:opts?.range ? bytes.slice(opts.range.offset,opts.range.offset+opts.range.length):bytes}) } };
async function check(method,range,status,body,extra={}) {
 const request=new Request('https://example.invalid/media/RTM-website.mp4',{method,headers:{...(range?{Range:range}:{}),...extra}});
 const response=await onRequest({request,env}); assert.equal(response.status,status); assert.equal(await response.text(),body);
 if(status===206) assert.match(response.headers.get('Content-Range'),/^bytes \d+-\d+\/10$/);
}
await check('GET',null,200,'0123456789');
await check('HEAD',null,200,'');
await check('GET','bytes=2-5',206,'2345');
await check('GET','bytes=7-',206,'789');
await check('GET','bytes=-3',206,'789');
await check('GET','bytes=0-999',206,'0123456789');
await check('GET','bytes=2-5',200,'0123456789',{'If-Range':'"old"'});
for(const range of ['bytes=10-','bytes=7-3','bytes=-0','bytes=0-1,4-5','bytes=-']) {
 const r=await onRequest({request:new Request('https://example.invalid',{headers:{Range:range}}),env});assert.equal(r.status,416);
}
assert.equal((await onRequest({request:new Request('https://example.invalid',{method:'POST'}),env})).status,405);
assert.equal((await onRequest({request:new Request('https://example.invalid'),env:{}})).status,503);
console.log('14 video route cases passed (mock R2; not a Cloudflare integration or playback test).');
