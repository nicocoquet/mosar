from pathlib import Path

from config import load_config, project_path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = load_config()
STATISTICS_PAGES = CONFIG["publication"]["statistics"]["pages"]

OUTPUTS = {
    lang: project_path(page["output"])
    for lang, page in STATISTICS_PAGES.items()
}

INTRO_FILES = {
    lang: project_path(page["intro"])
    for lang, page in STATISTICS_PAGES.items()
}

DOWNLOADS = ROOT / "docs/downloads"
