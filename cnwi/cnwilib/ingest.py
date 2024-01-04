from pathlib import Path
from shutil import copytree


from pathlib import Path
from shutil import copytree


def ingest_data(src: Path, dest: Path) -> None:
    """
    Ingests data from the source directory to the destination directory.

    Args:
        src (Path): The path to the source directory.
        dest (Path): The path to the destination directory.

    Returns:
        None
    """
    copytree(src, dest, dirs_exist_ok=True)
