from io import BytesIO
from lxml import objectify
from typing import List, Tuple, Dict
from pandas import DataFrame, concat


class SeparatorError(Exception):
    '''
    Exception rised when an invalid field separator is detected

        Attributes:
        -----------
        separator(str): Separator value
    '''

    def __init__(self, separator:str, *args: object) -> None:
        super().__init__(*args)
        self.separator = separator
    
    def __str__(self) -> str:
        return """The string '{}' is not a valid field separator""".format(self.separator)



class XML_converter():
    '''
    This class allows for the conversion of multiple .xml files, given asy BytesIO streams, characterized by a generic topology, into
    a pandas DataFrame object.

        Conctructor parameters
        ----------------------
            instream (Dict[str, BytesIO]): Dictionary containing the BytesIO stream of all the .xml files to parse
                ordered by filename
            separator (str): Separator to be used during the parsing operation of the node fields (default: '|')
            concat_symbol (str): Symbol used to concatenate field associated with equivalent branches (default: ' & ')
    '''

    def __init__(self, instream: Dict[str, BytesIO], separator: str = "#@#", concat_symbol: str = "|") -> None:
        
        if type(instream) == dict:
            if instream == {}:
                raise ValueError
        else:
            raise ValueError

        if concat_symbol == separator:
            raise ValueError

        self.dataset = {}
        self.instream = instream
        self.separator = separator
        self.concat_symbol = concat_symbol

        for stream in instream.values():

            if self.separator in stream.read().decode('utf-8'):
                raise SeparatorError(self.separator)

            stream.seek(0)


    def traverse_node(self, nodes: List[objectify.ObjectifiedElement]) -> List[str]:
        '''
        Recursively linearizes the XML file tree into a list of strings containing the nodes tags and final values.
        each node/value field is separated by the 'self.separator' string.

            Parameters:
            -----------
                nodes (list): A list of (lxml.objectify.ObjectifiedElement) node to explore
            
            Returns:
            --------
                strings (list): A list of string containing nodes and values for each XML entry    
        '''

        strings = []

        for node in nodes:

            if node.countchildren() != 0:

                tail_strings = self.traverse_node(node.getchildren())

                for entry in tail_strings:
                    strings.append("{}{}{}".format(node.tag, self.separator, entry))
            
            else:
                strings.append("{}{}{}".format(node.tag, self.separator, node.text))
                
        return strings


    def prune_equivalent_nodes(self, strings: List[str]) -> List[str]:
        '''
        Prune the string decomposition of the .xml tree to remove data attached to identical branches.
        The data of equivalent branches are united in the same entry and divided by a '&' separator.
            
            Parameters:
            -----------
                strings (list[str]): A list of strings containing the branches of the .xml tree
            
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
            branch_a = self.separator.join(string_a.split(self.separator)[0:-1])

            for b, string_b in enumerate(strings[a+1::]):

                branch_b = self.separator.join(string_b.split(self.separator)[0:-1])

                if branch_a == branch_b:
                    if buffer == []:
                        buffer.append(string_a.split(self.separator)[-1])
                    buffer.append(string_b.split(self.separator)[-1])
                    skip.append(a+b+1)
            
            if buffer == []:
                pruned_strings.append(string_a)
            else:
                pruned_strings.append(branch_a + self.separator + self.concat_symbol.join(buffer))
        
        return pruned_strings
    

    def load(self, starting_with: str = None) -> None:
        '''
        Loads the .xml files contained in the instream BytesIO dictionary. Each branch of the .xml tree
        is linearized in data fields and the data related to identical branches are united in a single field. A starting
        condition for the branches can be specified.

            Parameters:
            -----------
                starting_with (str): starting condition to select a subset of the first tag layer (default: None)
        '''
        for filename, stream in self.instream.items():
          
            entry_name = filename.split(".")[0]

            xml_data = objectify.parse(stream)
            tree_root = xml_data.getroot()

            _stringlist_ = self.traverse_node(tree_root.getchildren())
            
            if starting_with == None or starting_with == "":
                stringlist = _stringlist_
            else:
                stringlist = [item for item in _stringlist_ if item.startswith(starting_with)]

            stringlist = self.prune_equivalent_nodes(stringlist)

            self.dataset[entry_name] = stringlist


    def get_branch_limits(self) -> Tuple[int, int]:
        '''
        Evaluate the minimum and maximum branch lengths of the loaded dataset

            Returns:
            --------
                lmin, lmax (Tuple[int, int]): The minimum and maximum branch lengths 
        '''

        lmin, lmax = None, None
        for stringlist in self.dataset.values():
            for string in stringlist:
                nlayers = string.count(self.separator)
                lmin = nlayers if lmin==None else min(lmin, nlayers)
                lmax = nlayers if lmax==None else max(lmax, nlayers)
        
        return lmin, lmax
    

    def inflate_tree(self, filler: str = " ") -> None:
        '''
        Selectively inflate with a 'filler' the .xml tree dataset to obtain branches of equal length.

            Parameters:
            -----------
                filler (str): Element to fill the gap between node fields (default: ' ')
            
            Returns:
            --------
                strings (list[str]): The inflated string decomposition of the .xml file  
        '''

        if self.separator in filler:
            raise ValueError
        
        _, lmax = self.get_branch_limits()

        inflated_dataset = {}
        
        for entry_name, stringlist in self.dataset.items():

            inflated_stringlist = []

            for string in stringlist:

                fields = string.split(self.separator)

                if len(fields) == lmax+1:
                    inflated_stringlist.append(string)
                else:
                    current = self.separator.join(fields[0:-1])
                    current += self.separator
                    current += self.separator.join([filler for _ in range(lmax-len(fields)+1)])
                    current += self.separator + fields[-1]
                    inflated_stringlist.append(current)
            
            inflated_dataset[entry_name] = inflated_stringlist
        
        self.dataset = inflated_dataset 


    def get_pandas_dataset(self, offset: int = 0) -> DataFrame:
        '''
        Convert the loaded dataset into a pandas.DataFrame object. An offset from the .xml tree root can
        be specified in the generation of the header.

            Parameters:
            --------
                offset (int): number of tree layer to remove from the header creation (default: 0)

            Returns:
            --------
                dataframe (pandas.DataFrame): pandas dataframe containing the loaded dataset
        '''

        lmin, lmax = self.get_branch_limits()
        lmin -= offset
    
        dataframe_by_lines = []

        for name in self.dataset:

            data = []
            header = [[] for _ in range(lmin+1)]

            for string in self.dataset[name]:

                sstring = string.split(self.separator)

                for i in range(lmin):
                    header[i].append(sstring[offset + i])

                header[lmin].append(' - '.join(sstring[lmin+offset:-1]))
                data.append(sstring[-1])
            
            if lmin+offset == lmax:
                del header[-1]
        
            df = DataFrame([data], index=[name], columns=header)
            dataframe_by_lines.append(df)
        
        dataframe = concat(dataframe_by_lines)

        return dataframe
