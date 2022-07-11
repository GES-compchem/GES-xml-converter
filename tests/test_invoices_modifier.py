from io import BytesIO
from pandas import DataFrame
from xml_parser.invoices_modifier import modify_header, get_default_lookup_table, convert_to_lookup_table, DEFAULT_LOOKUP_TABLE

# Test modify with DEFAULT_LOOKUP_TABLE
def test_modify_header_default():

    df = DataFrame(["test_field"], index=["test_index"], columns=[["DatiTrasmissione"], ["IdTrasmittente"], ["IdPaese"]])
    result, new_labels = modify_header(df)

    expected = DataFrame(["test_field"], index=["test_index"], columns=["Tras_Paese"])

    assert result.equals(expected)
    assert new_labels == {}


# Test modify with DEFAULT_LOOKUP_TABLE using non default branch
def test_modify_header_default():

    df = DataFrame(["test_field"], index=["test_index"], columns=[["DatiTrasmissione"], ["IdTrasmittente"], ["Unexpected"]])
    result, new_labels = modify_header(df)

    expected = DataFrame(["test_field"], index=["test_index"], columns=["unk_1"])

    assert result.equals(expected)
    assert new_labels == {'DatiTrasmissione|IdTrasmittente|Unexpected': 'unk_1'}


# Test modify with custom lookup table
def test_modify_header_custom():

    my_lookup_table = {"A|B|C": "custom_label"}
    df = DataFrame(["test_field"], index=["test_index"], columns=[["A"], ["B"], ["C"]])

    result, new_labels = modify_header(df, lookup_table=my_lookup_table)

    expected = DataFrame(["test_field"], index=["test_index"], columns=["custom_label"])

    assert result.equals(expected)
    assert new_labels == {}


# Test modify with custom lookup table with filler
def test_modify_header_custom_with_filler():

    my_lookup_table = {"A|B": "custom_label"}
    df = DataFrame(["test_field"], index=["test_index"], columns=[["A"], ["B"], ["#"]])

    result, new_labels = modify_header(df, filler="#", lookup_table=my_lookup_table)

    expected = DataFrame(["test_field"], index=["test_index"], columns=["custom_label"])

    assert result.equals(expected)
    assert new_labels == {}


# Test get_default_lookup_table and convert_to_lookup_table functions by cross-checking
def test_lookup_table_functions_by_crosscheck():
    
    table = get_default_lookup_table()    
    assert type(table) == BytesIO

    result = convert_to_lookup_table(table)
    assert type(result) == dict

    assert result == DEFAULT_LOOKUP_TABLE
