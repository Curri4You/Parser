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

#stackoverflow
def flattenlist(nestedList):
 
    # check if list is empty
    if not(bool(nestedList)):
        return nestedList
 
     # to check instance of list is empty or not
    if isinstance(nestedList[0], list):
 
        # call function with sublist as argument
        return flattenlist(*nestedList[:1]) + flattenlist(nestedList[1:])
 
    # call function with sublist as argument
    return nestedList[:1] + flattenlist(nestedList[1:])
def flattendict(dictnestedlist):#1d dict만 다룸
    newdict={}
    if isinstance(dictnestedlist,list):
        for d in dictnestedlist:
            if isinstance(d,dict):
                for k,v in d.items():
                    newdict[k]=v
    return newdict
def has_mid(a):
    if isinstance(a,str):
        if '-' in a:
            return True
    return False
def has_small(a):
    if isinstance(a,str):
        if '#' in a:
            return True
    return False

def depth(example,col):
    if len(example[example.iloc[:,col].apply(has_mid)])>0:
        if len(example[example.iloc[:,col].apply(has_small)])>0:
            return 3
        else:
            return 2
    elif len(example[example.iloc[:,1].apply(has_small)])>0:
        return 1
    else:
        return 0 

def find_index(df,col,sign):
    tmps=df.copy()
    _index=[]
    for i,t in enumerate(tmps.iloc[:,col]):
        if isinstance(t,str):
            if sign in t:
                _index.append(i)
                
    return _index
