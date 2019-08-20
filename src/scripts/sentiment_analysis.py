'''
Sentiment analysis script
'''
import pysentiment as ps
import numpy as np
import pandas as pd

results = []
hiv4 = ps.HIV4()

# pip3 install git+https://github.com/hanzhichao2000/pysentiment
# http://www.wjh.harvard.edu/~inquirer/homecat.htm
# https://pypi.org/project/pysentiment/0.1/
#cp -R '/Users/sunlightfellow/Desktop/static' '/usr/local/lib/python3.7/site-packages/pysentiment'
# https://github.com/hanzhichao2000/pysentiment
# Polarity = (Pos-Neg)/(Pos+Neg)
# Subjectivity= (Pos+Neg)/count(*)
def get_tone(df):
    '''
    Gets polarity and subjectivity for a set of websites.

    Inputs:
        - df (pandas dataframe): a pandas dataframe with a "text", "id" and
            "department" columns
    '''

    data = {'id': [],
            'department': [],
            'polarity': [],
            'subjectivity': []}
    df_content = df[['text', 'id', 'department']].values.tolist()
    #print(df_content)

    for row in df_content:
        text, id_obs, department = row
        try:
            #print(text)
            text = ', '.join(text) # join text as string
            tokens = hiv4.tokenize(text)
            score = hiv4.get_score(tokens)
            #print(score)
            data['id'].append(id_obs)
            data['department'].append(department)
            data['polarity'].append(score['Polarity'])
            data['subjectivity'].append(score['Subjectivity'])
        except:
            print('exception', id_obs)
            continue

    return data
