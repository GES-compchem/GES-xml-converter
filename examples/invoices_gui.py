from io import BytesIO
from pandas import ExcelWriter
from ges_xml_converter.xml_parser import XML_converter, SeparatorError
from ges_xml_converter.p7m_converter import group_convert_p7m_to_xml
from ges_xml_converter.invoices_modifier import modify_header, get_default_lookup_table, convert_to_lookup_table

import streamlit as st

st.session_state["p7m_exceptions"] = [[], []]

def p7m_exception_handler(exception, filename):
    st.session_state["p7m_exceptions"][0].append(filename)
    st.session_state["p7m_exceptions"][1].append(exception)

st.write("""
# GES invoices parser

This app is designed to parse multiple italian electronic invoices in `.xml` and `.xml.p7m` formats. The outut 
of the program is a `.xlsx` report in tabular form containing all the head and body fields.
""")

with st.sidebar:
    st.write(""" ## Options """)
    
    st.write("#### Parsing options")
    simplify_flag = st.checkbox("Simplify header with lookup table", value=True)

    offset = 1
    custom_lookup = None
    custom_lookup_flag = True
    if simplify_flag == True:
        custom_lookup_flag = st.checkbox("Use custom lookup-table", value=False)
        if custom_lookup_flag == True:
            buffer = st.file_uploader("Choose a custom lookup-table file", accept_multiple_files=False)
            if buffer != None:
                custom_lookup = convert_to_lookup_table(BytesIO(buffer.getvalue()))

        else:
            data = get_default_lookup_table()
            st.download_button("Download default lookup-table", data=data, file_name='default_lookup_table.txt')
    
    else:
        offset = st.number_input("Select header offset from the XML root", min_value=1, step=1)

    st.write("#### Separators options:")
    concat = st.text_input("Separator used for concatenating equivalent field", value="|")
    filler = st.text_input("Symbol used for filling empty header fields", value="-", disabled=simplify_flag)

    with st.expander("Advanced options"):
        separator = st.text_input("Separator used during XML recursion", value="#@#")

    st.markdown("#")
    st.markdown("#")

if custom_lookup_flag == False or custom_lookup != None:

    st.write('''
        ## File upload
        Please upload all the invoices files.
    ''')

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

                buffer = group_convert_p7m_to_xml(p7m_dict, exception_handler=p7m_exception_handler)

                for key, stream in buffer.items():
                    xml_dict[key] = stream 
            
            try:
                parser = XML_converter(xml_dict, separator=separator, concat_symbol=concat)

            except SeparatorError as e:
                st.error("""ERROR: the recursion separator '`{}`' has been detected in one or more `.xml`
                    files and therefore it cannot be used. \n\nPlease change the separator in the advanced
                    options section""".format(separator))

            else:
                parser.load(starting_with="FatturaElettronica")
                parser.inflate_tree(filler=filler)
                df = parser.get_pandas_dataset(offset=offset)

                if st.session_state["p7m_exceptions"] != [[], []]:
                    msg = "ERROR: exceptions encountered while parsing .xml.p7m files!\n\n"
                    msg += '\tThe following exceptions have been catched:\n'
                    for idx, filename in enumerate(st.session_state["p7m_exceptions"][0]):
                        msg += ('\t  "{}" : "{}"\n'.format(filename, st.session_state["p7m_exceptions"][1][idx]))
                    st.error(msg)

                if simplify_flag == True:
                    
                    if custom_lookup != None:
                        df, new_labels = modify_header(df, filler=filler, lookup_table=custom_lookup)
                    else:
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
