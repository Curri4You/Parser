import pandas as pd
import numpy as np
from ParseCourseByType_robust import *
from collections import deque
import os
from utils import *
import hashlib


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
    return str(0)

def isinstance_str(a):
    if isinstance(a,str):
        return True
    else:
        return False
def parse_jolup_credit(df):
    #여기서 구해갈거
    
    #심화전공인 경우
    #졸업학점-신입, 졸업학점-편입, 졸업평균평점, 영어강의이수학점,인문학관련교양이수학점,SW교과목이수학점,타과인정제한학점,심화전공설치여부

    #구분이 그래도 빠진 상태로 만남
    lookup=list(df.iloc[:,0])
   
    lookupindex=len(lookup)
    #부복수전공의 경우 2개 열, 심화 전공의 경우 훨씬 많을 것임
    jolup_nav,_nav=bar(df.iloc[lookupindex-2],df.columns)
    jolup_val,_val=bar(df.iloc[lookupindex-1],df.columns)
    
    
    #_nav _val 매칭 확인 -->확인됨
    
    #make it a dict
    ret={}
    for n,v in zip(jolup_nav,jolup_val):
        ret[n]=v
    return ret
class ParseFitDB:
    def __init__(self,resultdicts,outpath):
        self.resultdicts=resultdicts
        self.outpath=outpath
    def alldf_per_resultdict(self,resultdict): #done!
        keys=resultdict.keys()
        dfkeys=[f for f in keys if 'df' in f]
        print(dfkeys)
        all_dfs=[]
        for dfkey in dfkeys:
            dfs=list(resultdict[dfkey][1].values()) #list of df
            all_dfs+=dfs 
        
        result_alldf= pd.concat(all_dfs,axis=0)
        subject_name=resultdict['general_info']['subject_name']
        return result_alldf, subject_name
    def alldf_all_resultdict(self): #done!
        
        dfs=[]
        subject_names=[]
        for resultdict in self.resultdicts:
            df,subject_name=self.alldf_per_resultdict(resultdict)
            
            #중복 없애지 않고 그냥 합치기
            dfs.append(df)
            subject_names+=[subject_name]
        alldfs=pd.concat(dfs,axis=0)
        allsubject_names=pd.DataFrame(subject_names,columns=['subject_name'])
        return alldfs,allsubject_names

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
    def create_course_prev(self):
        #df0~df6을 합치고, df마다 소속된 subject_name을 list로 반환중임
        alldfs,subject_names=self.alldf_all_resultdict() 
        
        #중복제거 하지 말기 
        #nav부터 확인
        if self.check_all_nav_same()==False:
            assert('nav 항목이 서로 다른 교과과정표 존재')
            
        #nav 같으니까 nav 쓰기(check 함수 이용 이후 self.nav, self.nav_swhere (정수형) 생김)
        #구분부터 있음 
        
        #ourseDB:::: courseDB 1차
        # '영역명(학수번호)*:신설교과목', '교과목명', '이수권장학년', '설정학기', '시간', '학점', '필수여부', '학사편입생제외여부', '개설학과', '2022학년2학기개설여부', '비고'
        coursedb=alldfs.iloc[:,list(map(decrement,self.nav_swhere[1:]))].copy()
        
        #courseDB:::: column 재지정-->good!
        rename_columns={k:v for k,v in zip(coursedb.columns,self.nav[1:])}
        coursedb=coursedb.rename(columns=rename_columns)
      
        #prevDB::::
        prev_homo=coursedb[['영역명(학수번호)*:신설교과목','비고']].copy()
        prev_homo=prev_homo.rename(columns={'영역명(학수번호)*:신설교과목':'course_id','비고':'bigo'})
        bigo=prevdb['prev_list'].apply(prev_list_filtered)   
        for i in list(bigo):
            for j in str(i).split():
                
                
        #need work
        #prev_list중 [타]는 prevlist가 아닌 curri_course DB에 들어가야할 것 같음
        #prevDB:::: save
        #print('\n\nPREVLIST DB:::::::::\n',prevdb.head(5))
        #prevdb.to_csv(self.outpath+'prev_listDB.txt',index=False,header=None)
        
        #courseDB::::
        #필요한 것 솎아내기
        #개설학과-->subject_id, 
        #영역명(학수번호)*:신설교과목-->course_id
        #2022학년2학기개설여부-->is_open
        #학점-->credit
        #교과목명-->course_name
        #syllabus_id=None
        
        #courseDB:::: good!
        selected_cols=['영역명(학수번호)*:신설교과목','2022학년2학기개설여부','학점','교과목명']
        selected=coursedb[selected_cols].copy()
        selected=selected.rename(columns={'영역명(학수번호)*:신설교과목':'course_id','2022학년2학기개설여부':'is_open','학점':'credit','교과목명':'course_name'})
        #**중요 
        selected['syllabus_id']=[0]*len(selected)#pd.Series([0]*len(selected))
        
        #courseDB:::: filter and save
        #is_open 0과 1로 바꿔주기
        #syllabus_id
        selected['is_open']=selected['is_open'].apply(is_open_filtered)
        selected['syllabus_id']=selected['syllabus_id'].apply(syllabus_id_filtered)
        
        #print('\n\nCOURSEDB:::::',selected.head(5))
        selected.to_csv(self.outpath+'courseDB.txt',header=None,index=False)
        
    
    #need work 
    #major type 추가
    def create_allmajor(self):
        allmajor=[]
        for resultdict in self.resultdicts:
            '''
            subject_name[PK]
            (전공식별자)
            university_name
            (소속종합대학)
            college_name
            (소속단과대학)
            major_name
            (전공이름)

            '''
            gen_info=resultdict['general_info'] #college, division, subject_name,type
            major_division=gen_info['type']
            university_name='이화여자대학교'#수기! need work
            college_name=gen_info['college']
            major_name=gen_info['subject_name']
            allmajor.append([major_division,university_name,college_name,major_name])
        allmajordf=pd.DataFrame(allmajor,columns=['major_division','university_name','college_name','major_name'])
        
        print('\n\nALL MAJOR DB::::::::::\n',allmajordf.head(5))
        allmajordf.to_csv(self.outpath+'allmajorDB.txt',header=None,index=False)  
    
     
    def create_per_curriculum(self,resultdict):
        
        #금방 구하는 것들
        curr_id=resultdict['currid']
        subject_name=resultdict['general_info']['subject_name']
        the_year=resultdict['year']
        major_division=resultdict['general_info']['type']
        
        #bef 파싱 해야 구하는 것들 
        jolup_credits=parse_jolup_credit(resultdict['bef'])
        elec_num=jolup_credits['졸업학점-신입']
        
        #찐또배기 파싱해야 구하는 것들
        #standard를 파싱하면 된다. 
        
        #0. df항목들 키 모으기
        keys=[]
        for key in resultdict.keys():
            if 'df' in key:
                keys.append(key)
                
        #1.standard 모으기
        standards=[]
        for key in keys:
            s,_=resultdict[key]
            standards.append(s)
            
        #2.조건
        # credittype이 section,course,whole 중 하나고 
        # 첫 구분항목에 "전"이 들어가면 안됨  [전선, 전공기초, 전공필수]
        # 필수여부=필수
        gyo_num=0
        standards=flattenlist(standards)
        for s in standards:
            try:
                if s['credittype'] in ['section','course','whole']:
                    if '전' not in s['구분']:
                        if s['필수여부']=='필수':
                            gyo_num+=int(s['credit'])
                    
            except:
                print('필교학점이 존재하지 않습니다')
            
        
        return {'curr_id':curr_id,'the_year':the_year,'subject_name':subject_name,'major_division':major_division,'elec_num':elec_num,'gyo_num':gyo_num}
    def create_all_curriculum(self):
        '''
        curr_id[PK]
        the_year
        (기준 년도)
        subject_name
        전공이 무엇인지
        major_division
        (주복부전, 심화 구분)
        주/복/부
        elec_num
        전선 필수 학점


        '''
        i=0
        curriculums=[]
        for resultdict in self.resultdicts:
            curriculums.append(self.create_per_curriculum(resultdict))
        
        all_curriculum=pd.DataFrame(curriculums)
        #print('\n\nCURRICULUM DB::::::::::\n',all_curriculum.head(5))
        all_curriculum.to_csv(self.outpath+'curriculumDB.txt',header=None,index=False)
    
    def create_curri_course(self):
        #course마다
        #course의 subject_
        dfs=[]
        for resultdict in self.resultdicts:
            #df 구하기
            df,_=self.alldf_per_resultdict(resultdict)
            
            #nav부터 확인
            if self.check_all_nav_same()==False:
                assert('nav 항목이 서로 다른 교과과정표 존재')
           
            #열이름 재정비
            df=df.iloc[:,list(map(decrement,self.nav_swhere[1:]))].copy()
            rename_columns={k:v for k,v in zip(df.columns,self.nav[1:])}
            df=df.rename(columns=rename_columns)
            course_id=pd.DataFrame(df['영역명(학수번호)*:신설교과목'].values,columns=['course_id'])
            
            #currid 가져오기
            currid=pd.DataFrame([resultdict['currid']]*(len(df)),columns=['curr_id'])
            
            #합치기
            newdf=pd.concat([course_id,currid],axis=1)
            
            #열이름 재지정
            newdf=newdf.rename(columns={'영역명(학수번호)*:신설교과목':'course_id'})
            
            dfs.append(newdf)
            
        curridfs=pd.concat(dfs,axis=0)
        #print('\n\nCURRI-COURSE DB:::::::::::\n',curridfs.head(5))
        curridfs.to_csv(self.outpath+'curri_courseDB.txt',index=False,header=None)
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
    
    p=ParseFitDB(resultdicts,outpath)
    _,subject_names=p.alldf_all_resultdict()
    print(subject_names)
    '''
    p.create_allmajor()
    p.create_course_prev()
    p.create_all_curriculum()
    p.create_curri_course()
    '''