'''
ex 1) depth 3

bigstandard, midstandard,smallstandard,smalldfs

ex 2) depth 2

bigstandard, midstandard,middfs

ex 3) depth 1

bigstandard,bigdfs

''' 
import json
import pandas as pd
import numpy as np

def course(dfs):#어느 standard이든 dfs 받음
    
    pass


if __name__=='__main__':
    sample_path='content/gdrive/MyDrive/competition_data/curri/h_json.json'
    #h_json=json.load(sample_path)
    h_df=pd.read_json(sample_path)
    df=pd.read_json(h_df['-융복합교양']['docs']['#융복합교양(문학과언어)'])
    print(df)
    