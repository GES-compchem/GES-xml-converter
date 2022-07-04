from os.path import join, abspath
from pandas import ExcelWriter
from xml_parser.xml_parser import XML_converter
from xml_parser.p7m_converter import group_convert_p7m_to_xml


# Rudimental autocomplete on tab functions
import glob, readline

def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind('tab: complete')
readline.set_completer(complete)



if __name__ == "__main__":

    path = input("Please select the path to the .xml and .xml.p7m files\n> ")

    path = abspath(path)

    print("Converting .xml.p7m files to .xml")
    group_convert_p7m_to_xml(path, join(path), verbose=True)

    print("Parsing .xml files")
    parser = XML_converter(path)
    parser.load(starting_with="FatturaElettronica")
    parser.inflate_tree(filler="-")
    df = parser.get_pandas_dataset(offset=1)

    print("Exporting .xlsx file")
    excel_file = join(path, "parsed_xml_data.xlsx")
    ew = ExcelWriter(excel_file)
    df.to_excel(ew)
    ew.save()

    print(" --> Data written to .xlsx file: {}\n".format(excel_file))