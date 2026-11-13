# Registro de abasto de agua durante los tandeos

## 1. Lo que dice el chat del 12/11/26 («Apoyo de Agua 1er. Turno»)

En el día hubo 150 mensajes, de 08:54 a 20:27. De ellos, 60 son fotos o archivos multimedia, que casi no sirven para el registro.

**Cómo se organiza el día**

- **Asignación de pipas.** La coordinación asigna pipa, base, chofer y bombero: 8443 (B5), 8444 (B2), 8445 (B3) y 8446 (B4). La 8442 solo aparece en los saldos de combustible.
- **Garzas de carga.** San Pedrito, San Gaspar y La Bethel.
- **Puntos asignados.** Cada punto llega con un código PC, el lugar, un enlace de Maps, el cruce, la colonia y la base. Por ejemplo: «PC-127 · Academia 30 · Lomas de Oblatos · Base 4».
- **Encargado en el punto.** En cada punto espera un «Guardián del Agua», que trae los domicilios. La instrucción a las pipas es «tomar los 33 (datos) del encargado y de las personas».
- **Claves de radio.** Se usan claves (64 misión cumplida, 102 agua, 121 entrevista, 58 lugar indicado, 02 combustible) y se reporta lo que queda en la pipa («60 % de 102», «tres cuartos de 102»).

**Cómo llegan los datos de las entregas: hay tres formatos distintos**

1. **Institución.** Nombre del lugar, encargada, número de tinacos y a veces los litros («2 tinacos, total 1,200 L»; «3 tinacos de 1,100 L, total 3,300 L»). A veces no traen litros.
2. **Lista de vecinos sin litros.** Nombre, domicilio y teléfono, con la colonia una sola vez arriba (24 personas del Parque El Cuadro).
3. **Mensajes sueltos con litros.** Uno por persona, con nombre, domicilio, teléfono y litros (60, 100, 200, 250, 400 L). No dicen el tipo de almacenamiento.

**Problemas que se repiten**

- **Faltan datos clave.** Casi nunca viene el tipo de almacenamiento, y muchas veces tampoco los litros ni la colonia.
- **Personas repetidas.** La misma persona sale en varias listas con domicilios distintos, por ejemplo Amado Camarena 2672 y 2372.
- **Números de pipa mal escritos.** 8346, 4445, «84 44».
- **Calles mal escritas.** «Esteban uerta», «Camerena».
- **Listas tardías.** Las listas llegan en bloque al final. A las 14:15 la coordinación tuvo que preguntar «¿Tenemos datos de las personas que fueron apoyadas?».

Conclusión: el registro no falla por falta de ganas, sino porque cada quien lo escribe distinto y de memoria al final. Por eso la app pide pocas cosas, con botones, y en el momento de la entrega. Y ya no se manda nada por WhatsApp: todo va al registro.

## 2. Lo que se armó

| Archivo | Para qué |
|---|---|
| `abasto-agua.html` | La app (código fuente) |
| `app-abasto/index.html` | La app lista para el teléfono: un solo archivo que funciona sin internet (menos el mapa y el envío) |
| `siapa-datos.js` | Zonas y colonias del SIAPA dentro de Guadalajara, días de corte, garzas, bases y el límite de las coberturas |
| `actualizar-siapa.py` | Vuelve a bajar del sitio del SIAPA las zonas y el calendario y los recorta a Guadalajara (correr cuando cambie el tandeo; necesita `pip install shapely`) |
| `construir-abasto.py` | Arma `app-abasto/index.html` |
| `registro-apps-script.gs` | El código que se pega en la hoja de Drive para recibir las entregas |

**Cómo se usa en el teléfono (lo que hace el compañero)**

