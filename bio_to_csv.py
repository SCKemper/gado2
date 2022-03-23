"""
bio_to_csv
bio2csv
Reformats bio output from Gado2 Named Entity Recognition (NER) to Comma-separated values (csv) format and
include starting character within the input sequence and lenght of tokens as extra columns,
used to convert bio files back to PAGE-XML". This enables adding custom tags to your transcriptions.
"""

__author__ = "Simon C. Kemper."
__copyright__ = "Copyright 2022, NA"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Simon C. Kemper"
__email__ = "simon.kemper@nationaalarchief.nl"
__status__ = "Production"


import re
import sys
from pathlib import Path
import pandas as pd

sentences_doc = []
entities_doc = []
start_positions_doc = []
token_lengths_doc = []
file_names_doc = []
server_errors = []



for file in Path('folder').iterdir(): # add path to folder between brackets 
    line_id_2_all = []
    line_id_3_all = []
    sentence = []
    entities = []
    token_lengths = []
    start_positions = []
    size_errors = []
    file_names = []
    with open(file, 'r') as f:
        regex = r"(?<='folder')(\S+)\.json" # add path to folder between brackets 
        file_str = str(file)
        file_name = re.findall(regex, file_str)
        file_name_str = str(file_name)
        regex = r"\[\'|\'\]"
        file_name_proper = re.sub(regex, "", file_name_str)
        file_name_proper_str = str(file_name_proper)
        file_name_split = file_name_proper_str.split()
        print("\r\nPage: " + file_name_proper_str)
        contents = f.read()
        contents = "".join(contents)
        regexp = re.compile(r'Internal Server Error')  # improve this
        if regexp.search(contents):
            with open('server_errors.txt', 'w') as serr:
                print(file_name_proper_str, file=serr)
        regexp = re.compile(r'too large\!')
        if regexp.search(contents):
            size_errors += file_name_proper_str
            with open('size_errors.txt', 'a') as serz:
                print(file_name_proper_str)
                print(file_name_proper_str, file=serz)
        else:
            regex = r"\},\{"
            regex_2 = r"\}\r\n\{"
            split_lines = re.split(regex, contents)
            for line in split_lines:
                regex = '"confidence"\:0\.\d+,"tag"\:"\S{1,5}","word"\:"(\S+)"'
                line_unicode = re.findall(regex, line)
                regex = r"(\['|'\]|',\s')"
                line_unicode_str = str(line_unicode)
                line_unicode_str = re.sub(regex, ' ', line_unicode_str)
                regex = r"^ "
                line_unicode_str = re.sub(regex, '', line_unicode_str)
                regex = r" $"
                line_unicode_str = re.sub(regex, '', line_unicode_str)
                regex = r" .$"
                line_unicode_str = re.sub(regex, '.', line_unicode_str)
                lenght_unicode = len(str(line_unicode_str))
                lenght_unicode_str = str(lenght_unicode)
                lenght_unicode_split = lenght_unicode_str.split()
                token_lengths += lenght_unicode_split
                sentence += line_unicode
                regex = '"confidence"\:0\.\d+,"tag"\:"(\S{1,5})","word"\:"\S+"'
                tag = re.findall(regex, line)
                entities += tag

            sentence_str = str(sentence)
            """
            The following steps can sometimes distort automatically transcribed phrases if many HTR errors are present
            within them, please remember to adjust the following regex for bad transcriptions to ensure the traced 
            positions match the positions within the transcription. Alternatively, the regex applied to line_unicode_str
            can be adjusted to address pertinent concerns like the apostrophes used for abbreviation, which, if
            separated by a whitespace character, can lead to a single semantically meaningful token being split into two  
            even though it was united in the original transcription.
            """
            regex = r"(\['|'\]|',\s')"
            sentence_str = re.sub(regex,' ', sentence_str)
            regex = r"^ "
            sentence_str = re.sub(regex, '', sentence_str)
            regex = r" $"
            sentence_str = re.sub(regex, '', sentence_str)
            regex = r" .$"
            sentence_str = re.sub(regex, '.', sentence_str)
            regex = r" , "
            sentence_str = re.sub(regex, ', ', sentence_str)
            regex = r" \( "
            sentence_str = re.sub(regex, ' (', sentence_str)
            regex = r" \)"
            sentence_str = re.sub(regex, ')', sentence_str)
            regex = "', \"\'t\", '"
            sentence_str = re.sub(regex, " 't ", sentence_str)
            entities_str = str(entities)
            print(sentence_str)
            # print(sentence)
            # print(entities)
            #len(sentence))
            number_of_rows = len(entities)
            #len(start_positions))
            #en(token_lengths))


            for token in sentence:
                position_string = sentence_str.find(token)
                position_string_str = str(position_string)
                position_string_split = position_string_str.split()
                start_positions += position_string_split

            file_names += file_name_split * number_of_rows
            dictionary = {'Token': sentence, 'Entity' : entities, 'Position' : start_positions, 'Length' : token_lengths, 'File_name' : file_names}
            df = pd.DataFrame(dictionary) # if variables with different row numbers need to be added, chose the following command df = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in dictionary.items()]))
            sentences_doc += sentence
            entities_doc += entities
            start_positions_doc += start_positions
            token_lengths_doc += token_lengths
            file_names_doc += file_names
            dictionary_2 = {'File_name': file_names}
            print(df)
            df.to_csv(file_name_proper_str + ".csv")

dictionary = {'Token': sentences_doc, 'Entity' : entities_doc, 'Position' : start_positions_doc, 'Length' : token_lengths_doc, 'File_name' : file_names_doc}
df_doc = pd.DataFrame(dictionary)
print(df_doc)
df_doc.to_csv("total.csv")
