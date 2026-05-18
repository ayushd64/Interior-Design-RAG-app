from pathlib import Path

def tree_dirs(path=".", prefix=""):
    path = Path(path)
    if not path.is_dir():
        raise ValueError(f"{path} is not a directory")
    
    dirs = sorted([d for d in path.iterdir() if d.is_dir()])

    for i, d in enumerate(dirs):
        is_last = (i == len(dirs) - 1)
        print(prefix + ("└── " if is_last else "├── ") + d.name)
        new_prefix = prefix + ("    " if is_last else "│   ")
        tree_dirs(d, new_prefix)

tree_dirs()