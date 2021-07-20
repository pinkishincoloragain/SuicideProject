# -*- coding: utf-8 -*-
# 실행 전 pip install -r requirements.txt

from __future__ import print_function, unicode_literals
import regex
import re
import os
from datetime import date

from pprint import pprint
from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError

from pyfiglet import Figlet

import get_abstracts_pubmed
import pandas as pd

email_form = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

style = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#673AB7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#2196f3 bold',
    Token.Question: '',
})


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # Move cursor to end


class EmailValidator(Validator):
    def validate(self, document):
        if email_form.match(document.text) is None:
            raise ValidationError(
                message='Please enter a email form',
                cursor_position=len(document.text))  # Move cursor to end


class FileValidator(Validator):
    def validate(self, document):
        if os.path.exists(document.text):
            name, extension = os.path.splitext(document.text)
            exts = [".csv", ".xlsx"]
            if extension not in exts:
                raise ValidationError(
                    message='The file is not format in ' + exts.__str__(),
                    cursor_position=len(document.text))  # Move cursor to end
        elif document.text == "":
            raise ValidationError(
                message='Please input file path ',
                cursor_position=len(document.text))  # Move cursor to end
        else:
            raise ValidationError(
                message='Pathname seems to be incorrect.',
                cursor_position=len(document.text))


class DateValidator(Validator):
    def validate(self, document):
        ok = regex.match(
            r"[\d]{4}/[\d]{2}/[\d]{2}",
            document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid date format(yyyy/mm/dd)',
                cursor_position=len(document.text))  # Move cursor to end


f = Figlet(font='slant')
print(f.renderText('* * * * * * * * *'))
print(f.renderText('DSA'))
print(f.renderText('* * * * * * * * *'))
print("To stop in the process, press ctrl + c")
print()

questions = [
    {
        'type': 'input',
        'name': 'Email',
        'default': "smb1103@gmail.com",
        'message': 'Input email.',
        'validate': EmailValidator
    },
    {
        'type': 'confirm',
        'name': 'drug_input_type',
        'message': 'Do you have file including list of drugs?'
    },
    {
        'type': 'input',
        'name': 'druglist_path',
        'message': 'Input druglist file path',
        'default': "Drug_mapping_v2.xlsx",
        'when': lambda drug_input_type: drug_input_type['drug_input_type'],
        'validate': FileValidator
    },
    {
        'type': 'input',
        'name': 'drugs',
        'default': "Aspirin, Bupropion",
        'message': 'Input list of drugs',
        'when': lambda drug_input_type: not drug_input_type['drug_input_type']
    },
    {
        'type': 'checkbox',
        'name': 'columns',
        'message': 'Input columns',
        'choices':
            [
                {
                    'name': 'concept_id'
                },
                {
                    'name': 'brand_name'
                },
                {
                    'name': 'ingredient_num'
                },
                {
                    'name': 'ingredient',
                    'checked': True
                },
                {
                    'name': 'ingredient_1',
                    'checked': True
                },
                {
                    'name': 'atc code'
                },
                {
                    'name': 'atc_level'
                }
            ],
        'when': lambda drug_input_type: drug_input_type['drug_input_type']
    },
    {
        'type': 'input',
        'name': 'max_results',
        'message': 'Input max_results',
        'default': "100",
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    },
    {
        'type': 'input',
        'name': 'from_date',
        'message': 'Input from_date',
        'default': "1990/01/01",
        'validate': DateValidator
    },
    {
        'type': 'input',
        'name': 'to_date',
        'message': 'Input to_date',
        'default': date.today().strftime("%Y/%m/%d"),
        'validate': DateValidator
    },
    {
        'type': 'confirm',
        'name': 'mesh',
        'message': 'Search using meSH : y, \n',
        'default': True
    },
    {
        'type': 'confirm',
        'name': 'case_report',
        'message': 'Search using case report : y, \n',
        'default': True
    }
]

answers = prompt(questions, style=style)

if not answers['drug_input_type']:
    answers['drugs'] = answers['drugs'].split(", ")

print('Order receipt:')
pprint(answers)
pprint(type(answers))

#
abstracts, drugs, queries = get_abstracts_pubmed.main(**answers)

output_file = "PubMed_crawl_sui_casereports_210707)_1.xlsx"
df = pd.DataFrame(abstracts)

if not df.empty:

    df['drugs'] = df['drugs'].map(lambda x: ',\n'.join(x))
    df['PMID'] = df['PMIDa'].map(lambda x: ',\n'.join(x))

    df.drop(["PMIDa", "PMIDlist"], axis=1, inplace=True)
    writer = pd.ExcelWriter(output_file, engine='openpyxl')
    print(f"Length: {len(df)}")
    df.to_excel(writer, sheet_name="result", index=False)

    dfdrugs = pd.DataFrame({'Drugs': drugs})
    dfdrugs.to_excel(writer, sheet_name="drugs", index=False)

    dfq = pd.DataFrame({'Queries': queries})
    dfq.to_excel(writer, sheet_name="queries", index=False)

    writer.save()

else:
    print("Empty")
