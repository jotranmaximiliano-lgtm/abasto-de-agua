"""Arma la app web instalable (para iPhone, y también sirve en Android) de Abasto de agua.

Uso:
  python construir-web.py          # usa la misma versión que la app Android
  python construir-web.py 1.1      # con otra versión

Deja la carpeta web-abasto/ lista para publicarse tal cual (Netlify, arrastrando la carpeta).
En el iPhone se abre la dirección en Safari → Compartir → «Agregar a inicio».
"""
import hashlib, json, pathlib, re, shutil, subprocess, sys

AQUI = pathlib.Path(__file__).resolve().parent
ICONOS = AQUI / 'iconos'
SALIDA = AQUI / 'web-abasto'

def main():
    g = (AQUI / 'android-abasto' / 'android' / 'app' / 'build.gradle').read_text(encoding='utf-8')
    version = sys.argv[1] if len(sys.argv) > 1 else re.search(r'versionName "([^"]+)"', g).group(1)
    subprocess.run([sys.executable, 'construir-abasto.py'], cwd=AQUI, check=True)
    html = (AQUI / 'app-abasto' / 'index.html').read_text(encoding='utf-8')
    html = html.replace('window.AB_APP = true;', f'window.AB_APP = true; window.AB_WEB = true; window.AB_VERSION = {version!r};', 1)
    html = html.replace('<meta name="theme-color" content="#C3132B">', '''<meta name="theme-color" content="#C3132B">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" href="favicon-64.png">
<link rel="apple-touch-icon" href="icono-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">''', 1)
    html = html.replace('\n</body>', '''
<script>
/* Guarda la app en el teléfono para que abra sin señal; cada versión nueva se descarga sola al abrirla con señal */
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
</script>
</body>''', 1)

    if SALIDA.exists(): shutil.rmtree(SALIDA)
    SALIDA.mkdir()
    (SALIDA / 'index.html').write_text(html, encoding='utf-8', newline='\n')
    for f in ('icono-180.png', 'icono-512.png', 'favicon-64.png'):
        shutil.copy2(ICONOS / f, SALIDA / f)
    (SALIDA / 'manifest.webmanifest').write_text(json.dumps({
        'name': 'Abasto de agua', 'short_name': 'Abasto agua',
        'description': 'Registro de entregas de agua de las pipas durante los tandeos',
        'lang': 'es-MX', 'start_url': './', 'scope': './', 'display': 'standalone',
        'background_color': '#C3132B', 'theme_color': '#C3132B',
        'icons': [{'src': 'icono-180.png', 'sizes': '180x180', 'type': 'image/png'},
                  {'src': 'icono-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'}]
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    huella = hashlib.sha1(html.encode('utf-8')).hexdigest()[:8]
    (SALIDA / 'sw.js').write_text(SW.replace('__CACHE__', f'abasto-{version}-{huella}'), encoding='utf-8', newline='\n')
    # Netlify: que el navegador siempre pregunte por la página y el sw.js, para que las versiones nuevas lleguen
    (SALIDA / '_headers').write_text('/\n  Cache-Control: no-cache\n/index.html\n  Cache-Control: no-cache\n/sw.js\n  Cache-Control: no-cache\n', encoding='utf-8')
    print(f'web-abasto/ listo (versión {version}, caché abasto-{version}-{huella})')

SW = r"""/* Service worker de Abasto de agua: la página se pide a la red y, sin señal, se usa la guardada */
const CACHE = '__CACHE__';
const BASE = ['./', 'index.html', 'manifest.webmanifest', 'icono-180.png', 'icono-512.png', 'favicon-64.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const r = e.request, url = new URL(r.url);
  if (r.method !== 'GET') return;                                   // los envíos al registro van directo
  if (url.hostname.endsWith('script.google.com') || url.hostname.endsWith('googleusercontent.com')) return;
  if (r.mode === 'navigate' || url.origin === location.origin) {      // la app: red primero, guardada si no hay señal
    e.respondWith(fetch(r).then(res => { const c = res.clone(); caches.open(CACHE).then(k => k.put(r, c)); return res; })
      .catch(() => caches.match(r).then(x => x || caches.match('index.html'))));
    return;
  }
  /* Leaflet y tipografías: se guardan la primera vez; los mapas de calles no, porque pesan mucho */
  if (/cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com/.test(url.hostname)) {
    e.respondWith(caches.match(r).then(x => x || fetch(r).then(res => { const c = res.clone(); caches.open(CACHE).then(k => k.put(r, c)); return res; })));
  }
});
"""

if __name__ == '__main__':
    main()
