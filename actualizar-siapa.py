"""Descarga del sitio de rotación del SIAPA las zonas, las colonias y los días de corte vigentes,
y los deja en siapa-datos.js para la app de abasto. También copia las garzas y bases de toma-datos.html.
Las zonas se recortan al perímetro de las coberturas de Guadalajara (las zonas de las bases en toma-datos.html):
el tandeo abarca otros municipios que no atendemos.

Uso:  python actualizar-siapa.py
"""
import json, pathlib, re, urllib.request, datetime
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

AQUI = pathlib.Path(__file__).resolve().parent
SITIO = 'https://rotaciondeserviciosiapa.jalisco.gob.mx'
LAT0, LON0, ESC = 20.0, -104.0, 1e5   # coordenadas guardadas como enteros: (lat-LAT0)*1e5

def bajar(ruta):
    req = urllib.request.Request(SITIO + ruta, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))

def decodificar_arcos(topo):
    sx, sy = topo['transform']['scale']; tx, ty = topo['transform']['translate']
    arcos = []
    for arco in topo['arcs']:
        x = y = 0; pts = []
        for dx, dy in arco:
            x += dx; y += dy
            pts.append((y * sy + ty, x * sx + tx))   # (lat, lon)
        arcos.append(pts)
    return arcos

def anillo(arcos, ids):
    pts = []
    for i in ids:
        a = arcos[i] if i >= 0 else arcos[~i][::-1]
        pts.extend(a if not pts else a[1:])
    return pts

def poligonos(arcos, g):
    if g['type'] == 'Polygon': return [[anillo(arcos, r) for r in g['arcs']]]
    if g['type'] == 'MultiPolygon': return [[anillo(arcos, r) for r in p] for p in g['arcs']]
    return []

def simplificar(pts, tol):
    """Douglas-Peucker en grados (tol ≈ 1e-5 → 1 m)."""
    if len(pts) < 5: return pts
    def dist(p, a, b):
        (y, x), (y1, x1), (y2, x2) = p, a, b
        dx, dy = x2 - x1, y2 - y1
        if dx == dy == 0: return ((x - x1) ** 2 + (y - y1) ** 2) ** .5
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        return ((x - x1 - t * dx) ** 2 + (y - y1 - t * dy) ** 2) ** .5
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    pila = [(0, len(pts) - 1)]
    while pila:
        i, j = pila.pop()
        k, dm = -1, tol
        for m in range(i + 1, j):
            d = dist(pts[m], pts[i], pts[j])
            if d > dm: k, dm = m, d
        if k >= 0: keep[k] = True; pila += [(i, k), (k, j)]
    out = [p for p, s in zip(pts, keep) if s]
    return out if len(out) >= 4 else pts

def enteros(pts):
    return [v for la, lo in pts for v in (round((la - LAT0) * ESC), round((lo - LON0) * ESC))]

def poligono_shapely(anillos_latlon):
    """Anillos [(lat, lon)…] (exterior + huecos) → Polygon de shapely en (lon, lat)."""
    ext, *huecos = [[(lo, la) for la, lo in r] for r in anillos_latlon]
    return Polygon(ext, huecos).buffer(0)

def a_anillos(geom, tol):
    """Polygon/MultiPolygon de shapely → [[anillo exterior, huecos…], …] en enteros."""
    geoms = [geom] if isinstance(geom, Polygon) else list(getattr(geom, 'geoms', []))
    out = []
    for g in geoms:
        if not isinstance(g, Polygon) or g.area < 1e-8: continue
        g = g.simplify(tol)
        if g.is_empty: continue
        out.append([enteros([(la, lo) for lo, la in r.coords]) for r in [g.exterior, *g.interiors]])
    return out

