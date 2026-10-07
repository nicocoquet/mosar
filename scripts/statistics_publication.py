from config import load_config, project_path


CONFIG = load_config()
STATISTICS_PUBLICATION = CONFIG["publication"]["statistics"]
STATISTICS_PAGES = STATISTICS_PUBLICATION["pages"]

OUTPUTS = {
    lang: project_path(page["output"])
    for lang, page in STATISTICS_PAGES.items()
}

INTRO_FILES = {
    lang: project_path(page["intro"])
    for lang, page in STATISTICS_PAGES.items()
}

DOWNLOADS = project_path(STATISTICS_PUBLICATION["downloads"])