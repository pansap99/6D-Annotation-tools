import os
import tyro
import dataclasses

@dataclasses.dataclass
class rename_images_args:
    folder: str

def rename_images(folder: str):
    """Rename images in a folder to a sequential number."""
    for idx, filename in enumerate(os.listdir(folder)):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            new_filename = "{:06d}.{}".format(idx+1, filename.split('.')[-1])
            os.rename(os.path.join(folder, filename), os.path.join(folder, new_filename))


if __name__ == "__main__":
    args = tyro.cli(rename_images_args)
    rename_images(args.folder)
