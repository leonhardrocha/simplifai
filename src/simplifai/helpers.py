""" This module contains helper functions for simplifai. """

import os
from enum import Enum
import torch


class Split(Enum):
    """
    Enum class for specifying the level to split a filename at.
    """

    PATH_HEAD = "PATH_HEAD"
    PATH_TAIL = "PATH_TAIL"
    BASENAME = "BASENAME"
    DIRNAME = "DIRNAME"
    EXTENSION = "EXTENSION"


def get_split_part(
    filename: str,
    split_level: Split = None,
    sep=" ",
    split_index: int = 0,
    normalize=False,
):
    """
    Get a specific part of a filename based on the specified split level and index.

    Args:
        filename (str): The name of the file.
        split_level (Split, optional): The level to split the filename at:
             PATH_HEAD, PATH_TAIL, BASENAME, DIRNAME, EXTENSION. Defaults to None.
        sep (str, optional): The separator to split the filename at. Defaults to ' '.
        split_index (int, optional): The index of the split part to return. Defaults to 0.
        normalize (bool, optional): Whether to normalize the filename lowercase. Defaults to False.

    Returns:
        str: The specified split part of the filename.
    """
    path, tail = os.path.split(filename)
    basename, extension = os.path.splitext(tail)
    switch_dict = {
        Split.PATH_HEAD: path,
        Split.PATH_TAIL: tail,
        Split.BASENAME: basename,
        Split.EXTENSION: extension,
    }
    filename = switch_dict.get(split_level, basename)
    filename = filename.split(sep)[split_index]
    if normalize:
        filename = filename.lower()
    return filename


def get_label_config(label_reader):
    """
    Generate a dictionary mapping each unique label in `label_reader` to its corresponding index.

    Parameters:
        label_reader (iterable): An iterable containing the labels.

    Returns:
        dict: A dictionary where the keys are the unique labels and the values are their corresponding indices.
    """
    labels = set(label_reader)
    label_dict = {}
    for idx, label in enumerate(labels):
        label_dict[label] = idx
    return label_dict


def get_split_part_as_index(*args, **kwargs):
    """
    Get the index corresponding to a split part from a label configuration.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
            label_config (dict): A dictionary mapping split parts to their corresponding indices.

    Returns:
        int or None: The index corresponding to the split part in the label configuration, or
             None if the split part is not found.
    """
    label_config = kwargs.pop("label_config")
    part = get_split_part(*args, **kwargs)
    return label_config.get(part)


def get_split_part_as_tensor(*args, **kwargs):
    """
    Get a tensor representation of a split part from a label configuration.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
            label_config (dict): A dictionary mapping split parts to their corresponding indices.

    Returns:
        torch.Tensor: A tensor containing the index corresponding to the split part in the label configuration.
    """
    part = get_split_part_as_index(*args, **kwargs)
    return torch.Tensor([part])
