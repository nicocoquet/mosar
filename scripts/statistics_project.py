"""Adaptateur entre la configuration du projet et le moteur statistique."""

from config import load_config, project_path
from statistics_data import StatisticsSource


CONFIG = load_config()

DEFAULT_SOURCE = StatisticsSource(
    xlsx=project_path(CONFIG["data"]["file"]),
    sheet=CONFIG["data"]["sheet"],
    columns=CONFIG["columns"],
)