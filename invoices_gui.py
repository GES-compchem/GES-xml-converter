from io import BytesIO
from pandas import ExcelWriter
from xml_parser.xml_parser import XML_converter
from xml_parser.p7m_converter import group_convert_p7m_to_xml
from GES_invoices_utils.header_modifier import modify_header

import streamlit as st

st.session_state["p7m_exceptions"] = [[], []]

def p7m_exception_handler(exception, filename):
    st.session_state["p7m_exceptions"][0].append(filename)
    st.session_state["p7m_exceptions"][1].append(exception)

st.write("""
# GES invoices parser

This app is designed to parse multiple italian electronic invoices in `.xml` and `.xml.p7m` formats. The outut 
of the program is a `.xlsx` report in tabular form containing all the head and body fields.

## File upload
Please upload all the invoices files.
""")


files = st.file_uploader("Choose the files to parse", accept_multiple_files=True)

with st.sidebar:
    st.write(""" ## Advanced options """)
    
    st.write("Parsing options")
    simplify = st.checkbox("Simplify header with lookup table", value=True)

    st.write("Separators options:")
    concat = st.text_input("Separator used for concatenating equivalent field", value="|")
    filler = st.text_input("Symbol used for filling empty header fields", value="-", disabled=simplify)


if files != []:

    xml_dict, p7m_dict = {}, {}

    with st.spinner("Processing the uploaded data ..."):

        for file in files:
            if str(file.name).endswith(".xml"):
                if file.name not in xml_dict:
                    xml_dict[file.name] = BytesIO(file.getvalue())
            elif str(file.name).endswith(".xml.p7m"):
                if file.name not in p7m_dict:
                    p7m_dict[file.name] = BytesIO(file.getvalue())
        
        if p7m_dict != {}:

            buffer = group_convert_p7m_to_xml(p7m_dict, exception_handler=p7m_exception_handler)

            for key, stream in buffer.items():
                xml_dict[key] = stream 
        
        parser = XML_converter(xml_dict, separator='#@#', concat_symbol=concat)
        parser.load(starting_with="FatturaElettronica")
        parser.inflate_tree(filler=filler)
        df = parser.get_pandas_dataset(offset=1)

        if st.session_state["p7m_exceptions"] != [[], []]:
            msg = "ERROR: exceptions encountered while parsing .xml.p7m files!\n\n"
            msg += '\tThe following exceptions have been catched:\n'
            for idx, filename in enumerate(st.session_state["p7m_exceptions"][0]):
                msg += ('\t  "{}" : "{}"\n'.format(filename, st.session_state["p7m_exceptions"][1][idx]))
            st.error(msg)

        if simplify == True:

            df, new_labels = modify_header(df, filler=filler)

            if new_labels != {}:
                msg = "WARNING: New labels must be added to the lookup table\n\n"
                msg += '\tThe following labels have been defined:\n'
                for key, element in new_labels.items():
                    msg += ('\t  "{}" : "{}"\n'.format(key, element))
                st.warning(msg) 

        output = BytesIO()
        writer = ExcelWriter(output)
        df.to_excel(writer)
        writer.save()
        processed_data = output.getvalue()
    
    st.write("""
    ## Report download
    Press the download button to download the report in `.xlsx` format
    """)
    
    st.download_button("Download the report", data=processed_data, file_name='parsed_data.xlsx')


    
    
    
    

    
