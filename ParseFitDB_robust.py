
import json
import pandas as pd
import numpy as np
from ParseCourseByType_robust import *
from collections import deque
import os



def get_pilgyo(s,df):
    return 0
def get_jeon(s,df):
    return 0
def find_subject_id(name):
    try:#파일이 열리면
        file=pd.read_csv('subject_id.txt')
        
        #찾으면 
        retrieval=file[file['subject_name']==name]
        
        if len(retrieval)>0:
            return int(retrieval['subject_id'])
        else:
            new_id= int(file['subject_id'].iloc[-1]+1)
            new_row=pd.DataFrame([[name,new_id]],columns=['subject_name','subject_id'])
            file.append(new_row)
            file.to_csv('subject_id.txt',index=False)
            return new_id
    except:
        file=pd.DataFrame([[name,0]],columns=['subject_name','subject_id'])
        file.to_csv('subject_id.txt',index=False)
        return 0
    
    
def all_df(curriculum):
    
    dfkeys=[]
    for k in curriculum.keys():
        if 'df' in k:
            dfkeys.append(k)
            
    dfs=[]
    ss=[]
    for dfkey in dfkeys:
        s,dfd= curriculum[dfkey]
        for k,v in dfd.items():
            dfs.append(v)
        ss.append(s)
    tmp_df=pd.concat(dfs,axis=0)
    
    return ss,tmp_df.copy()

def save_courselist(df,filename,filetype=0):
    #flush it in csv
    #flush it in json
    #just yield 
    if filetype==0:
        df.to_json('data\\course\\'+filename,index=False)
    elif filetype==1:
        df.to_csv('data\\course\\'+filename,index=False)

def renew_open(a):
    if a=='Y':
        return 1
    else:
        return 0
def get_gyo(standards):
    gyo=0
    for s in standards:
        if s['필수여부']=='필수' and '전공' not in s['구분']:
            if isinstance(s['credit'],int):
                gyo+=s['credit']
            else:
                gyo+=int(s['credit'])
    return gyo
        
    
    