class ParseCoursebyType:
    def __init__(self,outpath,resultdict):
        self.outpath=outpath
        self.d=resultdict
        self.df_by_ids={}
        self.nav_for_standards=['flag']
    
    #out of run
    def pretty_standard_bynav(self,standard,swhere):
        nav=list(self.d['nav'])
        finalstandard={}
        for val,key in zip(standard,swhere):
            tmp=val
            tmp=tmp.strip(' ')
            tmp=re.sub('\n','',tmp)
            
            if '학수번호' in nav[key]:
                finalstandard['구분2']=tmp
            elif '교과목명' in nav[key]:
                #print(tmp)
                nums=re.findall('[0-9]+',tmp)
                if '전공' in tmp:
                    tmp_splitted=tmp.split('/')
                    finalstandard['심화']=nums[0]
                    finalstandard['복수']=nums[1]

                elif len(nums)>=2:
                    words=tmp.split(' ')
                    finalstandard[words[0][-2:0]]=nums[0]
                    finalstandard['credit']=nums[1]
                elif len(nums)==1:
                    finalstandard['credit']=nums[0]
                
            else:
            	finalstandard[re.sub('[\n]','',nav[key])]=tmp
        return finalstandard
    def bar(self,ser):#input: a series 
        keys=[]
        key_indices=[]
        
        for index,i in enumerate(ser):
            if isinstance(i,str):
                keys.append(re.sub('[\n\[\]#]','',i))
                key_indices.append(index)
                
        #print('::::::::YOUR BARS FOR YOUR CURRICULUM',keys)   
        return keys,key_indices
    def general_info(self):#done!
        df=self.d['bef']
        gen={}
        
        
        # result={'currid':rows[0],'year':rows[1][:4],'info':rows[2],'bef':df.iloc[0:start],'nav':df.iloc[nav_index],'gyo':df.iloc[gyo_index:-1]}
    
        #currid
        currid=self.d['currid']
        
        #year
        year=self.d['year']
        
        #대학
        global types
        
        try:
            belongto=self.d['info'].split('  ')#2개 스페이스로 구분됨 #5,1
        except:
            print(self.d['info'])
            belongto=input('Unable to parse 소속, copy and paste:').split('  ')
        
        if len(belongto)>=4:#학부와 전공이 있음
            college,div,subject,subject_type=belongto
            div=div.split(':')[-1]
            subject=subject.split(':')[-1]
            subject_type=types[subject_type.split(':')[-1].strip(' ')]
            gen={'college':college,'div':div,'subject_name':subject,'type':subject_type}
            
        elif len(belongto)==3:#전공만 있음
            college,subject,subject_type=belongto
            subject=subject.split(':')[-1]
            subject_type=types[subject_type.split(':')[-1].strip(' ')]
            gen={'college':college,'subject_name':subject,'type':subject_type}
            
        else:
            print('Something is not right with your general information:',belongto)
            return -1
        #general_info: {curri ID, year, 대학, 학부, 전공, 구분,}
        gen['year']=year 
        gen['curr_id']=currid 
        return gen
    def nav(self): #done!
        #구분제외
        #nav:  n개의 bar 항목
        #columns: '구분' 행에 있는 것들
        keys,key_indices=self.bar(self.d['nav'])
        
        return keys[1:],key_indices[1:]
    
    
    #included in run
    def mid_only(self,id,df):
        tmps=df.copy()
        
        mid_standard_index=find_index(tmps,1,'-')
        #print('mid:::::::',mid_standard_index)
        
        
        #slice
        dfs=[]
        standards=[]
        for i in range(len(mid_standard_index)):
            #get standard
            mid_standard,swhere=self.bar(tmps.iloc[mid_standard_index[i]]) #list 

            
            #pretty a standard
            mid_standard=self.pretty_standard_bynav(mid_standard,swhere)#becomes dictionary
            standards.append(mid_standard)            
            
            #slice
            start=mid_standard_index[i]
            try:
                end=mid_standard_index[i+1]
            except:
                end=len(tmps)-1
            dfs.append(tmps.iloc[start+1:end])
        
        ret_dict={}
        #make a dictionary
        for i,d in enumerate(dfs):
            newid=id+'-'+str(i)+'-0'
            ret_dict[newid]=d
        return standards, ret_dict
    
    def mid_small(self,id,df):
        tmps=df.copy()
        
        mid_standard_index=find_index(tmps,1,'-')
        #print('mid small:::::::',mid_standard_index)
        
        
        #slice
        dfs=[]
        for i in range(len(mid_standard_index)):
            start=mid_standard_index[i]
            try:
                end=mid_standard_index[i+1]
            except:
                end=len(tmps)-1
            dfs.append(tmps.iloc[start+1:end])
        
        #slice further
        rets=[]
        standards=[]
        for i,d in enumerate(dfs):
            mid_standard,mswhere=self.bar(tmps.iloc[mid_standard_index[i]])
            mid_standard=self.pretty_standard_bynav(mid_standard,mswhere)#becomes dictionary
            standards.append(mid_standard)
            if depth(d,col=1)==1:
                small_standard,ret_small=self.small_only(id,d,mid=i)
                rets.append(ret_small)          
                standards.append(small_standard)  
            else:
                newid=id+'-'+str(i)+'-0'
                rets.append({newid:d})
                
        
        return flattenlist(standards), flattendict(rets)
                
    def small_only(self,id,df,mid=0):
        tmps=df.copy()
        
        small_standard_index=find_index(tmps,1,'#')
        
        
        dfs=[]
        standards=[]
        for i in range(len(small_standard_index)):
            #get standard
            small_standard,swhere=self.bar(tmps.iloc[small_standard_index[i]]) #list 
            
            #pretty standard
            small_standard=self.pretty_standard_bynav(small_standard,swhere)#becomes dictionary
            standards.append(small_standard)
            #slice
            start=small_standard_index[i]
            try:
                end=small_standard_index[i+1]
            except:
                end=len(tmps)-1
            dfs.append(tmps.iloc[start+1:end])
        
        ret_dict={}
        #make a dictionary
        for i,d in enumerate(dfs):
            newid=id+'-'+str(mid)+'-'+str(i)
            ret_dict[newid]=d
        return standards, ret_dict
    def run(self,df,id='0'):#한 big standard 블록을 받을 것 
        #1붜터 20의 column을 기대해야함
        #big standard 그건 0 column
        #big standard: [0번째 index의 값, bar, 소속 mid 개수 ]의 리스트
        #bigdfs: bigstandard에 의해 나눠진 1번째 행  1번째 열부터의 df list
        
        #big standard가 있는 위치를 찾는다.
        tmp=df.copy()

        bigstandard,swhere=self.bar(df.iloc[0]) #list 
        #확인
        #print(':::::::::::::::::::::::',bigstandard)
        
        #big standard에 맞춰서 df를 자른다.
        
        deep=depth(df,1)
        
        #경우에 따라 파싱    
        #잘라주기
        tmp=tmp.iloc[1:]
        standards=[self.pretty_standard_bynav(bigstandard,swhere)]
        if deep==0:
            ret_df={id+'-0-0':tmp}
        elif deep==1: #small df들이 있음 
            s,ret_df=self.small_only(id,tmp)
            standards.append(s)
        elif deep==2: #midd만
            s,ret_df=self.mid_only(id,tmp)
            standards.append(s)
        elif deep==3:
            s,ret_df=self.mid_small(id,tmp) 
            standards.append(s)
        else:
            print('Miss, your extra setting is a little weird:',deep)
		
        #print(new_big_standard)
        return  standards,ret_df

      
      
if __name__=='__main__':
    #test dataframe_generator
    root='.\\content\\gdrive\\MyDrive\\competition_data\\curri\\'
    
    f=os.walk(root)
    filenames=[]
    for k in f:
        filenames=k[-1]
    

    #test dataframe_splitter
    for df in dataframe_generator(root,filenames):
	
        #{'nav','gyo','df0'...'df6'}
        result=dataframe_splitter(df)#dfs는 dictionary다. 
        parser=ParseCoursebyType('testoutput',result)
        
        i=1
        for key in result.keys():
            if 'df' in key:
                s,k=parser.run(result[key],id=str(i))
                #print(k.keys())
                print(s)
                i+=1
        
   
            
            