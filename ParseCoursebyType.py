from ast import excepthandler
from cgitb import small
from cmath import nan
import pandas as pd
import numpy as np
from utils import *
import re
import json


#give name 

currid_path='currid.csv'
types={'주전공':1,'복수전공':2,'부전공':3,'연계전공':4}

def leave_empty(li):
    new_li=[]
    
    for l in li:
        if len(l)>0:
            new_li.append(l)
    return new_li
class ParseCoursebyType:
    def __init__(self,outpath):
        self.outpath=outpath
    
    #out of run
    
    def bar(self,ser):#input: a series 
        keys=[]
        ignorable_columns=[]
        for index,i in enumerate(ser):
            if isinstance(i,str):
                keys.append(re.sub('[\n\[\]#]','',i))
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
        #print(':::::::::::::::::::::::',bigstandard)
        
        #big standard에 맞춰서 df를 자른다.
        bigdfs=[]
        df_ids=[]
        for i in range(len(big_standard_index)):
            start=big_standard_index[i]
            try:
                end=big_standard_index[i+1]
            except:
                end=len(df)-1
            slice=tmp.iloc[start:end]
            bigdfs.append(slice)
            df_ids.append(str(i+1))#1에서 시작한다. 0이면 skip임
            #print(':::::bigdifs count[',i,']',len(slice))
            #print(slice.iloc[1])
            
        #경우에 따라 파싱       
        if extra_setting!=-1:
            print('extra_setting:::::::::entered',extra_setting)
            new_big_standard=[]
            if extra_setting==0:#g
                for standard in bigstandard:
                    new_standard=[]
                    element_count=0
                    for element in standard:
                        if '이수' in element:
                            element_count+=1
                            #parse
                            bare_minimum=leave_empty(list(set(re.findall('[0-9]*',element))))
                        elif 'Y' in element:
                            continue
                        else:
                            new_standard.append(element.strip(''))
                    if element_count==0:
                        bare_minimum='-1' # it means all of coursed below this standard is required!! 
                    new_standard.append(bare_minimum) #all new standard must have bare_minimum element 
                    new_big_standard.append(new_standard)
                    
            elif extra_setting==1:#h
                #print('::::::::::::::::big standard, 1 activated')
                for standard in bigstandard:
                    
                    new_standard=standard[:-2]#leave out 'Y'
                    
                    new_standard.append('-1')
                    new_big_standard.append(new_standard)
                #print('::::::::::::::::',new_standard)
            elif extra_setting==2 or extra_setting==3:#j, js
                #print('::::::::;big standard, 3 activated')
                for standard in bigstandard:
                    new_standard=[]
                    for element in standard:
                        if '이수' in element:
                            try:
                                tmp=leave_empty(list(set(re.findall('[0-9]*',element))))
                                #print(tmp,':::::::::::::::::::::')
                                new_standard.append(tmp)
                            except:
                                print('this document does not consist two bare minimum credits')
                                new_standard.append('-1')
                            
                        else:
                            new_standard.append(element.strip(' '))
                    new_big_standard.append(new_standard)
                        
            else:
                print('Miss, your extra setting is a little weird:',extra_setting)
            
            #print(new_big_standard)
            return new_big_standard, bigdfs, df_ids

        
        return bigstandard,bigdfs,df_ids
    #여기부터 0번째 열을 제거한다 
    def mid_standard(self,df,bigdf_id,extra_setting=-1):#제거가 안된 dfs를 받게 될 것 
        #mid standard:[] 1번째 열의 값, bar, 소속 small 개수]의 리스트
        #middfs: midstandard에 나눠진 1번째 행부터의 df
        tmp_df=df.iloc[:,1:]
        
        #print('middfs starts')
        #column은 이름을 바꾸지 않는다--> 나중에 '구분'과 매핑하기 위해서 
        #for all df
        midstandards=[]
        middfs=[]
        middf_ids=[]
        
        #midstandard index
        #per df
        
        #midstandard_index
        midstandard_index=[]
        for index,i in enumerate(tmp_df.iloc[:,0]):
            if '-' in i:
                midstandard_index.append(index)
                
        #midstandard가 없는 경우는 넣지 않는다
        
        #get midstandard
        for index in midstandard_index:
            #1차 추출
            mid_standard_orig,_= self.bar(tmp_df.iloc[index])
            orig_len=len(mid_standard_orig)
            
            #정제 
            mid_standard_fixed=[]
            #print('MIDSTANDARD:::::::::::::',mid_standard_orig)
            #공통적인 부분
            mid_standard_fixed.append(re.sub('[ \0\t-]','',mid_standard_orig[0]))
            
            
            if extra_setting!=-1:
                
                '''if extra_setting==0:#g
                    for i in range(1,orig_len):
                            element= mid_standard_orig[i]
                            if '이수' in element:
                                mid_standard_fixed.append(list(set(re.findall('[\0\t0-9]*',element)))[1:])
                            elif 'Y' in element:
                                continue
                            else:
                                mid_standard_fixed.append(element)'''
                if extra_setting==1 or extra_setting==0:#h or g 
                    for i in range(1,orig_len):
                            element= mid_standard_orig[i]
                            if '이수' in element:
                                mid_standard_fixed.append(list(set(re.findall('[\0\t0-9]*',element)))[1:])
                            elif 'Y' in element:
                                continue
                            else:
                                mid_standard_fixed.append(element)
                elif extra_setting==2: #j
                    if '필수' in mid_standard_fixed[0]:#어차피 다 필수니까 파싱 안해줄거임
                        for i in range(1,orig_len):
                            element=mid_standard_orig[i]
                            if '이수' in element:
                                mid_standard_fixed.append('-1')
                            else:
                                mid_standard_fixed.append(element)
                                
                    elif '필' in mid_standard_fixed[0]:
                        for i in range(1,orig_len):
                                element= mid_standard_orig[i]
                                if '이수' in element:
                                    mid_standard_fixed.append(list(set(re.findall('[\0\t0-9]*',element)))[1:])
                                else:
                                    mid_standard_fixed.append(element)
                    else: #선택
                        mid_standard_fixed.append('선택')
                            
                elif extra_setting==3:#js
                    if orig_len==1:
                        mid_standard_fixed.append('선택')
                    else:
                        for i in range(1,orig_len):
                            element= mid_standard_orig[i]
                            if '이수' in element:
                                mid_standard_fixed.append(list(set(re.findall('[0-9]*',element)))[1:])
                            
                    
                else:
                    mid_standard_fixed=mid_standard_orig
            midstandards.append(mid_standard_fixed)
            
        #get middfs
        for i in range(len(midstandard_index)):
            middf_ids.append(bigdf_id+'-'+str(i+1))#1에서 시작한다. 0이면 skip임
            try:
                middf=tmp_df.iloc[midstandard_index[i]+1:midstandard_index[i+1]]
                middfs.append(middf)
            except:
                middf=tmp_df.iloc[midstandard_index[i]+1:]
                middfs.append(middf)
                
        #get midstandard
            
        
        return midstandards,middfs,middf_ids
    
    
    def small_standard(self,df,id): #하나의 DF만 받는다, #가 없으면 안 받는다, middf를 거치지 않은 건 없을 것이다.
        #small standard: [1번째 열의 값, bar]의 리스트
        #smalldfs: smallstandard에 나눠진 1번째 행부터의 df
        
        tmp_df=df.copy()
        
        #get index
        smallstandard_index=[]
        for index,i in enumerate(tmp_df.iloc[:,0]):
            if '#' in i:
                smallstandard_index.append(index)
          
        #get smallstandards
        smallstandards=[]
        for index in smallstandard_index:
            smallstandard=self.bar(tmp_df.iloc[index])[0]
            fixed_standard=[]
            for element in smallstandard:
                if '이수' in element:
                    fixed_standard.append(leave_empty(list(set(re.findall('[0-9]*',element)))))
                elif 'Y' in element:
                    if '필수' in smallstandard[-1]:
                        continue
                    else:
                        fixed_standard.append('필수')
                else:
                    fixed_standard.append(element.strip(' '))
            smallstandards.append(fixed_standard)
        
        
        
        print('::::::::::::::::;smallstandards:::::::::::::::::\n',smallstandards)
        
        #smalldfs
        smalldfs=[]
        small_ids=[]
        for i in range(len(smallstandard_index)):
            start=smallstandard_index[i] 
            try:
                end=smallstandard_index[i+1]
            except:
                end=len(tmp_df)-1
            smalldfs.append(tmp_df.iloc[start+1:end])
            small_ids.append(id+'-'+str(i+1))
       
        
        return smallstandards,smalldfs,small_ids
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
        #bigdf_count, middf_count, smalldf_count *database update required 
        elif depth==-1:
            #print('depth')
            final_ids=[]
            final_dfs=[]
            final_standards=[]
            bigstandard,bigdfs,bigdf_ids=self.big_standard(tmp,extra_setting=mysetting)
            print(bigstandard)
            for bigdf,big_id,bigs in zip(bigdfs,bigdf_ids,bigstandard):
                #print('should-mid-be-activated checker ::::::::::::',bigdf.iloc[0,1])
                if '-' in bigdf.iloc[1,1]: #한 개 bigdf 넣음
                    #print('mid activated')
                    midstandard,middfs,mid_ids=self.mid_standard(bigdf,big_id,extra_setting=mysetting)
                    #print(midstandard)
                    for middf ,mid_id,mids in zip(middfs,mid_ids,midstandard):
                        if len(middf)>1:
                            if '#' in middf.iloc[0,0]:
                                #print('small activated')
                                smallstandard,smalldfs,small_ids=self.small_standard(middf,mid_id)
                                final_ids.append(small_ids)
                                final_dfs.append(smalldfs)
                                final_standards.append(smallstandard)
                            else:
                                #smallstandard가 없고 mid로 끝남
                                final_ids.append(mid_id+'-0')
                                final_dfs.append(middf)
                                final_standards.append(mids)
                else:
                    #midstandardd가 없고 big로 끝남
                    final_ids.append(big_id+'-0-0')
                    final_dfs.append(bigdf)
                    final_standards.append(bigs)
                    
                
                    
            return final_ids,final_dfs,final_standards
            
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
        final_ids,final_dfs,final_standards=parser.run_separate(dfs,choice='h',depth=-1)
        print(final_standards)
        
#1부터 20을 준다   