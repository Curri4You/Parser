from ast import excepthandler
from cmath import nan
import pandas as pd
import numpy as np
from utils import *
import re
import json


#give name 

currid_path='currid.csv'
types={'주전공':1,'복수전공':2,'부전공':3,'연계전공':4}
class ParseCoursebyType:
    def __init__(self,outpath):
        self.outpath=outpath
    
    #out of run
    
    def bar(self,ser):#input: a series 
        keys=[]
        ignorable_columns=[]
        for index,i in enumerate(ser):
            if isinstance(i,str):
                keys.append(re.sub('[\n\[\]]',' ',i))
            else:
                ignorable_columns.append(index)
                
        #print('::::::::YOUR BARS FOR YOUR CURRICULUM',keys)   
        return keys,ignorable_columns
    def general_info(self,df):
        gen={}
        #currid
        global currid_path
        try:
            with open(currid_path,'a') as f:
                #교과과정표 식별자를 관리하는 파일을 관리한다
                currid=f.readlines()[-1]
                mycurrid=currid+1
                f.writelines(str(mycurrid)+'\n')
        except:
            with open(currid_path,'w') as f:
                mycurrid=0
                f.writelines(str(0)+'\n')
        
        
        #year
        try:
            year=int(df.iloc[2,0][:4])
        except:
            print(df.iloc[2,0])
            year=int(input('Unable to parse year, input it yourself:'))

        #대학
        global types
        belongto=df.iloc[5,0].split('  ')#2개 스페이스로 구분됨
        
        if len(belongto)==4:#학부와 전공이 있음
            college,div,subject,subject_type=belongto
            div=div.split(':')[-1]
            subject=subject.split(':')[-1]
            subject_type=types[subject_type.split(':')[-1].strip(' ')]
            gen={'college':college,'div':div,'subject_name':subject,'type':subject_type}
            
        elif len(belongto)==3:#전공만 있음
            college,subject,subject_type=belongto
            subject=subject.split(':')[-1]
            subject_type=types[subject_type.split(':')[-1]]
            gen={'college':college,'subject_name':subject,'type':subject_type}
            
        else:
            print('Something is not right with your general information:',belongto)
            return -1
        #general_info: {curri ID, year, 대학, 학부, 전공, 구분,}
        gen['year']=year 
        gen['curr_id']=mycurrid 
        return gen
    def nav(self,df):
        #구분까지
        #nav:  n개의 bar 항목
        #columns: '구분' 행에 있는 것들
        keys,ignorable_columns_candidates=self.bar(df.iloc[9])
        tmp=df.copy()
        ignorable_columns=[]
        for i in ignorable_columns_candidates:
            if tmp[i].dropna().empty:
                ignorable_columns.append(i)
        

        return keys,ignorable_columns
    
    #included in run
    def big_standard(self,df,extra_setting=-1):
        #1붜터 20의 column을 기대해야함
        #big standard 그건 0 column
        #big standard: [0번째 index의 값, bar, 소속 mid 개수 ]의 리스트
        #bigdfs: bigstandard에 의해 나눠진 1번째 행  1번째 열부터의 df list
        
        #big standard가 있는 위치를 찾는다.
        tmp=df.copy()
        big_standard_index=[]
        for i,t in enumerate(tmp[1].values):
            if isinstance(t,str):
                big_standard_index.append(i)
         
        bigstandard=[self.bar(df.iloc[index])[0] for index in big_standard_index] #list of lists
        #확인
        #print(bigstandard)
        
        #big standard에 맞춰서 df를 자른다.
        bigdfs=[]
        for i in range(len(big_standard_index)):
            start=big_standard_index[i]
            try:
                end=big_standard_index[i+1]
            except:
                end=len(df)-1
            slice=tmp.iloc[start:end]
            bigdfs.append(slice)
            #print(':::::bigdifs count[',i,']',len(slice))
            #print(slice.iloc[1])
            
        #경우에 따라 파싱       
        if extra_setting!=-1:
            new_big_standard=[]
            if extra_setting==0:#g
                for standard in bigstandard:
                    new_standard=[]
                    element_count=0
                    for element in standard:
                        if '이수' in element:
                            element_count+=1
                            #parse
                            bare_minimum=list(set(re.findall('[0-9]*',element)))[1:]
                        elif 'Y' in element:
                            continue
                        else:
                            new_standard.append(element)
                    if element_count==0:
                        bare_minimum='-1' # it means all of coursed below this standard is required!! 
                    new_standard.append(bare_minimum) #all new standard must have bare_minimum element 
                    new_big_standard.append(new_standard)
                    
            elif extra_setting==1:#h
                for standard in bigstandard:
                    
                    new_standard=standard[:-2]#leave out 'Y'
                    new_standard.append('-1')
                    
            elif extra_setting==2 or extra_setting==3:#j, js
                for standard in bigstandard:
                    new_standard=[]
                    for element in standard:
                        if '이수' in element:
                            try:
                                tmp=list(set(re.findall('[0-9]*',element)))[1:]
                                #print(tmp,':::::::::::::::::::::')
                                new_standard.append(tmp)
                            except:
                                print('this document does not consist two bare minimum credits')
                                new_standard.append('-1')
                            
                        else:
                            new_standard.append(element)
                    new_big_standard.append(new_standard)
                        
            else:
                print('Miss, your extra setting is a little weird:',extra_setting)
            
            print(new_big_standard)
            return new_big_standard, bigdfs

        
        return bigstandard,bigdfs
    #여기부터 0번째 열을 제거한다 
    def mid_standard(self,dfs):#제거가 안된 dfs를 받게 될 것 
        #mid standard:[] 1번째 열의 값, bar, 소속 small 개수]의 리스트
        #middfs: midstandard에 나눠진 1번째 행부터의 df
        tmp_df=[d.iloc[:,1:] for d in dfs]
        
        #column은 이름을 바꾸지 않는다--> 나중에 '구분'과 매핑하기 위해서 
        #for all df
        midstandards=[]
        middfs_s=[]
        #midstandard index
        for df in tmp_df:
            #per df
            midstandard=[]
            middfs=[]
            
            #midstandard_index
            midstandard_index=[]
            for index,i in enumerate(df.iloc[:,0]):
                if '-' in i:
                    midstandard_index.append(index)
            if len(midstandard_index)==0:
                pass #got to pass this on to small standard!
            print(':::::::::::::midstandard::::::::::::',df.iloc[midstandard_index])
            
            #get middfs
            for i in range(len(midstandard_index)):
                try:
                    middf=df.iloc[midstandard_index[i]:midstandard_index[i+1]]
                    middfs.append(middf)
                except:
                    middf=df.iloc[midstandard_index[i]:]
                    middfs.append(middf)
                    
            #get midstandard
            
        
        return midstandards,middfs_s
    def small_standard(self,dfs):
        #small standard: [1번째 열의 값, bar]의 리스트
        #smalldfs: smallstandard에 나눠진 1번째 행부터의 df
        return smallstandard,smalldfs
    def run_separate(self, dfs,depth=1,choice='g',ifnav=False):
        
        settings={'g':0,'h':1,'j':2,'js':3}
        mysetting=settings[choice]
        
        if ifnav==True:
            return self.nav(dfs['nav'])
        tmp=dfs[choice].copy()
        if depth==3:
            bigstandard,bigdfs=self.big_standard(tmp,extra_setting=mysetting)
            midstandard,middfs=self.mid_standard(bigdfs)
            smallstandard,smalldfs=self.small_standard(middfs)
            return {'depth':depth,'bigstandard':bigstandard,'midstandard':midstandard,'smallstandard':smallstandard,'dfs':smalldfs}
        elif depth==2:
            bigstandard,bigdfs=self.big_standard(tmp,extra_setting=mysetting)
            midstandard,middfs=self.mid_standard(bigdfs)
            return {'depth':depth,'bigstandard':bigstandard,'midstandard':midstandard}
        elif depth==1:
            bigstandard,bigdfs=self.big_standard(tmp,extra_setting=mysetting)
            return {'depth':depth,'bigstandard':bigstandard}
        else:
            print('depth other than 1,2,3 not implemented:::::::::::::::::')
            return -1
      
