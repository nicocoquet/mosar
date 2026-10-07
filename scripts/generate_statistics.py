from statistics_build import build
from statistics_data import derive, read_rows
from statistics_project import DEFAULT_SOURCE
from statistics_publication import DOWNLOADS, OUTPUTS


def main():
    DOWNLOADS.mkdir(parents=True, exist_ok=True)

    rows = read_rows(DEFAULT_SOURCE)
    data = derive(rows, DEFAULT_SOURCE)

    for lang, path in OUTPUTS.items():
        path.write_text(build(data, lang), encoding="utf-8")

    opened = sum(v["open"] for v in data["level_access"].values())
    print(
        f"Corpus : {data['total']} | accès ouvert={opened} | "
        f"droits={dict(data['rights'])}"
    )


if __name__ == "__main__":
    main()
