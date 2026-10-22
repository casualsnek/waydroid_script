# Guía de funcionamiento de Waydroid Extras Script

Esta guía explica cómo funciona internamente el script `main.py` y sus módulos auxiliares.

## Requisito previo: Wayland

Waydroid solo funciona en una sesión Wayland. Verifica con `echo $XDG_SESSION_TYPE`. Si muestra `x11`, cambia a una sesión Wayland o usa un compositor anidado (`weston`/`cage`). Al usar `sudo`, conserva el entorno con `sudo -E`.

## Visión general

`main.py` es un script Python que modifica las imágenes de Waydroid (principalmente `system.img` y `vendor.img`) para añadir extras como Google Apps, microG, Magisk, traducción ARM, Widevine, etc.

El script puede usarse de dos formas:

1. **Modo interactivo**: ejecuta `sudo python3 main.py` sin argumentos y muestra menús con `InquirerPy`.
2. **Modo línea de comandos**: subcomandos `install`, `remove`/`uninstall`, `hack`, `certified`.

## Archivos principales

- `main.py`: punto de entrada, parseo de argumentos, orquestación de instalación/desinstalación.
- `stuff/*.py`: implementación de cada extra (`Gapps`, `MicroG`, `Magisk`, `Ndk`, `Houdini`, `Widevine`, `Smartdock`, `FDroidPriv`, `Mitm`, `Nodataperm`, `HideStatusBar`, `AndroidId`).
- `stuff/general.py`: clase base `General` con lógica común de descarga, extracción, copia, permisos y propiedades.
- `tools/container.py`: detección de overlayfs, arranque/parada del contenedor, upgrade.
- `tools/images.py`: montaje, desmontaje y redimensionado de imágenes.
- `tools/helper.py`: ejecución de comandos, descargas con barra de progreso, detección de arquitectura.
- `tools/logger.py`: salida coloreada.

## Flujo de instalación

Para cada extra seleccionado:

1. Se crea una lista de objetos (`General`).
2. Si no se usa overlayfs:
   - Se detiene Waydroid.
   - Se redimensionan `system.img` y/o `vendor.img` si es necesario.
   - Se montan las imágenes en `/tmp/waydroid`.
3. Se descarga el paquete del extra (si no está en caché).
4. Se extrae el paquete.
5. Se copian los archivos a la imagen montada (o al overlay).
6. Se ajustan permisos.
7. Se aplican propiedades en `waydroid.cfg` si corresponde.
8. Si no se usa overlayfs, se desmontan las imágenes.
9. Se ejecuta `waydroid upgrade -o` para aplicar cambios.

## Flujo de desinstalación

1. Se crea la lista de extras a eliminar.
2. Si no se usa overlayfs, se montan las imágenes.
3. Se eliminan los archivos listados en `files`.
4. Se eliminan las propiedades asociadas.
5. Se ajustan permisos.
6. Se desmontan las imágenes (si aplica).
7. Se ejecuta `waydroid upgrade -o`.

## Overlayfs vs no overlayfs

- Con `mount_overlays = True` en `/var/lib/waydroid/waydroid.cfg`, los cambios se escriben en `/var/lib/waydroid/overlay` sin montar imágenes.
- Sin overlayfs, el script monta directamente `system.img` y `vendor.img` en `/tmp/waydroid`.

## Hacks

- `nodataperm`: reemplaza `services.jar` para otorgar permisos completos a los datos de apps (Android 11/13).
- `hidestatusbar`: instala un overlay APK para ocultar la barra de estado (Android 11).

## Complemento Python

El script depende de `InquirerPy` para los menús interactivos. Si no está instalado, instala los requisitos con:

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Notas de seguridad

- Ejecuta siempre el script como root.
- Haz copia de seguridad de las imágenes antes de modificarlas.
- Si un hack impide el arranque, elimínalo con `remove`.