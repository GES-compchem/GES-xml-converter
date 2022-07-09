import sys
from os.path import join, abspath, isdir
from pandas import ExcelWriter
from xml_parser.xml_parser import XML_converter
from xml_parser.p7m_converter import group_convert_p7m_to_xml
from xml_parser.bytesIO_utils import path_to_BytesIO
from xml_parser.invoices_modifier import modify_header

# Rudimental autocomplete on tab functions
import glob, readline

def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind('tab: complete')
readline.set_completer(complete)



if __name__ == "__main__":

    if len(sys.argv) == 1:
        path = input("Please select the path to the .xml and .xml.p7m files\n> ")
    else:
        path = sys.argv[1]

    path = abspath(path)

    if isdir(path) == False:
        raise ValueError
    
    print("Converting .xml.p7m files to .xml")
    p7m_streams = path_to_BytesIO(path, extension=".xml.p7m")
    p7m_conv_streams = group_convert_p7m_to_xml(p7m_streams, verbose=True)

    print("Parsing .xml files")
    xml_streams = path_to_BytesIO(path, extension=(".xml", ".XML"))
    

    for key, stream in p7m_conv_streams.items():
        xml_streams[key] = stream
    
    parser = XML_converter(xml_streams, separator='#@#', concat_symbol='|')
    parser.load(starting_with="FatturaElettronica")
    parser.inflate_tree(filler="-")
    df = parser.get_pandas_dataset(offset=1)

    df, new_labels = modify_header(df)

    if new_labels != {}:
        print("\nWARNING: new labels must be added to the lookup table")
        for key, element in new_labels.items():
            print("\t{} -> {}".format(key, element))
        print('\n')

    print("Exporting .xlsx file")
    excel_file = join(path, "parsed_xml_data.xlsx")
    ew = ExcelWriter(excel_file)
    df.to_excel(ew)
    ew.save()

    print(" --> Data written to .xlsx file: {}\n".format(excel_file))