def main():
    td = (AQUI.parent / 'toma-datos.html').read_text(encoding='utf-8')
    m = re.search(r'/\* COBERTURAS:INICIO.*?\*/\s*const COBERTURAS = (\{.*?\});\s*/\* COBERTURAS:FIN \*/', td, re.S)
    cob = json.loads(m.group(1))
    perimetro = unary_union([Polygon([(lo, la) for la, lo in a]).buffer(0) for z in cob['zonas'] for a in z['anillos']])
    topo = bajar('/geo/rotacion-siapa.topo.json')
    ajustes = bajar('/api/ajustes.php')
    arcos = decodificar_arcos(topo)
    obj = topo['objects']
    colores = {1: '#776a3f', 2: '#e37cfb', 3: '#99e36c', 4: '#77d1d5', 5: '#8b5fda', 6: '#8f4f77', 7: '#f0c451'}

    zonas = []
    for g in obj['zonas']['geometries']:
        z = g['properties']['z']
        geom = unary_union([poligono_shapely(p) for p in poligonos(arcos, g)]).intersection(perimetro)
        pols = a_anillos(geom, 2e-5)
        if pols: zonas.append({'z': z, 'nombre': g['properties']['nombre'], 'color': colores.get(z, '#005cb9'), 'p': pols})

    col = {'n': [], 'm': [], 'cp': [], 'z': [], 'r': []}
    for g in obj['colonias']['geometries']:
        pr = g['properties']; n = (pr.get('n') or '').strip()
        if not n or re.fullmatch(r'(?i)sin nombre', n): continue
        pols = poligonos(arcos, g)
        if not any(Polygon([(lo, la) for la, lo in p[0]]).buffer(0).intersects(perimetro) for p in pols): continue
        anillos = [enteros(simplificar(p[0], 1.5e-5)) for p in pols]
        col['n'].append(n); col['m'].append(pr.get('m') or ''); col['cp'].append(pr.get('cp') or 0)
        col['z'].append(pr.get('z') or ''); col['r'].append(anillos)
    # Colonias movidas de zona desde el panel del SIAPA
    for clave, v in (ajustes.get('colonias') or {}).items():
        nombre, mun = (clave.split('|') + ['', ''])[:2]
        for i, n in enumerate(col['n']):
            if n == nombre and col['m'][i] == mun and isinstance(v.get('zonas'), list):
                col['z'][i] = ','.join(map(str, v['zonas']))

    dias = {str(k): v['dias'] for k, v in ajustes['zonas'].items()}
    datos = {'actualizado': ajustes.get('actualizado', ''), 'descargado': datetime.date.today().isoformat(),
             'lat0': LAT0, 'lon0': LON0, 'esc': ESC, 'dias': dias, 'zonas': zonas, 'colonias': col}

    # Garzas, bases y perímetro de Guadalajara del mapa de coberturas de la app toma datos
    datos['perimetro'] = a_anillos(perimetro, 3e-5)
    datos['coberturas'] = [{'nombre': z['nombre'], 'base': z['base'], 'modulo': bool(z.get('modulo')),
                            'p': [enteros(simplificar([tuple(x) for x in r], 2e-5)) for r in z['anillos']]} for z in cob['zonas']]
    datos['garzas'] = [{'nombre': g['nombre'], 'dir': g.get('dir', ''), 'pos': g['pos']} for g in cob['garzas']]
    datos['bases'] = [{'nombre': s['nombre'], 'tipo': s['tipo'], 'pos': s['pos']} for s in cob['sitios']]

    js = '/* Generado por actualizar-siapa.py desde ' + SITIO + ' — no editar a mano */\nwindow.SIAPA = ' + json.dumps(datos, ensure_ascii=False, separators=(',', ':')) + ';\n'
    (AQUI / 'siapa-datos.js').write_text(js, encoding='utf-8')
    print(f"siapa-datos.js: {len(zonas)} zonas, {len(col['n'])} colonias, {len(datos['garzas'])} garzas, "
          f"{len(js) // 1024} KB; calendario actualizado {datos['actualizado']}")
    for z in sorted(dias): print(f"  Zona {z}: sin servicio {', '.join(dias[z])}")

if __name__ == '__main__':
    main()
