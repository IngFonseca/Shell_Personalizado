"""Controlador: interpreta los comandos y coordina modelo y vista."""
from dataclasses import dataclass
from typing import Callable, Optional

import config
from models.sistema import ErrorSistema


@dataclass(frozen=True)
class Comando:
    nombre: str
    descripcion: str
    manejador: Callable[[str], None]
    uso: str = ""


class ShellController:
    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self._activo = False
        self._comandos = {c.nombre: c for c in self._definir_comandos()}

    def _definir_comandos(self):
        return [
            Comando("mihorario", "Muestra la fecha y hora actual del sistema", self._cmd_horario),
            Comando("misprocesos", "Lista los procesos que más memoria usan", self._cmd_procesos, "[cantidad]"),
            Comando("matarproceso", "Termina un proceso por su PID", self._cmd_matar, "[pid]"),
            Comando("ayudame", "Muestra esta lista de comandos", self._cmd_ayuda),
            Comando("infopc", "Muestra información del sistema", self._cmd_info_pc),
            Comando("misarchivos", "Lista archivos del directorio actual o de la ruta indicada", self._cmd_archivos, "[ruta]"),
            Comando("mired", "Muestra información de red", self._cmd_red),
            Comando("miespacio", "Muestra espacio en disco", self._cmd_espacio),
            Comando("limpiar", "Limpia la pantalla", self._cmd_limpiar),
            Comando("salir", "Sale del shell", self._cmd_salir),
        ]

    # ---------- ciclo principal ----------
    def ejecutar(self) -> None:
        self.vista.mostrar_bienvenida()
        self._activo = True
        while self._activo:
            try:
                self.procesar(self.vista.pedir_comando())
            except EOFError:                    # Ctrl+Z / Ctrl+D
                self.vista.mensaje()
                self._cmd_salir("")
            except KeyboardInterrupt:           # Ctrl+C
                self.vista.mensaje("\nInterrumpido. Use 'salir' para cerrar el shell.")

    def procesar(self, linea: str) -> None:
        nombre, _, argumento = linea.strip().partition(" ")
        nombre = nombre.lower()
        argumento = argumento.strip().strip("\"'")
        if not nombre:
            return

        comando = self._comandos.get(nombre)
        if comando is None:
            self.vista.error(f"Comando '{nombre}' no reconocido. Use 'ayudame' para ver la lista de comandos.")
            return

        try:
            comando.manejador(argumento)
        except ErrorSistema as e:
            self.vista.error(str(e))
        except Exception as e:  # último recurso: el shell nunca debe caerse
            self.vista.error(f"Error inesperado: {e}")

    # ---------- comandos ----------
    def _cmd_horario(self, _arg: str) -> None:
        self.vista.mostrar_fecha_hora(self.modelo.fecha_hora())

    def _cmd_procesos(self, arg: str) -> None:
        limite = config.MAX_PROCESOS
        if arg:
            limite = self._entero(arg, "La cantidad", minimo=1)
            if limite is None:
                return
        procesos, total = self.modelo.listar_procesos(limite)
        self.vista.mostrar_procesos(procesos, total)

    def _cmd_matar(self, arg: str) -> None:
        texto = arg or self.vista.preguntar("Ingrese el PID del proceso a terminar: ")
        pid = self._entero(texto, "El PID", minimo=0)
        if pid is None:
            return

        proceso = self.modelo.obtener_proceso(pid)
        if not self.vista.confirmar(f"¿Terminar '{proceso.nombre}' (PID {pid})?"):
            self.vista.mensaje("Operación cancelada.")
            return

        if self.modelo.terminar_proceso(pid):
            self.vista.exito(f"Proceso {proceso.nombre} (PID: {pid}) terminado correctamente.")
        else:
            self.vista.advertencia(
                f"Se envió la señal de terminación a {proceso.nombre} (PID: {pid}), "
                "pero el proceso sigue activo."
            )

    def _cmd_ayuda(self, _arg: str) -> None:
        self.vista.mostrar_ayuda([(c.nombre, c.uso, c.descripcion) for c in self._comandos.values()])

    def _cmd_info_pc(self, _arg: str) -> None:
        self.vista.mostrar_info_sistema(self.modelo.info_sistema())

    def _cmd_archivos(self, arg: str) -> None:
        ruta, archivos = self.modelo.listar_archivos(arg or None)
        self.vista.mostrar_archivos(ruta, archivos)

    def _cmd_red(self, _arg: str) -> None:
        self.vista.mostrar_red(self.modelo.info_red())

    def _cmd_espacio(self, _arg: str) -> None:
        self.vista.mostrar_discos(self.modelo.discos())

    def _cmd_limpiar(self, _arg: str) -> None:
        self.vista.limpiar()

    def _cmd_salir(self, _arg: str) -> None:
        self.vista.mostrar_despedida()
        self._activo = False

    # ---------- utilidades ----------
    def _entero(self, texto: str, etiqueta: str, minimo: int) -> Optional[int]:
        try:
            valor = int(texto)
        except ValueError:
            self.vista.error(f"{etiqueta} debe ser un número entero.")
            return None
        if valor < minimo:
            self.vista.error(f"{etiqueta} debe ser un número entero mayor o igual a {minimo}.")
            return None
        return valor