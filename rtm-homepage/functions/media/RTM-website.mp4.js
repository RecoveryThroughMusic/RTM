// Private R2 bucket; only this approved object is addressable. No uploads or listings.
export async function onRequest({ request, env }) {
  const base = { 'Cache-Control': 'private, no-store', 'X-Robots-Tag': 'noindex', 'X-Content-Type-Options': 'nosniff' };
  const fail = (status, message, extra = {}) => new Response(message, { status, headers: { ...base, ...extra } });
  if (!['GET', 'HEAD'].includes(request.method)) return fail(405, 'Method not allowed', { Allow: 'GET, HEAD' });
  if (!env.RTM_MEDIA) return fail(503, 'Video is awaiting preview configuration.');
  try {
    const key = 'RTM-website.mp4';
    const meta = await env.RTM_MEDIA.head(key);
    if (!meta) return fail(404, 'Video unavailable.');
    const headers = new Headers({ ...base, 'Content-Type': 'video/mp4', 'Accept-Ranges': 'bytes', ETag: meta.httpEtag, 'Content-Length': String(meta.size) });
    if (request.method === 'HEAD') return new Response(null, { headers });
    let range;
    const rangeHeader = request.headers.get('range');
    const ifRange = request.headers.get('if-range');
    if (rangeHeader && (!ifRange || ifRange === meta.httpEtag)) {
      const match = /^bytes=(\d*)-(\d*)$/.exec(rangeHeader);
      if (!match || (!match[1] && !match[2])) return fail(416, 'Unsupported byte range.', { 'Content-Range': `bytes */${meta.size}` });
      const start = match[1] ? Number(match[1]) : Math.max(0, meta.size - Number(match[2]));
      const end = match[1] && match[2] ? Math.min(Number(match[2]), meta.size - 1) : meta.size - 1;
      if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start > end || start >= meta.size) return fail(416, 'Invalid byte range.', { 'Content-Range': `bytes */${meta.size}` });
      range = { offset: start, length: end - start + 1 };
      headers.set('Content-Range', `bytes ${start}-${end}/${meta.size}`);
      headers.set('Content-Length', String(range.length));
    }
    const object = await env.RTM_MEDIA.get(key, range ? { range } : undefined);
    if (!object) return fail(404, 'Video unavailable.');
    return new Response(object.body, { status: range ? 206 : 200, headers });
  } catch {
    // Do not reveal account/bucket details or log request contents.
    return fail(503, 'Video temporarily unavailable.');
  }
}
