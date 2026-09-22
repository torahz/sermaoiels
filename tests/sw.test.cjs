const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const handlers={}, stores=new Map([['outro-site-v1',new Map()],['sermaoiels-v2-antigo',new Map()]]);
const scope='https://example.test/sermaoiels/';
let requests=[],offline=false,body='novo';
const caches={
  keys:async()=>[...stores.keys()],delete:async key=>stores.delete(key),
  open:async key=>{
    if(!stores.has(key))stores.set(key,new Map());const store=stores.get(key);
    return {addAll:async urls=>{requests=urls;urls.forEach(u=>store.set(u,new Response('inicial')));},put:async(k,v)=>store.set(k,v),match:async k=>store.get(k)?.clone()};
  }
};
const sandbox={self:{location:{href:scope+'sw.js'},addEventListener:(k,f)=>handlers[k]=f,clients:{claim:async()=>{}}},caches,URL,Response,AbortController,setTimeout,clearTimeout,fetch:async()=>{if(offline)throw new Error('offline');return new Response(body);}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../sw.js'),'utf8'),sandbox);
async function runEvent(type){let promise;handlers[type]({waitUntil:p=>promise=p});await promise;}
async function request(url){let promise;handlers.fetch({request:{url,method:'GET'},respondWith:p=>promise=p});return promise?await (await promise).text():null;}
(async()=>{
  await runEvent('install');assert.equal(requests.length,10);assert.ok(requests.every(u=>u.startsWith(scope)));
  await runEvent('activate');assert.ok(stores.has('outro-site-v1'));assert.ok(!stores.has('sermaoiels-v2-antigo'));
  assert.equal(await request(scope+'?ano=2026'),'novo');
  offline=true;assert.equal(await request(scope+'?ano=2025'),'novo');assert.equal(await request(scope+'index.html?sermao=x'),'novo');
  assert.equal(await request('https://drive.google.com/file/d/x/view'),null);
  assert.equal(await request(scope+'backups/index-antigo.html'),null);
  offline=false;body='atualizado';assert.equal(await request(scope),'atualizado');
  console.log('PWA: caminhos, atualização, fallback offline e isolamento de cache OK.');
})().catch(e=>{console.error(e);process.exitCode=1;});
