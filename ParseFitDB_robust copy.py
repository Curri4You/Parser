import pandas as pd
import numpy as np
from ParseCourseByType_robust import *
from collections import deque
import os
from utils import *

def decrement(a):
    return a-1
def is_open_filtered(a):
    if isinstance(a,str):
        if a=='Y':
            return 1
    return 0 
def syllabus_id_filtered(a):
    return 0

def prev_list_filtered(a):
    if isinstance(a,str):
        #여러개인 경우
        courses=[]
        if '\n' in a:
            courses=a.split('\n')
        else:
            courses=[a] 
            
        #각 과목에 대해서 파싱
        ret=''
        for course in courses:
            #텅 비어있을 경우
            if len(re.findall('[0-9]+',course))==0:
                continue
            
            #아닐 경우
            course_id=re.findall('[0-9]+',course)[0]
            
            if '(재)' in course: #재수강 인정과목
                if len(ret)==0:
                    ret='[2]'+course_id#학수번호 추출
                else:
                    ret+='-[2]'+course_id#학수번호 추출
            elif '(선)' in course:# 선수과목
                if len(ret)==0:
                    ret='[1]'+course_id#학수번호 추출
                else:
                    ret+='-[1]'+course_id#학수번호 추출
            elif '(타)' in course:
                if len(ret)==0:
                    ret='[3]'+course_id
                else:
                    ret+='-[3]'+course_id
        return ret
    return -1
class ParseFitDB:
    def __init__(self,resultdicts,outpath):
        self.resultdicts=resultdicts
        self.outpath=outpath
    def alldf_per_resultdict(self,resultdict): #done!
        keys=resultdict.keys()
        dfkeys=[f for f in keys if 'df' in f]
        
        all_dfs=[]
        for dfkey in dfkeys:
            dfs=list(resultdict[dfkey][1].values()) #list of df
            all_dfs+=dfs 
        
        result_alldf= pd.concat(all_dfs,axis=0)
        return result_alldf
    def alldf_all_resultdict(self): #done!
        
        dfs=[]
        for resultdict in self.resultdicts:
            df=self.alldf_per_resultdict(resultdict)
            
            #중복 없애지 않고 그냥 합치기
            dfs.append(df)
        alldfs=pd.concat(dfs,axis=0)
            #무식
        print(len(alldfs))
        return alldfs

    def check_all_nav_same(self):
        #nav들이 다 같은지 확인해줌
        
        navs=[]
        for resultdict in self.resultdicts:
            nav,_=bar(resultdict['nav'],[i for i in range(0,len(list(resultdict['nav'])))])
            nav.append(navs)
        try:
            navs=pd.DataFrame(navs)
            if len(navs.drop_duplicates())>1:
                print(len(navs.drop_duplicates()))
            else:
                self.nav=nav 
                self.nav_swhere=_
                return True
        except:
            print('하나의 데이터프레임으로 뭉치는 것도 안됨(column 수 다름)')
        return False
    def course_prev(self):
        alldfs=self.alldf_all_resultdict() 
        
        #중복제거
        alldfs_noduplicate=alldfs.drop_duplicates()
        
        #nav부터 확인
        if self.check_all_nav_same()==False:
            assert('nav 항목이 서로 다른 교과과정표 존재')
            
        #nav 같으니까 nav 쓰기(check 함수 이용 이후 self.nav, self.nav_swhere (정수형) 생김)
        #구분부터 있음 
        
        #ourseDB:::: courseDB 1차
        # '영역명(학수번호)*:신설교과목', '교과목명', '이수권장학년', '설정학기', '시간', '학점', '필수여부', '학사편입생제외여부', '개설학과', '2022학년2학기개설여부', '비고'
        coursedb=alldfs_noduplicate.iloc[:5,list(map(decrement,self.nav_swhere[1:]))].copy()
        
        
        #courseDB:::: column 재지정-->good!
        rename_columns={k:v for k,v in zip(coursedb.columns,self.nav[1:])}
        coursedb=coursedb.rename(columns=rename_columns)
      
        #prevDB::::
        prevdb=coursedb[['영역명(학수번호)*:신설교과목','비고']].copy()
        prevdb=prevdb.rename(columns={'영역명(학수번호)*:신설교과목':'course_id','비고':'prev_list'})
        prevdb['prev_list']=prevdb['prev_list'].apply(prev_list_filtered)
        
        #prevDB:::: save
        print('PREV:::::',prevdb.columns)
        prevdb.to_csv(self.outpath+'prev_listDB.txt',index=False,header=None)
        
        #courseDB::::
        #필요한 것 솎아내기
        #개설학과-->subject_id, 
        #영역명(학수번호)*:신설교과목-->course_id
        #2022학년2학기개설여부-->is_open
        #학점-->credit
        #교과목명-->course_name
        #syllabus_id=None
        
        #ourseDB:::: good!
        selected_cols=['개설학과','영역명(학수번호)*:신설교과목','2022학년2학기개설여부','학점','교과목명']
        selected=coursedb[selected_cols].copy()
        selected=selected.rename(columns={'개설학과':'subject_id','영역명(학수번호)*:신설교과목':'course_id','2022학년2학기개설여부':'is_open','학점':'credit','교과목명':'course_name'})
        selected['syllabus_id']=[0]*len(selected)#pd.Series([0]*len(selected))
        
        #ourseDB:::: filter and save
        #is_open 0과 1로 바꿔주기
        #syllabus_id
        selected['is_open']=selected['is_open'].apply(is_open_filtered)
        selected['syllabus_id']=selected['syllabus_id'].apply(syllabus_id_filtered)
        print('COURSEDB:::::',selected.columns)
        alldfs_noduplicate.to_csv(self.outpath+'courseDB.txt',header=None,index=False)
        

if __name__=='__main__':
    #test dataframe_generator
    root='.\\content\\gdrive\\MyDrive\\competition_data\\curri\\'
    outpath='data\\DB\\'
    f=os.walk(root)
    filenames=[]
    for k in f:
        filenames=k[-1]
    
    resultdicts=[]
    #test dataframe_splitter
    for df in dataframe_generator(root,filenames):
	
        #{'nav','gyo','df0'...'df6'}
        result=dataframe_splitter(df)#dfs는 dictionary다. 
        resultnew=run_parser(result)
        resultdicts.append(resultnew)#[(s,df)]
        #print(resultnew.keys())
    
    p=ParseFitDB(resultdicts,outpath)
    #p.check_all_nav_same()
    prevdb=p.course_prev()  
    #print(new_prevdb[~new_prevdb['prev_list'].duplicated()])
    #new_prevdb['prev_list']=prevdb['prev_list'].apply(prev_list_filtered)