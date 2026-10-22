# Waydroid Extras Script

Script para añadir Google Apps, microG, Magisk, traducción ARM, Widevine y otros extras a Waydroid.

Este fork (`BENDER35/waydroid_script_2026`) mantiene el flujo original de `casualsnek/waydroid_script` y corrige varios problemas detectados al probarlo en sistemas actuales.

## Características

- Instalar / desinstalar OpenGApps (Android 11) o MindTheGapps (Android 13)
- Instalar / desinstalar microG (Standard, NoGoolag, UNLP, Minimal, MinimalIAP)
- Instalar / desinstalar traducción ARM libndk (recomendado para CPU AMD)
- Instalar / desinstalar traducción ARM libhoudini (recomendado para CPU Intel)
- Instalar / desinstalar Magisk Delta
- Instalar / desinstalar Widevine DRM L3
- Instalar / desinstalar Smart Dock
- Instalar / desinstalar F-Droid Privileged Extension
- Instalar un certificado CA autofirmado en el almacén de confianza del sistema (`mitm`)
- Hacks: `nodataperm`, `hidestatusbar`
- Obtener el Android ID necesario para certificar un dispositivo con Google

## Requisitos

- Waydroid inicializado y funcionando
- Python 3
- `lzip`
- Paquetes de Python: `requests`, `tqdm`, `InquirerPy`

En Debian / Ubuntu:

```bash
sudo apt install lzip python3 python3-pip
```

## Instalación

```bash
git clone https://github.com/BENDER35/waydroid_script_2026.git
cd waydroid_script_2026
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Uso

### Modo interactivo

```bash
sudo venv/bin/python3 main.py
```

### Línea de comandos

```bash
# Obtener el Android ID para la certificación de Play Store
sudo venv/bin/python3 main.py certified

# Instalar uno o varios extras
sudo venv/bin/python3 main.py install gapps
sudo venv/bin/python3 main.py install microg magisk libndk
sudo venv/bin/python3 main.py install mitm --ca-cert mycert.pem
sudo venv/bin/python3 main.py install fdroidpriv

# Desinstalar uno o varios extras
sudo venv/bin/python3 main.py remove gapps
sudo venv/bin/python3 main.py uninstall microg magisk

# Aplicar hacks (Android 11; nodataperm también disponible en Android 13)
sudo venv/bin/python3 main.py hack nodataperm
sudo venv/bin/python3 main.py hack hidestatusbar
```

La versión de Android se puede seleccionar con `-a` / `--android-version` (por defecto: 13):

```bash
sudo venv/bin/python3 main.py -a 11 install gapps
```

## Dependencias

`lzip` es necesario para extraer OpenGApps. Instálalo con el gestor de paquetes de tu distribución:

- Arch / Manjaro: `sudo pacman -S lzip`
- Debian / Ubuntu: `sudo apt install lzip`
- Fedora / RHEL: `sudo dnf install lzip`
- openSUSE: `sudo zypper install lzip`

## Notas

- El script debe ejecutarse como root.
- En configuraciones sin overlayfs el script monta las imágenes de Waydroid en `/tmp/waydroid`; asegúrate de que Waydroid esté detenido antes de ejecutarlo.
- Magisk se instala en el siguiente arranque.
- Para la certificación de Google Play, ejecuta `certified`, registra el ID impreso en https://google.com/android/uncertified/, espera 10-20 minutos y luego limpia la caché de Google Play Services.

## Solución de problemas

- `ModuleNotFoundError: No module named 'InquirerPy'`: instala los requisitos dentro del entorno virtual (`venv/bin/pip install -r requirements.txt`).
- Waydroid debe estar en ejecución para `certified`.
- Si un hack rompe el arranque, elimínalo con `sudo venv/bin/python3 main.py remove <hack>`.

## Créditos

- [WayDroid](https://github.com/waydroid/waydroid)
- [casualsnek/waydroid_script](https://github.com/casualsnek/waydroid_script)
- [Magisk Delta](https://huskydg.github.io/magisk-files/)
- [microG Project](https://microg.org)
- [Open GApps](https://opengapps.org)
- [Smart Dock](https://github.com/axel358/smartdock)
- [wd-scripts](https://github.com/electrikjesus/wd-scripts/)