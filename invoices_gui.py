from io import BytesIO
from pandas import ExcelWriter
from xml_parser.xml_parser import XML_converter
from xml_parser.p7m_converter import group_convert_p7m_to_xml

import streamlit as st

st.write("""
# GES invoices parser

This app is designed to parse multiple italian electronic invoices in `.xml` and `.xml.p7m` formats. The outut 
of the program is a `.xlsx` report in tabular form containing all the head and body fields.

## File upload
Please upload all the invoices files.
""")

files = st.file_uploader("Choose the files to parse", accept_multiple_files=True)

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

            buffer = group_convert_p7m_to_xml(p7m_dict)

            for key, stream in buffer.items():
                xml_dict[key] = stream 
        
        parser = XML_converter(xml_dict, separator='#@#', concat_symbol='|')
        parser.load(starting_with="FatturaElettronica")
        parser.inflate_tree(filler="-")
        df = parser.get_pandas_dataset(offset=1)
    
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


    
    
    
    

    
