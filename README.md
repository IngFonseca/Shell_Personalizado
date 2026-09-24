# Shell Personalizado

Shell interactivo de consola escrito en Python para consultar información del sistema (procesos, memoria, red, discos, archivos) y administrar procesos, con comandos propios en español.

## Descripción

Este proyecto implementa un intérprete de comandos sencillo con un conjunto de comandos personalizados (`mihorario`, `misprocesos`, `matarproceso`, `infopc`, etc.). Cada comando consulta el sistema operativo a través de la librería `psutil` y muestra el resultado en tablas legibles.

El proyecto está construido siguiendo el patrón MVC (Modelo - Vista - Controlador), lo que separa claramente la obtención de datos del sistema, la presentación en consola y la interpretación de comandos, facilitando su mantenimiento y la incorporación de nuevos comandos.

## Características

- 10 comandos personalizados en español, con ayuda generada automáticamente
- Comandos con argumentos opcionales (`misprocesos 30`, `matarproceso 1234`, `misarchivos C:\Users`)
- Lista de procesos ordenada por uso de memoria
- Terminación de procesos con confirmación previa
- Protección contra terminar procesos críticos del sistema o el propio shell
- Información de sistema, CPU, memoria, red y discos
- Listado de archivos con directorios primero y soporte de rutas con espacios
- Manejo robusto de errores: el shell nunca se cierra por una excepción
- Soporte de Ctrl+C y fin de entrada (Ctrl+Z / Ctrl+D) sin volcar trazas de error
- Compatible con Windows, Linux y macOS
- Arquitectura MVC para facilitar mantenimiento y escalabilidad

## Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `mihorario` | Muestra la fecha y hora actual del sistema |
| `misprocesos [cantidad]` | Lista los procesos que más memoria usan (15 por defecto) |
| `matarproceso [pid]` | Termina un proceso por su PID, pidiendo confirmación |
| `ayudame` | Muestra la lista de comandos |
| `infopc` | Muestra información del sistema (SO, CPU, memoria) |
| `misarchivos [ruta]` | Lista archivos del directorio actual o de la ruta indicada |
| `mired` | Muestra información de red (host, IP, interfaces, tráfico) |
| `miespacio` | Muestra el espacio en disco de cada unidad |
| `limpiar` | Limpia la pantalla |
| `salir` | Cierra el shell |

Los nombres de comando no distinguen entre mayúsculas y minúsculas. Los argumentos entre corchetes son opcionales; `matarproceso` pide el PID si no se indica.

## Tecnologías

- Lenguaje: Python 3.8+
- Interfaz: Consola interactiva con tablas de `tabulate`
- Información del sistema: `psutil`
- Persistencia: ninguna (consulta el sistema en cada comando)
- Empaquetado (opcional): PyInstaller

## Requisitos

- Python >= 3.8
- pip

## Descarga

Si solo quieres usar el shell, descarga el ejecutable desde la sección
[Releases](https://github.com/IngFonseca/Shell_Personalizado/releases) (Windows, no requiere Python).

## Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/IngFonseca/Shell_Personalizado.git
cd Shell_Personalizado
```

2. (Recomendado) Crea y activa un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

Ejecuta la aplicación desde la raíz del proyecto:

```bash
python main.py
```

Ejemplo de sesión:

```
$ ayudame
$ misprocesos 5
$ matarproceso 4321
¿Terminar 'notepad.exe' (PID 4321)? [s/N]: s
[OK] Proceso notepad.exe (PID: 4321) terminado correctamente.
$ misarchivos C:\Users
$ salir
```

## Estructura del Proyecto

```
Shell_Personalizado/
├── main.py                      # Punto de entrada de la aplicación
├── config.py                    # Configuración y procesos protegidos
├── requirements.txt
├── .gitignore
├── models/                      # MODELO
│   ├── __init__.py
│   ├── datos.py                 # Estructuras de datos (dataclasses)
│   └── sistema.py               # Acceso al sistema con psutil
├── views/                       # VISTA
│   ├── __init__.py
│   └── consola_view.py          # Entrada/salida por consola (tabulate)
└── controllers/                 # CONTROLADOR
    ├── __init__.py
    └── shell_controller.py      # Interpreta comandos y coordina modelo y vista
```

| Capa | Responsabilidad |
|------|-----------------|
| **Modelo** | Consulta el sistema y devuelve datos estructurados. No imprime nada ni lee del teclado. |
| **Vista** | Muestra tablas y mensajes, y pide datos al usuario. No conoce psutil. |
| **Controlador** | Lee el comando, lo valida, llama al modelo y le pasa el resultado a la vista. |

### Cómo agregar un comando nuevo

1. Agrega un método que consulte el dato en `models/sistema.py` (y una dataclass en `models/datos.py` si hace falta).
2. Agrega un método `mostrar_...` en `views/consola_view.py`.
3. Agrega el manejador `_cmd_...` y su línea en `_definir_comandos()` de `controllers/shell_controller.py`. La ayuda se actualiza sola.

## Generar el Ejecutable (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --name Shell main.py
```

El archivo queda en `dist/Shell.exe`. Es una aplicación de consola, por lo que **no** se usa la opción `--windowed`. No se versiona en el repositorio; se distribuye desde la sección *Releases* de GitHub.

## Notas sobre Seguridad y Credenciales

- El proyecto no usa credenciales, API keys, variables de entorno ni servicios externos, y no guarda datos en disco.
- `matarproceso` siempre pide confirmación y rechaza el PID del propio shell y una lista de procesos críticos del sistema (configurable en `config.py`).
- Terminar procesos de otros usuarios o del sistema puede requerir ejecutar la consola como administrador.
- El `.gitignore` excluye archivos `.env`, claves y los archivos generados por PyInstaller (`build/`, `dist/`, `*.spec`), que pueden contener rutas locales del equipo donde se compiló.

## Roadmap

- [ ] Pruebas unitarias con pytest para el modelo y el controlador
- [ ] Historial de comandos y autocompletado
- [ ] Comando para buscar procesos por nombre
- [ ] Comandos de manipulación de archivos (copiar, mover, eliminar) con confirmación
- [ ] Salida coloreada
- [ ] Exportar resultados a archivo (CSV/TXT)

## Autor

Juan Fernando Fonseca Martínez

## Licencia

Este proyecto no especifica una licencia por el momento.

## Soporte

Para reportar problemas o sugerir mejoras:

- Abre un Issue en GitHub.
- Describe claramente el problema encontrado.
- Incluye los pasos necesarios para reproducirlo.
- Si es posible, proporciona mensajes de error o capturas de pantalla.
