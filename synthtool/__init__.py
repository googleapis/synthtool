from pathlib import Path
import shutil
import os


def copy(source: Path, destination: str=None):
    '''
    copy file(s) at source to current directory
    '''
    if destination is None:
        destination = Path('.')
    else:
        # ensure destination is a `Path`
        destination = Path(destination)

    if source.is_dir():
        _copy_to_existing_dir(source, destination)

    else:
        # copy individual file
        shutil.copy2(source, destination)


def _copy_to_existing_dir(source: Path, destination: Path):
    '''
    copies files over existing files to an existing directory
    this function does not copy empty directories
    '''
    for root, _, files in os.walk(source):
        for name in files:
            rel_path = str(Path(root).relative_to(source)).lstrip('.')
            dest_dir = os.path.join(destination, rel_path)
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, name)
            shutil.copyfile(os.path.join(root, name), dest_path)
