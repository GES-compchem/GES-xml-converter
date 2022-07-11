import pytest, pathlib
from io import BytesIO
from os.path import isdir
from random import choice
from string import ascii_letters
from ges_xml_converter.bytesIO_utils import path_to_BytesIO


def random_string(length):
    return "".join([choice(ascii_letters) for _ in range(length)])


@pytest.fixture(scope="session")
def generate_random_textfiles(tmp_path_factory):
    folder = tmp_path_factory.mktemp("random_text_files")
    data = {}
    for i in range(2):
        filename = random_string(10) + ".txt"
        content = random_string(100)
        file_path = folder / filename
        file_path.write_text(content)
        data[filename] = content
    return folder, data


# Test if exception is raised when passing invalid path argument
def test_argument_exceptions():
    with pytest.raises(ValueError):
        path_to_BytesIO("")
        path_to_BytesIO(None)


# Test if exception is raised when invalid file path is given
def test_invalid_path_exceptions():
    while(True):
        invalid_path = "./" + random_string(10)
        if isdir(invalid_path) == False:
            break

    with pytest.raises(ValueError):
        path_to_BytesIO(invalid_path)


#Test the conversion of a single file given the path to the file
def test_conversion_single(generate_random_textfiles):
    
    folder, data = generate_random_textfiles
    filename = next(iter(data))

    expected = BytesIO(data[filename].encode('utf-8'))
    
    result = path_to_BytesIO(folder/filename)

    assert result[filename].read() == expected.read()


#Test the conversion of a single file given the path to the file given the file extension
def test_conversion_single_with_extension(generate_random_textfiles):
    
    folder, data = generate_random_textfiles
    filename = next(iter(data))

    expected = BytesIO(data[filename].encode('utf-8'))
    
    result = path_to_BytesIO(folder/filename, extension=".txt")

    assert result[filename].read() == expected.read()


#Test the conversion of a multiple files given the path to the folder
def test_conversion_multiple(generate_random_textfiles):
    
    folder, data = generate_random_textfiles
    result = path_to_BytesIO(folder)

    for filename, content in data.items():

        expected = BytesIO(content.encode('utf-8'))
        assert result[filename].read() == expected.read()


#Test the conversion of a multiple files given the path to the folder given the files extension
def test_conversion_multiple_with_extension(generate_random_textfiles):
    
    folder, data = generate_random_textfiles
    result = path_to_BytesIO(folder, extension=".txt")

    for filename, content in data.items():

        expected = BytesIO(content.encode('utf-8'))
        assert result[filename].read() == expected.read()


