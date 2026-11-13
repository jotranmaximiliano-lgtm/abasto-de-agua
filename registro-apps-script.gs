/**
 * Registro de abasto de agua — PLANTILLA. Lo que se pega en Apps Script es registro-apps-script.listo.gs,
 * que arma construir-abasto.py con la clave y la hoja de registro-enlace.txt (archivo privado, no se sube).
 * Recibe de la app las entregas y sus fotos de evidencia:
 *  - cada día va en su propia pestaña, nombrada con la fecha (12/11/2026), como la sábana de C5;
 *  - si una entrega llega otra vez (se reintentó sin señal, o se corrigió en la app) se actualiza su renglón, no se duplica;
 *  - las fotos se guardan en la carpeta «Fotos abasto de agua», una subcarpeta por día, y su liga queda en la columna Fotos.
 * La CLAVE es la misma que lleva la app; no la compartas fuera del equipo.
 *
 * La primera vez (y cada vez que Google lo pida): elige «autorizar» arriba, junto a Depurar, y toca Ejecutar.
 */
const CLAVE = '__CLAVE__';
const LIBRO = '__LIBRO__'; // hoja «Registro abasto de agua 2026» en Drive
const CARPETA_FOTOS = 'Fotos abasto de agua';
const COLUMNAS = ['Hora', 'Base', 'Pipa', 'Chofer', 'Bombero', 'Lugar o institución', 'Recibe', 'Teléfono',
  'Domicilio', 'Colonia', 'Almacenamiento', 'Cantidad', 'Litros', 'Ubicación', 'Fotos', 'Notas', 'id'];
const COL = nombre => COLUMNAS.indexOf(nombre) + 1;

/* Solo sirve para que Google pida los permisos de la hoja y de Drive */
function autorizar() {
  SpreadsheetApp.openById(LIBRO).getName();
  DriveApp.getFileById(LIBRO).getParents().next().getName();
}

/* Pestaña del día; si no existe se crea al principio, con encabezados */
function hojaDelDia_(libro, fecha) {
  let h = libro.getSheetByName(fecha);
  if (h) return h;
  h = libro.insertSheet(fecha, 0);
  h.appendRow(COLUMNAS);
  h.setFrozenRows(1);
  h.getRange(1, 1, 1, COLUMNAS.length).setFontWeight('bold');
  h.getRange(1, COL('Hora'), h.getMaxRows(), 1).setNumberFormat('@'); // la hora queda como texto
  h.getRange(1, COL('Teléfono'), h.getMaxRows(), 1).setNumberFormat('@'); // el teléfono no se vuelve número
  /* Pestañas vacías que ya no hacen falta */
  ['Entregas', 'PRUEBA'].forEach(n => { const v = libro.getSheetByName(n); if (v && v.getLastRow() <= 1) libro.deleteSheet(v); });
  return h;
}

/* Renglón (1, 2, …) de la entrega con ese id en la pestaña, o 0 */
function renglonDe_(h, id) {
  if (h.getLastRow() < 2) return 0;
  const ids = h.getRange(2, COL('id'), h.getLastRow() - 1, 1).getValues().map(r => String(r[0]));
  const i = ids.indexOf(String(id));
  return i < 0 ? 0 : i + 2;
}

function carpetaDelDia_(fecha) {
  const padre = DriveApp.getFileById(LIBRO).getParents().next();
  const raiz = padre.getFoldersByName(CARPETA_FOTOS).hasNext() ? padre.getFoldersByName(CARPETA_FOTOS).next() : padre.createFolder(CARPETA_FOTOS);
  const nombre = String(fecha).replace(/\//g, '-');
  return raiz.getFoldersByName(nombre).hasNext() ? raiz.getFoldersByName(nombre).next() : raiz.createFolder(nombre);
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const datos = JSON.parse(e.postData.contents);
    if (datos.clave !== CLAVE) return respuesta_({ ok: false, error: 'clave' });
    const libro = SpreadsheetApp.openById(LIBRO);
    let nuevas = 0, cambiadas = 0, borradas = 0;
    const urls = {};

    /* Entregas: nueva → renglón al final; repetida o corregida → se reescribe su renglón */
    (datos.entregas || []).forEach(x => {
      if (!x.id || !x.fecha) return;
      const h = hojaDelDia_(libro, x.fecha), r = renglonDe_(h, x.id);
      const valores = COLUMNAS.map(c => x[c] == null ? '' : x[c]);
      if (!r) { h.appendRow(valores); nuevas++; return; }
      const antes = h.getRange(r, 1, 1, COLUMNAS.length).getValues()[0];
      if (!valores[COL('Fotos') - 1]) valores[COL('Fotos') - 1] = antes[COL('Fotos') - 1]; // no perder ligas ya puestas
      h.getRange(r, 1, 1, COLUMNAS.length).setValues([valores]);
      cambiadas++;
    });

    /* Entregas que se borraron en la app */
    (datos.borrar || []).forEach(x => {
      const h = libro.getSheetByName(x.fecha || ''); if (!h) return;
      const r = renglonDe_(h, x.id); if (r) { h.deleteRow(r); borradas++; }
    });

    /* Fotos: se guardan una sola vez (por su id) y su liga se agrega a los renglones de las entregas */
    (datos.fotos || []).forEach(f => {
      if (!f.id || !f.base64) return;
      const carpeta = carpetaDelDia_(f.fecha), nombre = f.id + '.jpg', ya = carpeta.getFilesByName(nombre);
      const archivo = ya.hasNext() ? ya.next() : carpeta.createFile(Utilities.newBlob(Utilities.base64Decode(f.base64), 'image/jpeg', nombre));
      const url = archivo.getUrl();
      urls[f.id] = url;
      const h = libro.getSheetByName(f.fecha || ''); if (!h) return;
      (f.ids || []).forEach(id => {
        const r = renglonDe_(h, id); if (!r) return;
        const celda = h.getRange(r, COL('Fotos')), hay = String(celda.getValue() || '');
        if (!hay.includes(url)) celda.setValue(hay ? hay + '\n' + url : url);
      });
    });
    return respuesta_({ ok: true, nuevas, cambiadas, borradas, urls });
  } finally {
    lock.releaseLock();
  }
}

/* Para ver en el mapa de la app las entregas de todas las pipas del día: ?clave=…&fecha=12/11/2026
   Solo regresa datos sin nombres ni teléfonos */
function doGet(e) {
  const p = e.parameter || {};
  if (p.clave !== CLAVE) return respuesta_({ ok: false, error: 'clave' });
  const h = SpreadsheetApp.openById(LIBRO).getSheetByName(p.fecha || '');
  if (!h) return respuesta_({ ok: true, entregas: [] });
  const filas = h.getDataRange().getDisplayValues(), cab = filas.shift();
  const quiero = ['id', 'Hora', 'Base', 'Pipa', 'Lugar o institución', 'Colonia', 'Almacenamiento', 'Litros', 'Ubicación'];
  const idx = quiero.map(c => cab.indexOf(c));
  return respuesta_({ ok: true, entregas: filas.map(r => Object.fromEntries(quiero.map((c, i) => [c, r[idx[i]]]))) });
}

function respuesta_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
