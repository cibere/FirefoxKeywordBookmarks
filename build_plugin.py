import sys
import tempfile
import zipfile
from pathlib import Path


def main(archive_name: str):
    prod_file = Path("DELETE-ME-FOR-LOGS.flogin.prod")
    prod_file.write_text("")

    files = [
        Path(fp)
        for fp in (
            "SettingsTemplate.yaml",
            "plugin.json",
            "main.py",
        )
    ]
    files.append(prod_file)
    ignore_exts = (".dist-info", ".pyc", "__pycache__")

    files.extend(Path("assets").iterdir())
    files.extend(Path("plugin").iterdir())

    lib_dir = Path("lib")
    files.extend(
        [
            file
            for file in lib_dir.rglob("*")
            if not file.parent.parent.name.endswith(
                ignore_exts  # some deps include a licenses dir inside of their dist-info dir
            )
            and not file.parent.name.endswith(ignore_exts)
            and not file.name.endswith(ignore_exts)
        ]
    )

    if archive_name == "--debug":
        manager = tempfile.TemporaryFile("w")  # noqa: SIM115
        archive_name = manager.name
    else:
        manager = zipfile.ZipFile(archive_name, "w")

    with manager as f:
        for file in files:
            f.write(str(file))
            print(f"Added {file}")
    print(f"\nDone. Archive saved to {archive_name}")


if __name__ == "__main__":
    main(sys.argv[-1])
