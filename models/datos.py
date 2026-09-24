"""Estructuras de datos que devuelve el modelo (sin lógica ni impresión)."""
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class FechaHora:
    fecha: str
    hora: str
    timestamp: int


@dataclass(frozen=True)
class ProcesoInfo:
    pid: int
    nombre: str
    usuario: str
    memoria_pct: float


@dataclass(frozen=True)
class InfoSistema:
    sistema_operativo: str
    equipo: str
    procesador: str
    arquitectura: str
    memoria_total_gb: float
    memoria_usada_gb: float
    memoria_pct: float
    nucleos_fisicos: Optional[int]
    nucleos_logicos: Optional[int]
    uso_cpu_pct: float


@dataclass(frozen=True)
class ArchivoInfo:
    nombre: str
    es_directorio: bool
    tamano_kb: Optional[float]
    modificado: Optional[str]


@dataclass(frozen=True)
class InterfazRed:
    nombre: str
    ip: str
    mascara: str


@dataclass(frozen=True)
class InfoRed:
    host: str
    ip_principal: Optional[str]
    interfaces: List[InterfazRed]
    mb_enviados: float
    mb_recibidos: float


@dataclass(frozen=True)
class Disco:
    dispositivo: str
    punto_montaje: str
    sistema_archivos: str
    total_gb: float
    usado_gb: float
    libre_gb: float
    porcentaje: float