from io import BytesIO
from os import listdir
from os.path import isdir, isfile, abspath, join
from typing import Dict, Tuple, Union


def path_to_BytesIO(source: str, extension: Union[Tuple[str], str] = "") -> Dict[str, BytesIO]:
    '''
    This function converts a path to a file o a path to a folder containing more than one file,
    in a dictionary of BytesIO data ordered by a key equal to the filename.

        Parameters:
        -----------
        source (str): String containing the path to the file or the folder
        extension(str): Extension of the file to be processes (default: "")

        Returns:
        --------
            dataset (Dict[BytesIO]): Dictionary of BytesIO of the selected files ordered by filename
    '''
    if source == "" or source == None:
        raise ValueError

    dataset = {}
    path = abspath(source)

    if isdir(path):
        for filename in listdir(path):
            if extension != "":
                if filename.endswith(extension) == False:
                    continue

            filepath = join(path, filename)
            with open(filepath, 'rb') as file:
                dataset[filename] = BytesIO(file.read())

    elif isfile(path):
        filename = path.split("/")[-1]      #Linux only
        if extension != "":
            if path.endswith(extension) == False:
                raise ValueError
        with open(path, 'rb') as file:
            dataset[filename] = BytesIO(file.read())

    else:
        raise ValueError
    
    return dataset