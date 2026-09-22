// Escopo exclusivo deste projeto; nenhum cache de outros sites é removido.
const PREFIX = 'sermaoiels-v2-';
const CACHE = PREFIX + '20260922-1';
const ROOT = new URL('./', self.location.href);
const INDEX = new URL('index.html', ROOT).href;
const FILES = ['index.html','styles.css','core.js','app.js','manifest.json','background.webp','background-mobile.webp','logoesperanca.png','icon-192.png','icon-512.png'].map(p => new URL(p,ROOT).href);
self.addEventListener('install',event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(FILES)));
});
self.addEventListener('activate',event => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) if (key.startsWith(PREFIX) && key !== CACHE) await caches.delete(key);
    await self.clients.claim();
  })());
});
self.addEventListener('fetch',event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== ROOT.origin || !url.pathname.startsWith(ROOT.pathname)) return;
  const isIndex = url.pathname === ROOT.pathname || url.pathname === new URL(INDEX).pathname;
  const key = isIndex ? INDEX : url.origin + url.pathname;
  if (!FILES.includes(key)) return;
  // Rede primeiro: novos cadastros aparecem no próximo acesso online.
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(),6000);
    try {
      const response = await fetch(event.request,{cache:'no-cache',signal:controller.signal});
      if (response.ok) {await cache.put(key,response.clone());return response;}
      return (await cache.match(key)) || response;
    } catch {
      return (await cache.match(key)) || new Response('Conteúdo indisponível sem conexão.',{status:503,headers:{'Content-Type':'text/plain; charset=utf-8'}});
    } finally {clearTimeout(timer);}
  })());
});
