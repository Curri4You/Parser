import pandas as pd
import os
import hashlib
#give dataframes of csv files [generator]
def dataframe_generator(root,filenames):
    for file in filenames:
        df= pd.read_csv(root+file,header=None)
        new_columns=[i for i in range(df.shape[-1])]
        df.columns=new_columns
        #print('CURRICULUM OPENS:::::::::::::::::\n',file)
        yield df

def dataframe_emptycol_drop(df):
    return df.dropna()
#divide dataframes into nav, 0,1,2,3 
'''
nav=df.iloc[:a_index]
df0=df.iloc[a_index:h_index]#기초교양
df1=df.iloc[h_index:jg_index] #핵심교양
df2=df.iloc[jg_index:j_index]#전공기초
df3=df.iloc[j_index:g_index]#[교과과정안내]
'''
def get_currid(*args):
    m=hashlib.sha256()
    inp=''
    for info in args:
        inp+=info
    m.update(inp.encode())
    return m.hexdigest()
def dataframe_splitter(df):
    #print('\n\nDf being splitted ::::::::::::::::::::\n\n')

    
    #index column 제외
    df=df.iloc[:,1:].copy()
    
    #뭔가 들어있는 것만 빼기
    ids=[]
    rows=[]
    for id,row in enumerate(df.iloc[:,0]):
        if isinstance(row,str):
            ids.append(id)
            rows.append(row)
    start=rows.index('구분')
    end=rows.index('[교과과정안내]')
    nav_index=ids[start]
    
    
    result={'elec_num':rows[3],'year':rows[1][:4],'info':rows[2],'bef':df.iloc[0:start+3],'nav':df.iloc[nav_index]}
    #print(rows[0][:-9],'AAAAAAHHHHHH')
    
    currid=get_currid(result['year'],result['info']) #NEED WORK
    result['currid']=currid
    name_index=0
    
    for id in range(start+1,end):
        slice_start=ids[id]
        slice_end=ids[id+1]
        
        try:
            tmp=df.iloc[slice_start:slice_end]
        except:
            tmp=df.iloc[slice_start:end]
            
        #string-fy columnnames 
        newcols=map(str,list(tmp.columns))
        tmp.columns=newcols 
        result['df'+str(name_index)]=tmp #df0= dataframe with standards intact
        name_index+=1
    
    return result
   
   
if __name__=='__main__':
    #test dataframe_generator
    root='.\\content\\gdrive\\MyDrive\\competition_data\\curri\\'

    
    f=os.walk(root)
    filenames=[]
    for k in f:
        filenames=k[-1]
    #test dataframe_splitter
    for df in dataframe_generator(root,filenames):
        print(len(dataframe_splitter(df)))
#1부터 20을 준다   