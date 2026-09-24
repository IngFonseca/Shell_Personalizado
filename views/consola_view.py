"""Vista: toda la entrada/salida por consola. No contiene lógica del sistema."""
import os
import platform
from typing import List, Sequence, Tuple

from tabulate import tabulate

import config


class ConsolaView:
    # ---------- entrada ----------
    def pedir_comando(self) -> str:
        return input(config.PROMPT)

    def preguntar(self, texto: str) -> str:
        return input(texto).strip()

    def confirmar(self, pregunta: str) -> bool:
        respuesta = input(f"{pregunta} [s/N]: ").strip().lower()
        return respuesta in ("s", "si", "sí", "y", "yes")

    # ---------- mensajes ----------
    def mensaje(self, texto: str = "") -> None:
        print(texto)

    def exito(self, texto: str) -> None:
        print(f"[OK] {texto}")

    def advertencia(self, texto: str) -> None:
        print(f"[!] {texto}")

    def error(self, texto: str) -> None:
        print(f"[ERROR] {texto}")

    def limpiar(self) -> None:
        os.system("cls" if platform.system() == "Windows" else "clear")

    def mostrar_bienvenida(self) -> None:
        print("=========================================")
        print(f"  {config.NOMBRE} - VERSIÓN {config.VERSION}")
        print("  Escriba 'ayudame' para ver los comandos")
        print("=========================================")

    def mostrar_despedida(self) -> None:
        print("Saliendo del shell. ¡Hasta pronto!")

    # ---------- utilidades de formato ----------
    @staticmethod
    def _abrir(titulo: str) -> str:
        cabecera = f"=== {titulo} ==="
        print(f"\n{cabecera}")
        return "=" * len(cabecera)

    @staticmethod
    def _cerrar(pie: str) -> None:
        print(f"{pie}\n")

    # ---------- pantallas ----------
    def mostrar_ayuda(self, comandos: Sequence[Tuple[str, str, str]]) -> None:
        pie = self._abrir("COMANDOS DISPONIBLES")
        filas = [[f"{nombre} {uso}".strip(), desc] for nombre, uso, desc in comandos]
        print(tabulate(filas, headers=["Comando", "Descripción"], tablefmt="grid"))
        self._cerrar(pie)

    def mostrar_fecha_hora(self, fh) -> None:
        pie = self._abrir("FECHA Y HORA DEL SISTEMA")
        print(f"Fecha: {fh.fecha}")
        print(f"Hora: {fh.hora}")
        print(f"Timestamp UNIX: {fh.timestamp}")
        self._cerrar(pie)

    def mostrar_procesos(self, procesos: List, total: int) -> None:
        pie = self._abrir("PROCESOS EN EJECUCIÓN")
        filas = [[p.pid, p.nombre, p.usuario, f"{p.memoria_pct:.2f}%"] for p in procesos]
        print(tabulate(filas, headers=["PID", "Nombre", "Usuario", "Memoria"], tablefmt="grid"))
        print(f"Mostrando {len(procesos)} de {total} procesos (ordenados por memoria)")
        self._cerrar(pie)

    def mostrar_info_sistema(self, i) -> None:
        pie = self._abrir("INFORMACIÓN DEL SISTEMA")
        print(f"Sistema operativo: {i.sistema_operativo}")
        print(f"Nombre del equipo: {i.equipo}")
        print(f"Procesador: {i.procesador}")
        print(f"Arquitectura: {i.arquitectura}")
        print(f"Memoria total: {i.memoria_total_gb:.2f} GB")
        print(f"Memoria usada: {i.memoria_usada_gb:.2f} GB ({i.memoria_pct}%)")
        print(f"Núcleos físicos: {i.nucleos_fisicos}")
        print(f"Núcleos lógicos: {i.nucleos_logicos}")
        print(f"Uso de CPU: {i.uso_cpu_pct}%")
        self._cerrar(pie)

    def mostrar_archivos(self, ruta: str, archivos: List) -> None:
        pie = self._abrir(f"ARCHIVOS EN {ruta}")
        if not archivos:
            print("(directorio vacío)")
        else:
            filas = [
                [
                    a.nombre,
                    "Directorio" if a.es_directorio else "Archivo",
                    "-" if a.tamano_kb is None else f"{a.tamano_kb:.2f} KB",
                    a.modificado or "-",
                ]
                for a in archivos
            ]
            print(tabulate(filas, headers=["Nombre", "Tipo", "Tamaño", "Modificado"], tablefmt="grid"))
        self._cerrar(pie)

    def mostrar_red(self, r) -> None:
        pie = self._abrir("INFORMACIÓN DE RED")
        print(f"Nombre del host: {r.host}")
        print(f"Dirección IP: {r.ip_principal or 'No disponible'}")
        print("\nInterfaces de red:")
        if not r.interfaces:
            print("  (ninguna interfaz IPv4 detectada)")
        for i in r.interfaces:
            print(f"  {i.nombre}:")
            print(f"    IP: {i.ip}")
            print(f"    Máscara de red: {i.mascara}")
        print("\nEstadísticas:")
        print(f"  Datos enviados: {r.mb_enviados:.2f} MB")
        print(f"  Datos recibidos: {r.mb_recibidos:.2f} MB")
        self._cerrar(pie)

    def mostrar_discos(self, discos: List) -> None:
        pie = self._abrir("ESPACIO EN DISCO")
        if not discos:
            print("No se encontraron unidades accesibles.")
        else:
            filas = [
                [d.dispositivo, d.punto_montaje, d.sistema_archivos,
                 f"{d.total_gb:.2f} GB", f"{d.usado_gb:.2f} GB",
                 f"{d.libre_gb:.2f} GB", f"{d.porcentaje}%"]
                for d in discos
            ]
            print(tabulate(
                filas,
                headers=["Unidad", "Montaje", "Sist. archivos", "Total", "Usado", "Libre", "% Uso"],
                tablefmt="grid",
            ))
        self._cerrar(pie)