1. **Una vez por turno:** elige su base y la pipa se pone sola (B1 8442, B2 8444, B3 8445, B4 8446, B5 8443; todas de 9,000 L). Escribe su nombre y el del chofer. No hay nada más que configurar: la app no tiene Ajustes.
2. **Entrega a domicilio** (casa, escuela, institución): toca «+ Entrega a domicilio». La ubicación se toma sola y con ella salen la colonia, la base que cubre ese punto y la zona del tandeo. Luego escribe:
   - quién recibe (y su cargo, si es una institución);
   - calle y número;
   - qué se llenó, con botones: garrafón (cuántos, 20 L c/u), tinaco (450, 750 o 1,100 L y cuántos), aljibe o cisterna (litros descargados, o «toda la carga» = 9,000 L), u otro.

   Los litros se calculan solos. El teléfono es opcional. Se puede tomar una foto de evidencia. «Guardar y otra aquí» sirve para varias casas seguidas en el mismo lugar.
3. **Punto de llenado** (la pipa se queda en un lugar y la gente llega con sus recipientes, como el Parque El Cuadro): toca «+ Punto de llenado». Se pone una sola vez el nombre del punto, y la ubicación y la colonia salen solas. Luego, por cada persona, solo se escribe su nombre y domicilio (y teléfono si lo da), se toca cuántos litros se llevó (20, 50, 100 o 200 L, u otra cantidad) y «+ Agregar persona». Se pueden tomar fotos del punto. En el registro cada persona es un renglón con el nombre del punto y «Recipientes». Los litros que se eligen se quedan marcados para la siguiente persona.
4. **Fotos de evidencia:** se reducen a unos 200 KB, se guardan en el teléfono y se suben solas a Drive cuando hay señal. Quedan en la carpeta «Fotos abasto de agua» (junto a la hoja), una subcarpeta por día, y su liga aparece en la columna «Fotos» del renglón.
5. **Al final:** en «Hoy» se ven las entregas, los litros por tipo y las colonias del día. No se manda nada por WhatsApp: cada entrega se va sola al registro de Drive.

**Lo que ve la coordinación**

- En el inicio, qué zonas del SIAPA no tienen servicio hoy.
- Un mapa con las zonas del tandeo recortadas al límite de las coberturas de Guadalajara (más fuertes las que hoy no tienen servicio), las garzas, las bases y las entregas. Las partes del tandeo en Zapopan, Tlajomulco, El Salto y otros municipios ya no se marcan.
- Con el registro configurado, también las entregas de todas las pipas del día.

**Sobre el calendario del SIAPA:** la app toma los días del sitio oficial (rotaciondeserviciosiapa.jalisco.gob.mx), que se actualizó el 03/11/26. Esos días coinciden con los del PDF `colonias_siapa.pdf` que está en esta carpeta. Aun así, conviene confirmarlo con el SIAPA, como indicaron. Si cambia, se corre `python actualizar-siapa.py` y luego `python construir-abasto.py`.

## 3. El registro en Drive

«Registro abasto de agua 2026» está en la carpeta «Abasto de agua» de tu Drive, junto con la carpeta «Fotos abasto de agua». Recibe las entregas por medio del script `registro-apps-script.gs`, publicado como app web. El enlace y la clave están en `registro-enlace.txt` (privado) y `construir-abasto.py` los mete en la app.

- **Una pestaña por día**, nombrada con la fecha (12/11/2026), como la sábana de C5. Se crea sola con la primera entrega del día y queda al principio.
- **Columnas** (solo lo que se compartía en el chat, más la hora y la ubicación): Hora, Base, Pipa, Chofer, Bombero, Lugar o institución, Recibe, Teléfono, Domicilio, Colonia, Almacenamiento, Cantidad, Litros, Ubicación (liga de Google Maps), Fotos (ligas a Drive), Notas, id. El id es interno: con él, si una entrega llega dos veces no se repite, y si se corrige o se borra en la app, se corrige o se borra su renglón.
- Cada entrega se envía sola cuando hay señal. Sin señal se queda en el teléfono y se manda después.

**Cuando cambie el script** (como en esta versión): en Apps Script borra todo, pega el nuevo `registro-apps-script.listo.gs` (lo arma `construir-abasto.py`) y guarda. Si el script pide permisos nuevos (esta versión pide Drive, para las fotos), elige `autorizar` en la lista junto a «Depurar», toca **Ejecutar** y acepta los permisos. Luego **Implementar → Gestionar implementaciones → lápiz ✏ → Versión: Nueva versión → Implementar**. Así el enlace `/exec` no cambia y no hay que rehacer la app.

