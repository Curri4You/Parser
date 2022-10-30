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
        if '-' in a :
            return True
    return False
def has_small(a):
    if isinstance(a,str):
        if '#' in a:
            return True
    return False

def depth(example,col):
    lookout=example.iloc[:,col]
    if len(example[example.iloc[:,col].apply(has_mid)])>0:
        if len(example[example.iloc[:,col].apply(has_small)])>0:
            return 3
        else:
            return 2
    elif len(example[example.iloc[:,1].apply(has_small)])>0:
        return 1
    else:
        return 0 


def depth_w_map(example,col):
    lookout=example.iloc[:,col]
    mid=any(map(has_mid,list(lookout)))
    small=any(map(has_small,list(lookout)))
    
    if mid and small:
        return 3
    elif mid:
        return 2
    elif small:
        return 1
    else:
        return 0
#필요 없는 열은 제외하고, 필요한 열이 가지는 column이름만 반환한다
#이 때 column 이름은 각 df (같은 커리큘럼에서는 같을 것이다.)를 참고한다. 
def bar(ser,cols):#input: a series 
	keys=[]
	key_indices=[]
	
	for col,i in zip(cols,ser):
		if isinstance(i,str):
			keys.append(re.sub('[\n\[\]#]','',i))
			key_indices.append(col)
			
	#print('::::::::YOUR BARS FOR YOUR CURRICULUM',keys)   
	return keys,key_indices
def find_index(df,col,signs):
    tmps=df.copy()
    _index=[]
    if len(signs)>1:
        _signs=signs.split(' ')
    else:
        _signs=[signs]
        
    for i,t in enumerate(tmps.iloc[:,col]):
        if isinstance(t,str):
            for sign in _signs:
                if sign in t:
                    _index.append(i)
                
    return _index
