import logging
import os
import shutil

import cv2

from typing import AnyStr

import numpy as np

_logger = logging.getLogger("app")


def save_to_file(file_name, data, is_img: bool):
    try:
        if is_img:
            cv2.imwrite(file_name, data)
        else:
            with open(file_name, 'w') as f:
                f.write(data)
    except FileNotFoundError:
        _logger.warning(f"The <{file_name}> directory does not exist")
        raise FileNotFoundError


def saving(output_folder_filename, time_form, content, frame, is_html):
    """Creating dir, files raising FileNotFoundError, FileExistsError"""
    folder_name = output_folder_filename + "/" + time_form
    try:
        os.makedirs(folder_name)
    except FileExistsError:
        _logger.warning(f"Folder Exists. Script finished. folder_name <{folder_name}>")
        raise FileExistsError
    else:
        _logger.info(f"Folder Created. folder_name <{folder_name}>")

    fn = "index.html" if is_html else "text.txt"
    file_name_txt = folder_name + "/" + fn
    save_to_file(file_name_txt, content, False)

    file_name_img = folder_name + "/" + "image1.png"
    save_to_file(file_name_img, frame, True)


def create_dir(folder_name: str) -> None:
    try:
        os.makedirs(folder_name)
    except FileExistsError:
        _logger.warning(f"Folder Exists. Removing.. , folder_name <{folder_name}>")
        shutil.rmtree(folder_name, ignore_errors=True)
        os.makedirs(folder_name)

    _logger.info(f"Folder Created. folder_name <{folder_name}>")