**La hoja queda privada**, solo con quien tú la compartas. La app solo puede agregar renglones y, con la clave, traer los puntos del día para el mapa (sin nombres ni teléfonos). No la compartas «a cualquiera con el enlace»: trae nombres, domicilios y teléfonos de ciudadanos. Lo mismo con la carpeta de fotos: para que la coordinadora las vea, compártele la carpeta a ella directamente.

## 4. App para Android

`Abasto de agua 1.0.apk` (en esta carpeta) es la app instalable. Por dentro es la misma página, empaquetada con Capacitor en `android-abasto/`, y ya pide los permisos de ubicación y cámara como cualquier app.

**Instalar en un teléfono:** pásale el APK (por Drive, cable o WhatsApp) y ábrelo. Android pedirá permitir «instalar apps de origen desconocido» para la app con la que se abrió (Drive, Archivos, WhatsApp). La primera vez que se toma ubicación o foto, la app pide el permiso: hay que elegir «Mientras se usa la app».

**Sacar una versión nueva** (después de cambiar `abasto-agua.html`): `python construir-android.py 1.1` (con el número nuevo). Deja `Abasto de agua 1.1.apk`. Al instalarla encima se conserva lo capturado en el teléfono.

**La llave de firma** está en `android-abasto/android/abasto-release.jks` y sus contraseñas en `keystore.properties`. Sin esos dos archivos no se pueden hacer actualizaciones que se instalen encima: habría que desinstalar y se perdería lo no enviado. Guarda un respaldo en un lugar privado y no los compartas.

Para compilar se usa el Android Studio instalado (su Java) y Gradle 9.1. No hace falta abrir Android Studio.

## 5. App para iPhone (app web instalable)

La carpeta `web-abasto/` es la misma app, preparada para instalarse desde Safari. Se arma con `python construir-web.py`.
- Tiene su ícono y abre a pantalla completa.
- Pide permisos de ubicación y cámara.
- Abre y captura sin señal: lo capturado espera en el teléfono, igual que en Android.

**Publicarla (una vez):**
1. Crea una cuenta gratis en netlify.com (se puede con la cuenta de Google).
2. Entra a app.netlify.com/drop y arrastra la carpeta `web-abasto` completa.
3. En **Site configuration → Change site name** ponle un nombre, por ejemplo `abasto-agua-gdl`. Queda en `https://abasto-agua-gdl.netlify.app`.

**Actualizarla:** corre `python construir-web.py`. Luego, en Netlify, entra al sitio → **Deploys** y arrastra otra vez la carpeta `web-abasto`. Los iPhone toman la versión nueva solos la siguiente vez que abran la app con señal.

**Instalar en el iPhone:**
1. Abre la dirección en **Safari**. Chrome en iPhone no sirve para instalarla.
2. Toca **Compartir** y luego **«Agregar a inicio»**.
3. Desde entonces se abre con ese ícono.

La primera vez que se toma ubicación o foto, el iPhone pide permiso. Lo capturado se queda en ese ícono: si se borra la app de inicio, se borra lo que no se haya enviado.

**Ojo:** la dirección es pública, aunque nadie la encuentra si no se la dan, y la app lleva dentro la clave del registro. Compártela solo con el equipo. Si se filtra, se cambia la clave en el script y se vuelve a publicar.

## 6. Lo que falta o conviene decidir

- **Aviso de privacidad.** Hace falta un aviso breve que se le pueda leer o mostrar a quien recibe el agua.
- **Probar en campo.** Falta una entrega real de punta a punta desde un teléfono (ubicación, foto y renglón en la hoja). En el emulador se probaron los permisos y el botón «atrás». La foto no se pudo tomar porque el emulador no tiene cámara.
- **Actualizaciones automáticas.** Hoy cada versión nueva se reparte como APK. Más adelante, con la app formal, se puede hacer por Play o con aviso de actualización dentro de la app.
- **Resumen para la coordinadora.** Se arma cuando llegue el formato que ella recibe.
