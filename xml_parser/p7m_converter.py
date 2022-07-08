from io import BytesIO
from base64 import b64decode
from OpenSSL import crypto
from OpenSSL._util import (ffi as _ffi, lib as _lib,)
from typing import Callable, Dict


def p7m_to_xml(p7m_stream: BytesIO) -> BytesIO:
    '''
    Convert a .xml.p7m BytesIO stream into a regular .xml BytesIO stream.

        Parameters:
        -----------
            p7m_stream (BytesIO): BytesIO stream of the .xml.p7m file to convert
        
        Returns:
        --------
            xml_stream (BytesIO): BytesIO stream of the .xml output file
    '''
    
    p7m_data = p7m_stream.read()
    
    try:
        p7m = crypto.load_pkcs7_data(crypto.FILETYPE_ASN1, p7m_data)
    
    except:
        buffer = b64decode(p7m_data)
        p7m = crypto.load_pkcs7_data(crypto.FILETYPE_ASN1, buffer)

    bio_out =crypto._new_mem_buf()
    res = _lib.PKCS7_verify(p7m._pkcs7, _ffi.NULL, _ffi.NULL, _ffi.NULL, bio_out, _lib.PKCS7_NOVERIFY|_lib.PKCS7_NOSIGS)

    if res != 1:
        raise RuntimeError
    
    try:
        data = crypto._bio_to_string(bio_out).decode("utf-8")
    except UnicodeDecodeError:
        data = crypto._bio_to_string(bio_out).decode("windows-1252")
    
    return BytesIO(data.encode('utf-8'))


def group_convert_p7m_to_xml(instream: Dict[str, BytesIO], verbose: bool = False, exception_handler: Callable[[Exception, str], None] = None) -> Dict[str, BytesIO]:
    '''
    Converts all the .xml.p7m file contained into a 'source_folder' to a regular .xml file in a 'destination_folder'.

        Parameters:
        -----------
            instream (Dict[str, BytesIO]): Dictionary of BytesIO stream, ordered by filename, containing
                the .xml.p7m to be converted.
            verbose (bool): If set to True will report the success of the conversion process on terminal.
            exception_handler (Callable[[Exception, str], None]): function taking as arguments the exception
                occurred and the filename, capable of handling a .p7m conversion exception.
        
        Returns:
        --------
            outstream (Dict[str, BytesIO]): Dictionary of BytesIO stream, ordered by filename, containing
                the .xml to be converted
    '''

    if type(instream) == dict:
        if instream == {}:
            raise ValueError
    else:
        raise ValueError

    outstream = {}

    for filename, stream in instream.items():

        newname = filename.strip(".p7m")

        try:
            buffer = p7m_to_xml(stream)

        except Exception as exception:
            if exception_handler != None:
                exception_handler(exception, filename)
            else:
                if verbose == True:
                    print(""" -> Parsing '{}': \u001b[31;1mFAILED\u001b[0m""".format(filename))
                    print("\t{}".format(exception))

        else:
            outstream[newname] = buffer

    return outstream

