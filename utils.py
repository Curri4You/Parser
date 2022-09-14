import pandas as pd

#give dataframes of csv files [generator]
filenames=['20sabo_xls.csv','20comgong_xls.csv']
def dataframe_generator(root,filenames):
    for file in filenames:
        yield pd.read_csv(root+file,header=None)

#divide dataframes into nav, 0,1,2,3 
'''
nav=df.iloc[:a_index]
df0=df.iloc[a_index:h_index]#기초교양
df1=df.iloc[h_index:jg_index] #핵심교양
df2=df.iloc[jg_index:j_index]#전공기초
df3=df.iloc[j_index:g_index]#[교과과정안내]
'''
def dataframe_splitter(df):
    '''print(':::::::::::::::::df:::::::::::::::::')
    print('length:\t',len(df))
    print('keys:\t',df.keys())'''
    
    #index column 제외
    df=df.iloc[:,1:]
    #colab과 다르게 "숫자" column이 "Unnamed: 숫자"로 변형이 되어 도로 바꿔주기
    new_columns=[i for i in range(df.shape[-1])]
    df.columns=new_columns
    
    #print(df.columns)
    #index 식별
    nav_index=df[df.iloc[:0]=='기초교양'].index.to_list()[0]
    a_index=nav_index
    h_index=df[df.iloc[:,0]=='핵심교양'].index.to_list()[0]
    jg_index=df[df.iloc[:,0]=='전공기초'].index.to_list()[0]
    j_index=df[df.iloc[:,0]=='전공'].index.to_list()[0]
    g_index=df[df.iloc[:,0]=='[교과과정안내]'].index.to_list()[0]
    #df split
    nav=df.iloc[:a_index]
    df0=df.iloc[a_index:h_index]#기초교양
    df1=df.iloc[h_index:jg_index] #핵심교양
    df2=df.iloc[jg_index:j_index]#전공기초
    df3=df.iloc[j_index:g_index]#전공
    return nav,df0,df1,df2,df3

if __name__=='__main__':
    #test dataframe_generator
    root='.\\content\\gdrive\\MyDrive\\competition_data\\curri\\'
    '''for df in dataframe_generator(root,filenames):
        print(df.size)'''
        
    #test dataframe_splitter
    for df in dataframe_generator(root,filenames):
        print(len(dataframe_splitter(df)))