class ParseCoursebyType:
    def __init__(self,outpath,resultdict):
        self.outpath=outpath
        self.resultdict=resultdict
        self.df_by_ids={}
        self.nav_for_standards=['flag']
        self.cols=resultdict['df0'].columns
    
    #pretty_standard by nav가 하는 일
    '''
    구분자:내용으로 바꾸어준다. 딕셔너리를 반환한다. 
    standard: 리스트로 이루어진 인풋
    swhere와 nav_swhere는 같은 바탕에서 만들어진다고 가정한다
    
    swhere는 standard를 만들 때 학수번호부터 열이 시작한다. 단 big_standard제외 
    nav_swhere는 구분부터 시작한다. 
    
    '''
    def pretty_standard_bynav(self,raw_standard,type='not big'):#각 df의 standard
        #standard 속 원소마다 이름 지어주기
        
        #커리큘럼의 df의 column
        cols=self.cols #string-fied 1~20
        if type=='not big':
            standard,swhere=bar(raw_standard,cols)
            nav,nav_swhere=bar(self.resultdict['nav'][1:],cols)
        else:
            standard,swhere=bar(raw_standard,cols)
            nav,nav_swhere=bar(self.resultdict['nav'],cols)
        
     

        finalstandard={}
        for s,key in zip(standard,swhere):
            
            if key in nav_swhere:
                tmp_swhere=nav_swhere.index(key) #nav 위치
                tmp_val=nav[tmp_swhere] #nav 속 이름
                
                if '학수번호' in tmp_val:
                    #대게 mid와 small에 대해 구분자를 언급하는 부분임
                    finalstandard['구분2']=s
                elif '교과목명' in tmp_val:
                    #대게 필수 이수 영역 및 과목 개수, 그리고 학점을 언급함 
                    #심화-복수가 있는 경우가 있음
                    
                    
                    #심화와 복수 구분이 있는 경우
                    nums=re.findall('[0-9]+',s)
                    if '/' in tmp_val:
                        nums=s.split('/')
                        finalstandard['diff_by_div']=True #심화전공 여부
                        finalstandard['1_credit']=nums[0] #심화전공 졸업요건
                        finalstandard['2_credit']=nums[1]#기타전공 졸업요건
                        finalstandard['credittype']='per_div' #졸엽요건 타입
                    else: #없는 경우
                        finalstandard['diff_by_div']=False
                    
                        if len(nums)>=2: #영역과 학점이 분리되어있는 경우 
                            words=tmp_val.split(' ')
                            the_word=words[0][-2:0]
                            finalstandard['credit']=nums[1]
                            if '과목' in tmp_val:
                                finalstandard['credittype']='course'
                                finalstandard['course']=nums[0]
                            elif '영역' in tmp_val:
                                finalstandard['credittype']='section'
                                finalstandard['section']=nums[0]
                            else:
                                finalstandard['credittype']='sector'
                                finalstandard['sector']=nums[0]
                        else:
                            #print(s)
                            finalstandard['credit']=nums[0]
                            finalstandard['credittype']='whole'
                    
                else:
                    finalstandard[re.sub('[\n]','',tmp_val)]=s
            else:
                print('What nav name for ',s,'?')
                print('nav:',nav_swhere,'and nav',nav,'and swhere',key)
                nav_name=input('name:\t')
                finalstandard[nav_name]=s

        return finalstandard #swhere

    def general_info(self):#done!
        
        
        gen={}
        
        
        #대학
        global types
        
        try:
            belongto=self.resultdict['info'].split('  ')#2개 스페이스로 구분됨 #5,1
        except:
            print(self.resultdict['info'])
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
        #general_info: { 대학, 학부, 전공, 구분,}

        return gen
    
    #included in run
    def mid_only(self,id,df):
        tmps=df.copy()
        
        mid_standard_index=find_index(tmps,0,'-')
        
        
        #slice
        dfs=[]
        standards=[]
        for i in range(len(mid_standard_index)):
            #get standard
            #pretty a standard
            mid_standard=self.pretty_standard_bynav(list(tmps.iloc[mid_standard_index[i]]))#becomes dictionary
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
            newid=id+'-'+str(i+1)+'-0'
            ret_dict[newid]=d
        #print('in mid',len(standards)==len(ret_dict))
        return standards, ret_dict
    
    def mid_small(self,id,df):
        tmps=df.copy()
        #잘 도착하고 있는 것 확인함
        # print('MID AND SMALL\n',tmps)
        
        mid_standard_index=find_index(tmps,0,'-')
        
        
        #slice small
        dfs=[]
        for i in range(len(mid_standard_index)):
            start=mid_standard_index[i]+1
            try:
                end=mid_standard_index[i+1]
            except:
                end=len(tmps)-1
            dfs.append(tmps.iloc[start+1:end])
        
        #slice further
        rets=[]
        standards=[]
        for i,d in enumerate(dfs):
            
            #d가 소속되는 df의 mid_standard
            #d는 midstandard는 거세되어있음
            mid_raw=tmps.iloc[mid_standard_index[i]]
            mid_standard=self.pretty_standard_bynav(list(mid_raw))#becomes dictionary
            standards.append(mid_standard)
            

            #d 안에 small standard가 있다면
            if depth_w_map(d,0)==1:
                #print('found small',d)
                small_standard,ret_small=self.small_only(id,d,mid=i+1)#big
                #print('small in mid',len(small_standard)==len(ret_small))
                rets.append(ret_small)          
                standards.append(small_standard)  
            #없다면 
            else:
                #print('mid small without small:,\n',d)
            
                newid=id+'-'+str(i+1)+'-0'
                rets.append({newid:d})
                
        #print('in mid small',len(flattenlist(standards))==len(flattendict(rets)))
        return flattenlist(standards), flattendict(rets)
                
    def small_only(self,id,df,mid=0):
        tmps=df.copy()
        small_standard_index=find_index(tmps,0,'# [')
        
        dfs=[]
        standards=[]
        for i in range(len(small_standard_index)):
            #get standard
            #pretty standard
            small_standard=self.pretty_standard_bynav(list(tmps.iloc[small_standard_index[i]]))#becomes dictionary
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
            newid=id+'-'+str(mid)+'-'+str(i+1)
            ret_dict[newid]=d
        #print('in small',len(standards),len(ret_dict))
        return standards, ret_dict
    def run(self,df,id='1'):#한 big standard 블록을 받을 것 
        #1붜터 20의 column을 기대해야함
        #big standard 그건 0 column
        #big standard: [0번째 index의 값, bar, 소속 mid 개수 ]의 리스트
        #bigdfs: bigstandard에 의해 나눠진 1번째 행  1번째 열부터의 df list
        
        #big standard가 있는 위치를 찾는다.
        tmp=df.copy()

        bigstandard=self.pretty_standard_bynav(list(df.iloc[0]),type='big') #list 

        
        #big standard에 맞춰서 df를 자른다.
        
        #경우에 따라 파싱    
        #'구분'잘라주기
        #bigstandard 행 잘라주기
        tmp=tmp.iloc[1:,1:]
        
        #판단하기
        deep=depth(tmp,0)
        #print('::::::::::::::::depth;::::::::::::;;',deep)
        standards=[bigstandard]
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
		
        #print(ret_df.keys())
        return  flattenlist(standards),ret_df

def run_parser(resultdict):
    parser=ParseCoursebyType('testoutput',resultdict)
    i=1
    newresultdict={'bef':resultdict['bef'],'nav':resultdict['nav'],'currid':resultdict['currid'],'year':resultdict['year']}

    for key in resultdict.keys():
        if 'df' in key:
            standard_intact_df=resultdict[key]
            s,k=parser.run(standard_intact_df,id=str(i))
            #TEST
            #print('SK::::',len(s),k.keys())
            newresultdict[key]=(s,k)
    newresultdict['general_info']=parser.general_info()
    return newresultdict
        
   
            
            
      
      
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
        
        #{'bef','nav','currid','year','df0'...'df6','general_info'}
        resultnew=run_parser(result)
        #print(resultnew.keys())
        
        #1~20
        #print(resultnew['bef'].keys())
        #currid, subject_name, college_name, elec_num,gyo_num 재료가 여기 있음
        #print(resultnew['bef'])
        
        #1~20
        #print(resultnew['nav'].keys())
        #series
        #nav 내용이 들어가있음
        #print((resultnew['nav'].values))
        
        #dict_keys(['college', 'subject_name', 'type'])
        #dict_keys(['college', 'div', 'subject_name', 'type'])
        #print(resultnew['general_info'].keys())
        
        

            
            