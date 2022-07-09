import pytest
from io import BytesIO
from lxml import objectify
from pandas import DataFrame
from xml_parser.xml_parser import XML_converter


# Test if exceptions are correctly raised by the constructor
def test_constructor_exceptions():
    with pytest.raises(ValueError):

        XML_converter({})
        XML_converter(None)

        dummy = {"test": BytesIO("test".encode('utf-8'))}
        XML_converter(dummy, separator="|", concat_symbol="|")


# Test for separator detection in input stream
def test_separator_validity():
    instream = {"1": BytesIO("A|B".encode('utf-8'))}
    with pytest.raises(ValueError):
        XML_converter(instream, separator="|")


# Test for valid XML tree parsing
def test_traverse_tree_function():

    xml_mockup="<a><b><c>First</c><d>Second</d></b><e>Third</e></a>"
    parser = XML_converter({"myfile.xml": BytesIO(xml_mockup.encode('utf-8'))}, separator="|", concat_symbol="&")

    xml_data = objectify.parse(parser.instream["myfile.xml"])
    tree_root = xml_data.getroot()

    output = parser.traverse_node(tree_root.getchildren())

    assert output == ['b|c|First', 'b|d|Second', 'e|Third']

    

# Test working of load function
def test_load_function():
    
    xml_mockup="<a><b><c>First</c><d>Second</d></b><e>Third</e></a>"
    parser = XML_converter({"myfile.xml": BytesIO(xml_mockup.encode('utf-8'))}, separator="|", concat_symbol="&")
    parser.load()

    assert parser.dataset == {"myfile": ['b|c|First', 'b|d|Second', 'e|Third']}


# Test working of load function with starting condition
def test_load_function_with_condition():
    
    xml_mockup="<a><b><c>First</c><d>Second</d></b><e>Third</e></a>"
    parser = XML_converter({"myfile.xml": BytesIO(xml_mockup.encode('utf-8'))}, separator="|", concat_symbol="&")
    parser.load(starting_with="b")

    assert parser.dataset == {'myfile': ['b|c|First', 'b|d|Second']}


# Test get_branch_limits function
def test_get_branch_limits_function():
    
    xml_mockup="<a><b><c>First</c><d>Second</d></b><e>Third</e></a>"
    parser = XML_converter({"myfile.xml": BytesIO(xml_mockup.encode('utf-8'))}, separator="|", concat_symbol="&")
    parser.load()
    lmin, lmax = parser.get_branch_limits()

    assert lmin == 1
    assert lmax == 2


# Test prune_equivalent_nodes function
def test_prune_equivalent_nodes_function():

    xml_mockup="<a><b><c>First</c><c>Second</c></b><e><f>Third</f></e></a>"
    parser = XML_converter({"myfile.xml": BytesIO(xml_mockup.encode('utf-8'))}, separator="|", concat_symbol="&")
    parser.load()
    
    assert parser.dataset["myfile"] == ['b|c|First&Second', 'e|f|Third']



# Test inflate_tree function
def test_infate_tree_function():
    xml_mockup="<a><b><c>First</c><d>Second</d></b><e>Third</e></a>"
    parser = XML_converter({"myfile.xml": BytesIO(xml_mockup.encode('utf-8'))}, separator="|", concat_symbol="&")
    parser.load()
    parser.inflate_tree()

    assert parser.dataset == {'myfile': ['b|c|First', 'b|d|Second', 'e| |Third']}


# Test inflate_tree function with field filler option
def test_infate_tree_function():
    xml_mockup="<a><b><c>First</c><d>Second</d></b><e>Third</e></a>"
    parser = XML_converter({"myfile.xml": BytesIO(xml_mockup.encode('utf-8'))}, separator="|", concat_symbol="&")
    parser.load()
    parser.inflate_tree(filler="@")

    assert parser.dataset == {'myfile': ['b|c|First', 'b|d|Second', 'e|@|Third']}


# Test get_pandas_dataset function
def test_get_pandas_dataset_function():
    xml_mockup="<a><b><c>First</c><d><k>Second</k></d></b><e>Third</e></a>"
    parser = XML_converter({"myfile.xml": BytesIO(xml_mockup.encode('utf-8'))}, separator="|", concat_symbol="&")
    parser.load()

    result = parser.get_pandas_dataset()

    expected = DataFrame([["First", "Second", "Third"]], index=["myfile"], columns=[["b", "b", "e"], ["c", "d - k", ""]])
    
    assert result.equals(expected)


# Test get_pandas_dataset function after inflate
def test_get_pandas_dataset_function_after_inflate():
    xml_mockup="<a><b><c>First</c><d>Second</d></b><e>Third</e></a>"
    parser = XML_converter({"myfile.xml": BytesIO(xml_mockup.encode('utf-8'))}, separator="|", concat_symbol="&")
    parser.load()
    parser.inflate_tree()

    result = parser.get_pandas_dataset()

    expected = DataFrame([["First", "Second", "Third"]], index=["myfile"], columns=[["b", "b", "e"], ["c", "d", " "]])
    
    assert result.equals(expected)


# Test get_pandas_dataset function after inflate with offset
def test_get_pandas_dataset_function_with_offset():
    xml_mockup="<a><b><c>First</c><d>Second</d></b><e>Third</e></a>"
    parser = XML_converter({"myfile.xml": BytesIO(xml_mockup.encode('utf-8'))}, separator="|", concat_symbol="&")
    parser.load()
    parser.inflate_tree()

    result = parser.get_pandas_dataset(offset=1)

    expected = DataFrame([["First", "Second", "Third"]], index=["myfile"], columns=[["c", "d", " "]])
    
    assert result.equals(expected)
