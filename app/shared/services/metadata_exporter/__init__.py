from app.shared.services.metadata_exporter.__base__ import Exporter
from app.shared.services.metadata_exporter.csv_exporter import CSVExporter

__all__ = [
    'Exporter',
    'add_exporter',
    'get_exporter',
    'CSVExporter',
]

_exporters: dict[tuple[str, str], Exporter] = {}


def add_exporter(supported_format: str, toolkit: str, exporter: Exporter) -> None:
    _exporters[supported_format, toolkit] = exporter


def get_exporter(format: str, toolkit: str) -> Exporter | None:
    return _exporters.get((format, toolkit))
