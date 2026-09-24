"""Configuración centralizada del shell."""

NOMBRE = "SHELL PERSONALIZADO"
VERSION = "2.0"
PROMPT = "\n$ "

MAX_PROCESOS = 15          # filas por defecto en 'misprocesos'
ESPERA_TERMINAR_S = 3      # segundos que se espera a que un proceso termine

# Protecciones de 'matarproceso': terminar estos procesos puede
# dejar el sistema inestable o cerrarlo.
PIDS_PROTEGIDOS = frozenset({0, 1, 4})
PROCESOS_PROTEGIDOS = frozenset({
    "system", "system idle process", "registry", "smss.exe", "csrss.exe",
    "wininit.exe", "winlogon.exe", "services.exe", "lsass.exe",
    "init", "systemd",
})