if __name__=='__main__':
    #test dataframe_generator
    root='.\\content\\gdrive\\MyDrive\\competition_data\\curri\\'

    #test dataframe_splitter
    for df in dataframe_generator(root,filenames):
        #print(len(dataframe_splitter(df)))
        print('\n\nchecking...:::::::::::::::::::::::::::::::\n',df[df.iloc[:,1]=='기초교양'].index.to_list()[0])
        #for i,d in enumerate(dataframe_splitter(df).values()):
            #if i==0:
                #print(d)
            #print(':::::::::::::::::::\n',d[1].value_counts())

        
        #check if d is given right 
        dfs=dataframe_splitter(df)#dfs는 dictionary다. 
        parser=ParseCoursebyType('testoutput')
        
        #test parsing general_info
        #general_info=parser.general_info(dfs['nav'])
        #print(general_info)
        
        #test parsing nav
        #keys,ignorable_columns=parser.nav(dfs['nav'])
        #print(keys,ignorable_columns)
        
        #test big standard
        #parser.big_standard(dfs['g'],extra_setting=0)
        #parser.big_standard(dfs['h'],extra_setting=1)
        #parser.big_standard(dfs['j'],extra_setting=2)
        #parser.big_standard(dfs['js'],extra_setting=3)
        
        #test connection
        r=parser.run_separate(dfs,depth=2)
        print(r)
        
#1부터 20을 준다   