# Abasto de agua

App para registrar las entregas de agua de las pipas de Bomberos Guadalajara durante los tandeos del SIAPA. Cada entrega se manda sola a una hoja de Google Drive, con ubicación, litros y foto de evidencia. Ya no se manda nada por WhatsApp.

- **Android:** APK firmado, armado con Capacitor (`android-abasto/`, `construir-android.py`).
- **iPhone:** app web instalable desde Safari, publicada con GitHub Pages (`construir-web.py`, `.github/workflows/pages.yml`).
- **Registro:** hoja de Google con un script de Apps Script (`registro-apps-script.gs`).

Cómo funciona, cómo se usa y cómo se actualiza: [LEEME - Registro de abasto de agua.md](LEEME%20-%20Registro%20de%20abasto%20de%20agua.md).

Este repositorio no guarda datos de ciudadanos ni claves. El enlace y la clave del registro viven en `registro-enlace.txt` (local) y en los secretos del repositorio. La llave de firma de Android tampoco se sube.
