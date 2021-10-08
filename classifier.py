from deepface import DeepFace
import os
import sys
import operator
from pathlib import Path
import shutil
from tqdm import tqdm

image_extensions = [".jpg", ".jpeg", ".png", ".tif", ".tiff"]
WOMEN_OUTPUT_FOLDER = 'women'
MEN_OUTPUT_FOLDER = 'men'

def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry

def get_image_paths(dir_path, image_extensions=image_extensions, subdirs=False, return_Path_class=False):
    dir_path = Path (dir_path)

    result = []
    if dir_path.exists():

        if subdirs:
            gen = scantree(str(dir_path))
        else:
            gen = os.scandir(str(dir_path))

        for x in list(gen):
            if any([x.name.lower().endswith(ext) for ext in image_extensions]):
                result.append( x.path if not return_Path_class else Path(x.path) )
    return sorted(result)

def copy_files(images: list, output_path: str) -> None:
    output_path = Path(output_path)
    for i in tqdm(range(len(images)), desc='Copying and renaming', initial=0, ascii=True, total=len(images)):
        shutil.copy(images[i][0], output_path / ('%.6d%s' % (i, Path(images[i][0]).suffix)))

def main() -> None:
    """Main function"""
    if len(sys.argv) < 2:
        print('Wrong script usage. Correct usage:\n\tpython main.py <path of image folder')
        input('Press one key to continue . . .')
        exit(1)

    input_path = Path(sys.argv[1])

    images_paths = [filepath for filepath in get_image_paths(input_path)]

    women_images = []
    men_images = []

    detected = 0

    for image in images_paths:
        obj = DeepFace.analyze(img_path=image, actions=['gender', 'age'], enforce_detection=False)
        if obj['gender'] == 'Woman':
            women_images.append([image, obj['age']])
        else:
            men_images.append([image, obj['age']])
        print(f"Path: {image}, gender: {obj['gender']}, age: {obj['age']}")

    # create output folders
    if not os.path.exists(WOMEN_OUTPUT_FOLDER):
        os.mkdir(WOMEN_OUTPUT_FOLDER)
    if not os.path.exists(MEN_OUTPUT_FOLDER):
        os.mkdir(MEN_OUTPUT_FOLDER)

    # sort the image dictionaries
    women_images.sort(key=operator.itemgetter(1))
    men_images.sort(key=operator.itemgetter(1))

    copy_files(women_images, WOMEN_OUTPUT_FOLDER)
    copy_files(men_images, MEN_OUTPUT_FOLDER)


if __name__ == '__main__':
    main()
