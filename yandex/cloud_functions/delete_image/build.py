import os
import pathlib
from zipfile import ZipFile


def main() -> None:
    base_dir = pathlib.Path(__file__).resolve().parent
    src_dir = base_dir / "src"

    main_file = src_dir / "main.py"
    requirements_file = base_dir / "requirements.txt"
    with ZipFile(f"{base_dir}/build.zip", "w") as zip_file:
        zip_file.write(main_file, os.path.basename(main_file))
        zip_file.write(requirements_file, os.path.basename(requirements_file))


if __name__ == '__main__':
    main()
