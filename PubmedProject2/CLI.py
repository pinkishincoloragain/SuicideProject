# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import regex
import os

from pprint import pprint
from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError

from pyfiglet import Figlet


import get_abstracts_pubmed
import pandas as pd


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
        if ('@' not in document.text) or ('.com' not in document.text):
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
        'message': 'Input email.',
        'validate': EmailValidator
    },
    {
        'type': 'confirm',
        'name': 'drug_input_type',
        'message': 'Will you write list of drugs by yourself?'
    },
    {
        'type': 'input',
        'name': 'druglist_path',
        'message': 'Input druglist file path',
        'when': lambda drug_input_type: not drug_input_type['drug_input_type'],
        'validate': FileValidator
    },
    {
        'type': 'input',
        'name': 'drugs',
        'message': 'Input list of drugs',
        'when': lambda drug_input_type: drug_input_type['drug_input_type']
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
                'name': 'ingredient'
            },
            {
                'name': 'ingredient_1'
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
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    },
    {
        'type': 'input',
        'name': 'from_date',
        'message': 'Input from_date',
        'validate': DateValidator
    },
    {
        'type': 'input',
        'name': 'to_date',
        'message': 'Input to_date',
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
print('Order receipt:')

pprint(answers)
pprint(type(answers))

abstracts, drugs, queries = get_abstracts_pubmed.main(email="???",drugs=["aspirin", "acetaminophen"] ,druglist_path="data/Drug_mapping_v2.xlsx", columns=["ingredient", "ingredient_1"],
                                                      max_results=100000, from_date="1990/01/01", to_date="2021/07/07", mesh=True, case_report=True)