from io import BytesIO
from os import mkdir, getcwd
from os.path import isdir, join, abspath
from datetime import datetime
from shutil import rmtree
from pandas import ExcelWriter
from xml_parser.xml_parser import XML_converter
from xml_parser.p7m_converter import group_convert_p7m_to_xml
from zipfile import ZipFile
import streamlit as st

st.write("""
# GES invoices parser

This app is designed to parse multiple italian electronic invoices in `.xml` and `.xml.p7m` formats. The outut 
of the program is a `.xlsx` report in tabular form containing all the head and body fields.

## File upload
Please upload the folder containing the invoices to be processed in `.zip` format.
""")

zipfile = st.file_uploader("Choose a file please")

if zipfile != None:

    now = datetime.now()
    timestamp = now.strftime("%d%m%Y%H%M%S")

    workdir = abspath(join(getcwd(), "tmp_{}".format(timestamp)))

    if isdir(workdir):
        rmtree(workdir)

    with st.spinner("Processing the uploaded data ..."):

        mkdir(workdir)

        with ZipFile(zipfile, "r") as zip_ref:
            zip_ref.extractall(workdir)
        
        datadir = join(workdir, zipfile.name.strip(".zip"))
        group_convert_p7m_to_xml(datadir, datadir)
        
        parser = XML_converter(datadir)
        parser.load(starting_with="FatturaElettronica")
        parser.inflate_tree(filler="-")
        df = parser.get_pandas_dataset(offset=1)

        rmtree(workdir)

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
