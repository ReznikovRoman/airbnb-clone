import os
import pathlib
from zipfile import ZipFile


def main() -> None:
    base_dir = pathlib.Path(__file__).resolve().parent
    home_dir = base_dir.parent

    main_file = base_dir / "main.py"
    requirements_file = home_dir / "requirements.txt"
    with ZipFile(f"{home_dir}/build.zip", "w") as zip_file:
        zip_file.write(main_file, os.path.basename(main_file))
        zip_file.write(requirements_file, os.path.basename(requirements_file))


if __name__ == '__main__':
    main()
