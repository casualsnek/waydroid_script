#!/usr/bin/env bash
#
# install_waydroid.sh
#
# Helper script to install Waydroid on the most common Linux distributions.
# It is meant to be run as root (sudo). After installing Waydroid it can
# optionally initialize the Android image (vanilla or GAPPS).
#
# Usage:
#   sudo ./install_waydroid.sh [--gapps|--vanilla] [--no-init] [--nested]
#
set -euo pipefail

GAAPS=0
INIT=1
NESTED=0

for arg in "$@"; do
    case "$arg" in
        --gapps) GAAPS=1 ;;
        --vanilla) GAAPS=0 ;;
        --no-init) INIT=0 ;;
        --nested) NESTED=1 ;;
        -h|--help)
            cat <<EOF
Usage: sudo $0 [--gapps|--vanilla] [--no-init] [--nested]

  --gapps     Initialize Waydroid with Google Apps
  --vanilla   Initialize Waydroid without Google Apps (default)
  --no-init   Only install packages, do not initialize Waydroid
  --nested    Install weston/cage for X11 sessions
EOF
            exit 0
            ;;
        *) echo "Unknown option: $arg"; exit 1 ;;
    esac
done

log() { echo "[INFO] $*"; }
warn() { echo "[WARN] $*" >&2; }
err() { echo "[ERROR] $*" >&2; }

if [ "${EUID}" -ne 0 ]; then
    err "This script must be run as root. Use: sudo $0"
    exit 1
fi

# Load distro information
if [ -f /etc/os-release ]; then
    . /etc/os-release
else
    err "/etc/os-release not found; cannot detect distribution."
    exit 1
fi

DISTRO_ID="${ID:-unknown}"
CODENAME="${VERSION_CODENAME:-${UBUNTU_CODENAME:-}}"

log "Detected distribution: ${PRETTY_NAME:-$DISTRO_ID} (${CODENAME})"

# Wayland check
if [ "${XDG_SESSION_TYPE:-}" != "wayland" ]; then
    warn "Current session is '${XDG_SESSION_TYPE:-unknown}', not Wayland."
    warn "Waydroid requires a Wayland session to run."
    if [ "$NESTED" -eq 1 ]; then
        log "Installing nested Wayland compositor (weston/cage)..."
        case "$DISTRO_ID" in
            debian|ubuntu|linuxmint|pop|zorin)
                apt-get update
                apt-get install -y weston cage
                ;;
            fedora)
                dnf install -y weston cage
                ;;
            arch|manjaro|endeavouros)
                pacman -Sy --noconfirm weston cage
                ;;
            *)
                warn "Please install weston or cage manually for your distribution."
                ;;
        esac
    else
        warn "Use --nested to install weston/cage, or switch to a Wayland session."
    fi
fi

install_deps_debian() {
    apt-get update
    apt-get install -y curl ca-certificates lzip python3
}

install_waydroid_debian() {
    install_deps_debian

    # Decide whether the third-party repository is needed.
    need_repo=1
    case "$DISTRO_ID" in
        debian)
            # Debian 14+ (trixie is 13, forky/sid 14+). Approximate by codename.
            case "$CODENAME" in
                trixie|bookworm|bullseye) need_repo=1 ;;
                *) need_repo=0 ;;
            esac
            ;;
        ubuntu)
            # Ubuntu 26.10+ (questing is 25.10). Treat questing/resolute as repo-less.
            case "$CODENAME" in
                noble|jammy|mantic|lunar|kinetic|focal|plucky|questing) need_repo=1 ;;
                *) need_repo=0 ;;
            esac
            ;;
    esac

    if [ "$need_repo" -eq 1 ]; then
        log "Adding official Waydroid repository..."
        apt-get install -y curl ca-certificates
        curl -s https://repo.waydro.id | bash
    else
        log "Waydroid is available in the official repositories; skipping third-party repo."
    fi

    apt-get update
    apt-get install -y waydroid
}

install_waydroid_fedora() {
    dnf install -y waydroid
}

install_waydroid_arch() {
    if command -v yay >/dev/null 2>&1; then
        sudo -u "${SUDO_USER:-$USER}" yay -S --noconfirm waydroid
    elif command -v paru >/dev/null 2>&1; then
        sudo -u "${SUDO_USER:-$USER}" paru -S --noconfirm waydroid
    else
        err "No AUR helper (yay/paru) found. Install waydroid from the AUR manually."
        exit 1
    fi
}

install_waydroid_void() {
    xbps-install -Sy waydroid
}

install_waydroid_opensuse() {
    warn "openSUSE requires following the community guide:"
    warn "https://github.com/waydroid/waydroid/discussions/1463"
    exit 1
}

case "$DISTRO_ID" in
    debian|ubuntu|linuxmint|pop|zorin)
        install_waydroid_debian
        ;;
    fedora)
        install_waydroid_fedora
        ;;
    arch|manjaro|endeavouros|cachyos)
        install_waydroid_arch
        ;;
    void)
        install_waydroid_void
        ;;
    opensuse*|suse)
        install_waydroid_opensuse
        ;;
    *)
        err "Unsupported or untested distribution: $DISTRO_ID"
        err "See https://docs.waydro.id/usage/install-on-desktops for manual instructions."
        exit 1
        ;;
esac

log "Waydroid installed."

# Binder check
if [ ! -e /dev/binder ] && [ ! -e /dev/anbox-binder ]; then
    warn "Binder device not found. You may need anbox-modules for your kernel."
    warn "See https://github.com/choff/anbox-modules"
fi

# Enable and start container service if systemd is available
if command -v systemctl >/dev/null 2>&1; then
    log "Enabling waydroid-container service..."
    systemctl enable --now waydroid-container || warn "Could not start waydroid-container; start it manually."
fi

# Initialize Waydroid
if [ "$INIT" -eq 1 ]; then
    if [ "$GAAPS" -eq 1 ]; then
        log "Initializing Waydroid with Google Apps..."
        waydroid init -s GAPPS || sudo waydroid init -s GAPPS
    else
        log "Initializing Waydroid (vanilla)..."
        waydroid init || sudo waydroid init
    fi
fi

log "Done. Launch Waydroid with: waydroid show-full-ui"
log "Or run this extras script: sudo python3 main.py"