from statistics_data import OUTPUTS, DOWNLOADS, read_rows, derive
from statistics_build import build


def main():
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    data = derive(read_rows())
    for lang, path in OUTPUTS.items():
        path.write_text(build(data, lang), encoding="utf-8")
    opened = sum(v["open"] for v in data["level_access"].values())
    print(f"Corpus : {data['total']} | accès ouvert={opened} | droits={dict(data['rights'])}")


if __name__ == "__main__":
    main()