class ParseFitDB:
    def __init__(self):
        self.tracker='curriculum_filename.txt'
    def get_curriculum(resultdict):
        
        '''curr_id[PK], the_year, (기준 년도), subject_id[FK], 전공이 무엇인지,
        major_division, (주복부전, 심화 구분), 주/복/부, elec_num, 
        전선 필수 학점, ge_info, 필교 학점
        '''
        #general_info{'college': '엘텍공과대학', 'div': ' 소프트웨어학부', 'subject_name': ' 컴퓨터공학', 'type': 1}
        subject_id=find_subject_id(resultdict['general_info'])#not defined
        major_division=resultdict['general_info']['type']
        elec_num=None#get_jeon(resultdict)#not defined  -->sould be defined with dfs
        ge_info=None#resultdict['elec_num']-elec_num -->should be defined with dfs
        
        newresultdict={'curr_id':resultdict['currid'],'the_year':resultdict['year'],'subject_id':subject_id,'major_division':major_division,'elec_num':elec_num,'ge_info':ge_info}
        
        return newresultdict
    def get_course_prev(nav,tmp_df):#one big df
        #column 명 찾기 
        cols,indices=bar(nav)#그냥 그 행 
        
        
        
        subject_id_index=indices[cols.index('개설학과')]#-2
        credit_index=indices[cols.index('학점')]#-2
        course_name_index=indices[cols.index('교과목명')]#-2
        course_id_index=indices[0]#-2
        is_open_index=indices[-2]#-2
        
        #print(df.columns)
        tmp=tmp_df.iloc[:,[course_id_index,subject_id_index,is_open_index,credit_index,course_name_index]]
        prev_cols=tmp.columns
        new_cols=['course_id','subject_id','is_open','credit','course_name']
        rename_dict={p:n for p,n in zip(prev_cols,new_cols)}
        tmp=tmp.rename(columns=rename_dict)
        
        tmp['is_open']=tmp['is_open'].apply(renew_open)
        #tmp.rename(columns={course_id_index:'course_id',subject_id_index:'subject_id',credit_index:'credit',course_name_index:'course_name'},inplace=True)
        print(tmp)
        tmp['subject_id']=tmp['subject_id'].map(find_subject_id)
        
        course_df=None
        prev_df=None
        return course_df, prev_df
        
    def get_prevlist(tmp_df):
        pass
    def get_major(curriculum):
        pass
    def run(self,all_curriculum):
        #목적: json파일로
        #all_curriculum: list of parser resultdict 
        
        #track filename
        last=-1
        try:
            with open(self.tracker,'r') as f:
                last=deque(f,1)[0]
            with open(self.tracker,'a') as f:
                f.write('\n'+str(int(last)+1))
            
        except:
            with open(self.tracker,'w') as f:
                last='\n1'
                f.write(last)
        
        #get data
        
        courseDB=[]
        curriculumDB=[]
        majorDB=[]
        prevlistDB=[]
        for curriculum in all_curriculum:#(['nav', 'currid', 'year', 'df0', 'df1', 'df2', 'df3', 'df4', 'df5', 'df6', 'general_info'])   
            nav=curriculum['nav']
            
            #몇 번째 교과과정표인가
            last=curriculum['currid']+curriculum['year']
            
            #교과과정표
            #curriculumDB.append(self.get_curriculum(curriculum))#리스트
                  
            #major 
            #majorDB.append(self.get_major(curriculum))#리스트
            
            #course & prevlist
            ss,tmp_df=all_df(curriculum)
            print(len(ss),len(tmp_df))
            courses,prevlist=self.get_course(nav,tmp_df)
    
            #courseDB.append(courses)
            #prevlistDB.append(prevlist)

        
        
            
      
    def prevlistDB(all_curriculum):
        #목적: json파일로
        #all_curriculum: list of parser resultdict 
        
        #track filename
        last=-1
        try:
            f=open('prevlist_filename.txt','r')
            last=deque(f,1)[0]
            f.close()
            f=open('prevlist_filename.txt','a')
            f.write('\n'+str(int(last)+1))
            f.close()
        except:
            f=open('prevlist_filename.txt','w')
            last='\n1'
            f.write(last)
            f.close()
        
        #get data
        for curriculum in all_curriculum:
            #update name
            last=str(int(last)+1)
            
            df=all_df(curriculum)#dict 내 수업 df를 다 합침
            cols,indices=curriculum['nav']#key가 있는 indices
            
            subject_id_index=indices[cols.index('개설학과')]-2
            credit_index=indices[cols.index('학점')]-2
            course_name_index=indices[cols.index('교과목명')]-2
            course_id_index=indices[0]-2
            is_open_index=indices[-1]-2
            
            #print(df.columns)
            tmp=df.iloc[:,[course_id_index,subject_id_index,is_open_index,credit_index,course_name_index]]
            prev_cols=tmp.columns
            new_cols=['course_id','subject_id','is_open','credit','course_name']
            rename_dict={p:n for p,n in zip(prev_cols,new_cols)}
            tmp=tmp.rename(columns=rename_dict)
            #tmp.rename(columns={course_id_index:'course_id',subject_id_index:'subject_id',credit_index:'credit',course_name_index:'course_name'},inplace=True)
            print(tmp)
            tmp['subject_id']=tmp['subject_id'].map(find_subject_id)
            
            
            #turn anme into filename
            #filename=last+'.json'
            filename=last+'.txt'
            save_courselist(tmp,filename,1)
        
        with open('course_json_filename.txt','a') as f:
            f.write(last)
            
        
        

if __name__=='__main__':
    #test dataframe_generator
    root='.\\content\\gdrive\\MyDrive\\competition_data\\curri\\'
    
    f=os.walk(root)
    filenames=[]
    for k in f:
        filenames=k[-1]
    
    curriculums=[]
    #test dataframe_splitter
    for df in dataframe_generator(root,filenames):
	
        #{'nav','gyo','df0'...'df6'}
        result=dataframe_splitter(df)#dfs는 dictionary다. 
        resultnew=run_parser(result)
        curriculums.append(resultnew)#[(s,df)]
    
    p=ParseFitDB()
    p.run(curriculums)   
    '''
    dict_keys(['nav', 'currid', 'year', 'df0', 'df1', 'df2', 'df3', 'df4', 'df5', 'df6', 'general_info'])
    'dfN'=(s,df)
    s=[{'구분':이화진선미,'필수여부':'필수','학사편입생제외여부': 'Y'...}]
    df=[{'1-1-0':df}]
    nav-->꼭 list 씌워줘야하는 series

    ''' 
        
