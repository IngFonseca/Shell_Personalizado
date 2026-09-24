"""Modelo: obtiene información del sistema con psutil. No imprime nada."""
import datetime
import os
import platform
import socket
from typing import List, Optional, Tuple

import psutil

import config
from models.datos import (ArchivoInfo, Disco, FechaHora, InfoRed, InfoSistema,
                          InterfazRed, ProcesoInfo)

GB = 1024 ** 3
MB = 1024 ** 2


class ErrorSistema(Exception):
    """Error base del modelo (el mensaje es apto para mostrarse al usuario)."""


class ProcesoNoExiste(ErrorSistema):
    pass


class PermisoDenegado(ErrorSistema):
    pass


class ProcesoProtegido(ErrorSistema):
    pass


class ServicioSistema:
    # ---------- fecha y hora ----------
    def fecha_hora(self) -> FechaHora:
        ahora = datetime.datetime.now()
        return FechaHora(
            fecha=ahora.strftime("%d/%m/%Y"),
            hora=ahora.strftime("%H:%M:%S"),
            timestamp=int(ahora.timestamp()),
        )

    # ---------- procesos ----------
    def listar_procesos(self, limite: int = config.MAX_PROCESOS) -> Tuple[List[ProcesoInfo], int]:
        """Devuelve (los 'limite' procesos con más memoria, total de procesos)."""
        procesos = []
        for proc in psutil.process_iter(["pid", "name", "username", "memory_percent"]):
            info = proc.info  # los datos inaccesibles llegan como None
            procesos.append(ProcesoInfo(
                pid=info["pid"],
                nombre=info["name"] or "?",
                usuario=info["username"] or "-",
                memoria_pct=info["memory_percent"] or 0.0,
            ))
        procesos.sort(key=lambda p: p.memoria_pct, reverse=True)
        return procesos[:limite], len(procesos)

    def obtener_proceso(self, pid: int) -> ProcesoInfo:
        self._validar_pid(pid)
        try:
            proc = psutil.Process(pid)
            nombre = proc.name()
            self._validar_nombre(pid, nombre)
            return ProcesoInfo(pid, nombre, self._usuario(proc), self._memoria(proc))
        except psutil.NoSuchProcess:
            raise ProcesoNoExiste(f"No existe un proceso con PID {pid}.") from None
        except psutil.AccessDenied:
            raise PermisoDenegado("No tiene permisos para acceder a este proceso.") from None

    def terminar_proceso(self, pid: int) -> bool:
        """Solicita terminar el proceso. True si terminó dentro del tiempo de espera."""
        self._validar_pid(pid)
        try:
            proc = psutil.Process(pid)
            self._validar_nombre(pid, proc.name())
            proc.terminate()
        except psutil.NoSuchProcess:
            raise ProcesoNoExiste(f"No existe un proceso con PID {pid}.") from None
        except psutil.AccessDenied:
            raise PermisoDenegado("No tiene permisos para terminar este proceso.") from None

        try:
            proc.wait(timeout=config.ESPERA_TERMINAR_S)
            return True
        except psutil.TimeoutExpired:
            return False
        except psutil.NoSuchProcess:
            return True

    @staticmethod
    def _validar_pid(pid: int) -> None:
        if pid == os.getpid() or pid in config.PIDS_PROTEGIDOS:
            raise ProcesoProtegido(f"El proceso con PID {pid} está protegido y no puede terminarse.")

    @staticmethod
    def _validar_nombre(pid: int, nombre: str) -> None:
        if nombre.lower() in config.PROCESOS_PROTEGIDOS:
            raise ProcesoProtegido(f"'{nombre}' (PID {pid}) es un proceso crítico del sistema y está protegido.")

    @staticmethod
    def _usuario(proc: psutil.Process) -> str:
        try:
            return proc.username()
        except psutil.Error:
            return "-"

    @staticmethod
    def _memoria(proc: psutil.Process) -> float:
        try:
            return proc.memory_percent()
        except psutil.Error:
            return 0.0

    # ---------- sistema ----------
    def info_sistema(self) -> InfoSistema:
        mem = psutil.virtual_memory()
        return InfoSistema(
            sistema_operativo=f"{platform.system()} {platform.release()} ({platform.version()})",
            equipo=platform.node(),
            procesador=platform.processor() or "Desconocido",
            arquitectura=platform.architecture()[0],
            memoria_total_gb=mem.total / GB,
            memoria_usada_gb=mem.used / GB,
            memoria_pct=mem.percent,
            nucleos_fisicos=psutil.cpu_count(logical=False),
            nucleos_logicos=psutil.cpu_count(),
            uso_cpu_pct=psutil.cpu_percent(interval=1),  # bloquea 1 s para medir
        )

    # ---------- archivos ----------
    def listar_archivos(self, ruta: Optional[str] = None) -> Tuple[str, List[ArchivoInfo]]:
        ruta = os.path.abspath(ruta or os.getcwd())
        if not os.path.isdir(ruta):
            raise ErrorSistema(f"'{ruta}' no es un directorio válido.")
        try:
            nombres = os.listdir(ruta)
        except PermissionError:
            raise PermisoDenegado(f"No tiene permisos para leer '{ruta}'.") from None

        archivos = []
        for nombre in nombres:
            completa = os.path.join(ruta, nombre)
            try:
                st = os.stat(completa)
                es_dir = os.path.isdir(completa)
                archivos.append(ArchivoInfo(
                    nombre=nombre,
                    es_directorio=es_dir,
                    tamano_kb=None if es_dir else st.st_size / 1024,
                    modificado=datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
                ))
            except OSError:
                archivos.append(ArchivoInfo(nombre, False, None, None))
        archivos.sort(key=lambda a: (not a.es_directorio, a.nombre.casefold()))
        return ruta, archivos

    # ---------- red ----------
    def info_red(self) -> InfoRed:
        host = socket.gethostname()
        try:
            ip = socket.gethostbyname(host)
        except OSError:
            ip = None

        interfaces = []
        for nombre, direcciones in psutil.net_if_addrs().items():
            for d in direcciones:
                if d.family == socket.AF_INET:
                    interfaces.append(InterfazRed(nombre, d.address, d.netmask or "-"))
                    break

        io = psutil.net_io_counters()
        return InfoRed(host, ip, interfaces, io.bytes_sent / MB, io.bytes_recv / MB)

    # ---------- discos ----------
    def discos(self) -> List[Disco]:
        resultado = []
        for part in psutil.disk_partitions(all=False):
            try:
                uso = psutil.disk_usage(part.mountpoint)
            except OSError:      # incluye PermissionError (unidades sin medio, etc.)
                continue
            resultado.append(Disco(
                dispositivo=part.device,
                punto_montaje=part.mountpoint,
                sistema_archivos=part.fstype or "-",
                total_gb=uso.total / GB,
                usado_gb=uso.used / GB,
                libre_gb=uso.free / GB,
                porcentaje=uso.percent,
            ))
        return resultado