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

## Requisito de Wayland (importante)

Waydroid **solo funciona en una sesión Wayland**. Antes de ejecutar este script, asegúrate de que tu escritorio está en Wayland:

```bash
echo $XDG_SESSION_TYPE
```

Debe mostrar `wayland`. Si muestra `x11`, tienes dos opciones:

1. **Cambiar a una sesión Wayland** (recomendado):
   - Cierra sesión, abre el menú de sesión del gestor de pantalla (GDM/SDDM/LightDM) y elige una sesión Wayland como *Ubuntu on Wayland*, *GNOME on Wayland* o *KDE Plasma (Wayland)*.
   - En Ubuntu/GNOME, Wayland es el predeterminado desde 22.04. Si estaba deshabilitado, reactívalo en `/etc/gdm3/custom.conf` (`WaylandEnable=true`) y reinicia GDM.
   - En Xubuntu/XFCE 26.04 (beta, soporte experimental de Wayland), prueba `startxfce4 --wayland` o la sesión *Xfce (Wayland)*. Si no está disponible, usa un compositor anidado (ver abajo).
   - En Fedora, Wayland es el predeterminado para GNOME/KDE.
   - En Arch/Manjaro, instala un compositor/escritorio Wayland (GNOME, KDE Plasma, Sway, Hyprland) o usa `cage`/`weston`.
2. **Usar un compositor Wayland anidado en un escritorio X11**:
   ```bash
   sudo apt install cage weston
   weston --xwayland
   # o
   cage -- waydroid show-full-ui
   ```

Al ejecutar Waydroid o este script con `sudo`, conserva las variables de entorno de Wayland para que el socket de sesión siga siendo visible:

```bash
sudo -E python3 main.py
```

### Nota sobre XWayland

XWayland permite ejecutar **aplicaciones X11** dentro de una sesión Wayland. **No** sustituye a un compositor Wayland y por sí solo no permite ejecutar Waydroid. Waydroid sigue necesitando un compositor Wayland (GNOME/KDE/Sway/Hyprland, o `weston`/`cage`).

Si necesitas XWayland (por ejemplo para apps antiguas solo X11), instálalo:

- Debian/Ubuntu: `sudo apt install xwayland`
- Fedora: `sudo dnf install xorg-x11-server-Xwayland`
- Arch/Manjaro: `sudo pacman -S xorg-xwayland`

En una sesión Wayland normal, XWayland se inicia automáticamente al lanzar una app X11. Puedes verificarlo con:

```bash
echo $DISPLAY
xlsclients
```

Si quieres iniciarlo manualmente:

```bash
Xwayland :1 &
DISPLAY=:1 <aplicacion>
```

### Notas por distribución

- **Ubuntu / Debian y derivadas**: se requiere sesión Wayland (Ubuntu 22.04+). Instala Waydroid desde el repositorio oficial o el repositorio de Waydroid según su documentación.
- **Xubuntu 26.04 (beta)**: el soporte Wayland en XFCE es experimental; si la sesión no está disponible, instala `weston` y/o `cage` y ejecuta Waydroid a través de ellos.
- **Fedora / openSUSE / Arch / Void / NixOS**: usa la sesión Wayland proporcionada por tu escritorio/compositor; los paquetes de Waydroid están disponibles en los repositorios respectivos.

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