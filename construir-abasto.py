# Genera app-abasto/index.html (una sola página, con zonas del SIAPA y escudo) a partir de abasto-agua.html.
# Si existe registro-enlace.txt (renglón 1: enlace del Apps Script, renglón 2: clave, renglón 3: id de la hoja), la app ya sale
# configurada y se arma registro-apps-script.listo.gs. En GitHub ese archivo se crea con los secretos del repositorio.
# Uso: python construir-abasto.py
import base64, json, pathlib
raiz = pathlib.Path(__file__).parent
src = (raiz / 'abasto-agua.html').read_text(encoding='utf-8')
datos = (raiz / 'siapa-datos.js').read_text(encoding='utf-8')
src = src.replace('<script src="siapa-datos.js"></script>', '<script>\n' + datos + '</script>', 1)
reg = {}
archivo = raiz / 'registro-enlace.txt'
if archivo.exists():
    renglones = [x.strip() for x in archivo.read_text(encoding='utf-8').splitlines() if x.strip()]
    if renglones: reg = {'url': renglones[0], 'clave': renglones[1] if len(renglones) > 1 else ''}
    # El script para Apps Script ya con la clave y la hoja (renglón 3); este archivo tampoco se sube
    if len(renglones) > 2:
        gs = (raiz / 'registro-apps-script.gs').read_text(encoding='utf-8').replace('__CLAVE__', reg['clave']).replace('__LIBRO__', renglones[2])
        (raiz / 'registro-apps-script.listo.gs').write_text(gs, encoding='utf-8', newline='\n')
escudo = raiz / 'iconos' / 'escudo-160.png'
logo = 'data:image/png;base64,' + base64.b64encode(escudo.read_bytes()).decode() if escudo.exists() else ''
head = f'''<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#C3132B">
<meta name="apple-mobile-web-app-title" content="Abasto de agua">
<style>body{{margin:0}}</style>
<script>window.AB_APP = true; window.AB_REGISTRO = {json.dumps(reg)}; window.AB_LOGO = {json.dumps(logo)};</script>
</head>
<body>
'''
salida = raiz / 'app-abasto'
salida.mkdir(exist_ok=True)
(salida / 'index.html').write_text(head + src + '\n</body>\n</html>\n', encoding='utf-8', newline='\n')
print('app-abasto/index.html listo' + (' (con registro configurado)' if reg else ' (sin registro: se configura en Ajustes)'))
