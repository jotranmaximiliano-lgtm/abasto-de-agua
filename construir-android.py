"""Arma la app Android (APK firmado) de Abasto de agua.

Uso:
  python construir-android.py          # vuelve a armar la misma versión
  python construir-android.py 1.1      # sube la versión (cada APK que se reparta debe llevar versión nueva)

Pasos: arma app-abasto/index.html, la copia a la app Android (Capacitor), compila con Gradle y deja
«Abasto de agua <versión>.apk» en esta carpeta. La llave de firma está en android-abasto/android/abasto-release.jks:
sin ella no se pueden publicar actualizaciones que se instalen encima, así que guarda un respaldo.
"""
import os, pathlib, re, shutil, subprocess, sys

AQUI = pathlib.Path(__file__).resolve().parent
PROY = AQUI / 'android-abasto'
ANDROID = PROY / 'android'
JDK = pathlib.Path(r'C:\Program Files\Android\Android Studio\jbr')

def correr(cmd, cwd, **kw):
    print('>', ' '.join(map(str, cmd)))
    subprocess.run(cmd, cwd=cwd, check=True, **kw)

def main():
    gradle = ANDROID / 'app' / 'build.gradle'
    g = gradle.read_text(encoding='utf-8')
    codigo = int(re.search(r'versionCode (\d+)', g).group(1))
    nombre = re.search(r'versionName "([^"]+)"', g).group(1)
    if len(sys.argv) > 1 and sys.argv[1] != nombre:
        codigo, nombre = codigo + 1, sys.argv[1]
        g = re.sub(r'versionCode \d+', f'versionCode {codigo}', g)
        g = re.sub(r'versionName "[^"]+"', f'versionName "{nombre}"', g)
        gradle.write_text(g, encoding='utf-8', newline='\n')

    correr([sys.executable, 'construir-abasto.py'], AQUI)
    html = (AQUI / 'app-abasto' / 'index.html').read_text(encoding='utf-8')
    html = html.replace('window.AB_APP = true;', f'window.AB_APP = true; window.AB_VERSION = {nombre!r};', 1)
    (PROY / 'www').mkdir(exist_ok=True)
    (PROY / 'www' / 'index.html').write_text(html, encoding='utf-8', newline='\n')

    npx = shutil.which('npx.cmd') or shutil.which('npx')
    correr([npx, 'cap', 'sync', 'android'], PROY)
    env = dict(os.environ, JAVA_HOME=str(JDK))
    correr([str(ANDROID / 'gradlew.bat'), '--no-daemon', 'assembleRelease'], ANDROID, env=env)

    apk = ANDROID / 'app' / 'build' / 'outputs' / 'apk' / 'release' / 'app-release.apk'
    destino = AQUI / f'Abasto de agua {nombre}.apk'
    shutil.copy2(apk, destino)
    print(f'Listo: {destino.name} (versión {nombre}, código {codigo}, {destino.stat().st_size // 1024} KB)')

if __name__ == '__main__':
    main()
