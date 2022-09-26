import pandas as pd

#give dataframes of csv files [generator]
filenames=['20sabo_xls.csv','20comgong_xls.csv']
def dataframe_generator(root,filenames):
    for file in filenames:
        df= pd.read_csv(root+file,header=None)
        new_columns=[i for i in range(df.shape[-1])]
        df.columns=new_columns
        print('CURRICULUM OPENS:::::::::::::::::\n',df.columns)
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
def dataframe_splitter(df):
    print('\n\nDf being splitted ::::::::::::::::::::')

    
    #index column 제외
    df=df.iloc[:,1:].copy()
    
    #print(df.columns)
    #index 식별
    nav_index=df[df.iloc[:,0]=='기초교양'].index.to_list()[0]
    a_index=nav_index
    h_index=df[df.iloc[:,0]=='핵심교양'].index.to_list()[0]
    jg_index=df[df.iloc[:,0]=='전공기초'].index.to_list()[0]
    j_index=df[df.iloc[:,0]=='전공'].index.to_list()[0]
    g_index=df[df.iloc[:,0]=='[교과과정안내]'].index.to_list()[0]
    print(a_index,'\t',h_index,'\t',jg_index,'\t',j_index,'\t',g_index)
    #df split
    nav=df.iloc[:a_index]
    df0=df.iloc[a_index:h_index]#기초교양
    df1=df.iloc[h_index:jg_index] #핵심교양
    df2=df.iloc[jg_index:j_index]#전공기초
    df3=df.iloc[j_index:g_index]#전공
    df4=df.iloc[g_index:]#교과과정
    return {'nav':nav,'g':df0,'h':df1,'j':df2,'js':df3,'gyo':df4}

if __name__=='__main__':
    #test dataframe_generator
    root='.\\content\\gdrive\\MyDrive\\competition_data\\curri\\'
    '''for df in dataframe_generator(root,filenames):
        print(df.size)'''
        
    #test dataframe_splitter
    for df in dataframe_generator(root,filenames):
        #print(len(dataframe_splitter(df)))
        print('\n\nchecking...:::::::::::::::::::::::::::::::\n',df[df.iloc[:,1]=='기초교양'].index.to_list()[0])
        for i,d in enumerate(dataframe_splitter(df).values()):
            if i==0:
                print(d)
            #print(':::::::::::::::::::\n',d[1].value_counts())
#1부터 20을 준다   