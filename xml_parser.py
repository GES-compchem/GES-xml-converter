from os import listdir
from os.path import isfile, isdir, abspath, join
from copy import deepcopy
from lxml import objectify
from typing import List
from pandas import DataFrame, ExcelWriter, concat



def traverse_node(nodes: List[objectify.ObjectifiedElement], separator: str = "|") -> List[str]:
    '''
    Recursively linearizes the XML file tree into a list of strings containing the nodes tags and final values.
    each node/value field is separated by a given 'separator' string.

        Parameters:
        -----------
            nodes (list): A list of (lxml.objectify.ObjectifiedElement) node to explore
            seseparator (str): Separator dividing the node fields (default: '|')
        
        Returns:
        --------
            strings (list): A list of string containing nodes and values for each XML entry    
    '''

    strings = []

    for node in nodes:

        if node.countchildren() != 0:

            tail_strings = traverse_node(node.getchildren())

            for entry in tail_strings:
                strings.append("{}{}{}".format(node.tag, separator, entry))
        
        else:
            strings.append("{}{}{}".format(node.tag, separator, node.text))
            
    return strings



def prune_equivalent_nodes(strings: List[str], separator: str = "|") -> List[str]:
    '''
    Prune the string decomposition of the .xml tree to remove data attached to identical branches.
    The data of equivalent branches are united in the same entry and divided by a '&' separator.
        
        Parameters:
        -----------
            strings (list[str]): A list of strings containing the branches of the .xml tree
            seseparator (str): Separator dividing the node fields (default: '|')
        
        Returns:
        --------
            strings (list[str]): The pruned string decomposition of the .xml file   
    '''

    skip = []
    pruned_strings = []

    for a, string_a in enumerate(strings):
        
        if a in skip:
            continue
        
        buffer = []
        branch_a = separator.join(string_a.split(separator)[0:-1])

        for b, string_b in enumerate(strings[a+1::]):

            branch_b = separator.join(string_b.split(separator)[0:-1])

            if branch_a == branch_b:
                if buffer == []:
                    buffer.append(string_a.split(separator)[-1])
                buffer.append(string_b.split(separator)[-1])
                skip.append(a+b+1)
        
        if buffer == []:
            pruned_strings.append(string_a)
        else:
            pruned_strings.append(branch_a + separator + " & ".join(buffer))
    
    return pruned_strings



def xml_to_pandas_dataframe(folderpath: str, offset: int = 0, starting_with: str = None) -> DataFrame:
    '''
    Converts the .xml files contained located in the 'path' folder into a pandas dataframe. Each node of the .xml tree
    is linearized in data fields and a common header is generated. All the extra field are joined with a ' - ' separator.
    
        Parameters:
        -----------
            folderpath (str): path to the folder containing the .xml files to parse (with the .xml or .XML extension)
            offset (int): number of tree layer to remove from the header creation (default: 0)
            starting_with (str): starting condition to select a subset of the first tag layer (default: None)
        
        Returns:
        --------
            df_entry (pandas.DataFrame): A dataframe entry for the .xml file
    '''
    
    dataset = {}

    if isdir(folderpath) == False:
        print("""ERROR: directory '{}' not found""".format(folderpath))
        exit()
    
    folderpath = abspath(folderpath)

    files = listdir(folderpath)
    for file in files:

        filepath = join(folderpath, file)
        
        if isfile(filepath) == True and (str(file).endswith(".xml") or str(file).endswith(".XML")):
            
            name = file.split(".")[0]

            xml_data = objectify.parse(filepath)
            tree_root = xml_data.getroot()

            _stringlist_ = traverse_node(tree_root.getchildren())
            stringlist = _stringlist_ if starting_with == "" else [item for item in _stringlist_ if item.startswith(starting_with)]

            stringlist = prune_equivalent_nodes(stringlist)

            dataset[name] = stringlist


    psize = None
    for stringlist in dataset.values():
        for string in stringlist:
            nlayers = string.count("|")
            psize = nlayers if psize==None else min(psize, nlayers)
    psize -= offset
    
    dataframe_by_lines = []

    for name in dataset:

        data = []
        header = [[] for _ in range(psize+1)]
        for string in dataset[name]:
            sstring = string.split('|')
            for i in range(psize):
                header[i].append(sstring[offset + i])
            header[psize].append(' - '.join(sstring[psize+offset:-1]))
            data.append(sstring[-1])
    
        df = DataFrame([data], index=[name], columns=header)
        dataframe_by_lines.append(df)
    
    dataframe = concat(dataframe_by_lines)

    return dataframe
