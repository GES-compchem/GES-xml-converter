from os import listdir, mkdir
from os.path import isfile, isdir, abspath, join
from OpenSSL import crypto
from OpenSSL._util import (ffi as _ffi, lib as _lib,)

def p7m_to_xml(p7m_path: str, xml_path: str) -> None:
    '''
    Convert a .xml.p7m file into a regular .xml file.

        Parameters:
        -----------
            p7m_path (str): path to the .xml.p7m file to convert
            xml_path (str): path to the .xml output file
    '''

    if isfile(p7m_path) == False:
        raise ValueError
    
    p7m_data = None

    with open(p7m_path, 'rb') as p7m_file:
        p7m_data = p7m_file.read()
    
    
    p7m = crypto.load_pkcs7_data(crypto.FILETYPE_ASN1, p7m_data)

    bio_out =crypto._new_mem_buf()
    res = _lib.PKCS7_verify(p7m._pkcs7, _ffi.NULL, _ffi.NULL, _ffi.NULL, bio_out, _lib.PKCS7_NOVERIFY|_lib.PKCS7_NOSIGS)

    if res == 1:
        data = crypto._bio_to_string(bio_out).decode("utf-8")

        with open(xml_path, 'w') as xml_file:
            xml_file.write(data)
        
    else:
        raise RuntimeError


def group_convert_p7m_to_xml(source_folder: str, destination_folder: str = None, verbose: bool = False) -> None:
    '''
    Converts all the .xml.p7m file contained into a 'source_folder' to a regular .xml file in a 'destination_folder'.

        Parameters:
        -----------
            source_folder (str): folder in which the .xml.p7m can be located
            destination_folder (str): destination folder for the .xml output files (default: source_folder)
            verbose (bool): If set to True will report the success of the conversion process on terminal
    '''

    if isdir(source_folder) == False:
        raise ValueError

    source_folder = abspath(source_folder)

    if destination_folder == None:
        destination_folder = join(source_folder, "tmp")
    
    destination_folder = abspath(destination_folder)

    if isdir(destination_folder) == False:
        mkdir(destination_folder)

    for filename in listdir(source_folder):
        if filename.endswith(".xml.p7m"):
            
            p7m_path = join(source_folder, filename)
            xml_path = join(destination_folder, filename.strip(".p7m"))

            try:
                p7m_to_xml(p7m_path, xml_path)

            except:
                if verbose == True:
                    print(""" -> Parsing '{}': \u001b[31;1mFAILED\u001b[0m""".format(filename))
            
            #else:
            #    if verbose == True:
            #        print(""" -> Parsing '{}': \u001b[32;1mSUCCESS\u001b[0m""".format(filename))



    

