import pandas as pd
import numpy as np
from ParseCourseByType_robust import *
from collections import deque
import os
from utils import *
import hashlib
import os.path as osp


def decrement(a):
    return a-1
def is_open_filtered(a):
    if isinstance(a,str):
        if a=='Y':
            return 1
    return 0 
def syllabus_id_filtered(a):
    return 0
def find_filled_element(li):
    for l in li:
        if len(l)!=0:
            return l 
    return '-1'
def filter_bigo(a):
    #한 개 course의 란에 대해 등장 
    if isinstance(a,str):
        #여러개인 경우
        #need work: 서로 다른 줄 뿐만 아니라 중첩이 되는 경우도 있다.
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
            course_id=find_filled_element(re.findall('[0-9]+',course)) # findall 결과 중 비어있는 것이 등장하지 않도록
            if course_id=='-1':
                continue 
            
            if '(재)' in course and '(타)' in course:
                ret+='[2]'+course_id+'-[3]'+course_id
            elif '(재)' in course: #재수강 인정과목
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
                print(course)
                if len(ret)==0:
                    ret='[3]'+course_id
                else:
                    ret+='-[3]'+course_id
        if ret!='': #비어있는 상태로 끝나지 않으면
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
def index_interpreter(all_indices): #[1-1-1,1-1-2,1-2-0,1-3-1] 각각의 standard list 내 위치 제공
    standard_indices=[]
    big_increment=1
    mid_increment=0
    tmp=0
    for index,k in enumerate(all_indices):
        _,mid,small=list(map(int,k.split('-')))
        if mid==0 and small==0:# 1-0-0, 밖에 안됨
            standard_indices.append(index)
        elif mid==0 and small!=0:#1-0-1,1-0-2... 밖에 안됨
            standard_indices.append(big_increment+index)
        elif mid!=0:
            if small==0: 
                standard_indices.append(big_increment+mid_increment+index)
            else:
                if tmp!=mid:
                    tmp=mid
                    mid_increment+=1
                standard_indices.append(big_increment+mid_increment+index)
        else:
            print('??')
    return standard_indices
def strip_name(s):
    s=s.strip() 
    s=re.sub('[\t\n-]','',s)
    return s
def get_standard_name(st): #구분, 구분2 등 뭐가 있고 없을 수 있음 
    #이름 분명히하기
    keys=st.keys()
    if '구분'in keys:
        if '구분2' in keys:
            name=strip_name(st['구분'])+'-'+strip_name(st['구분2'])
        else:
            name=strip_name(st['구분'])
    else:
        if '구분2' in keys:
            name=strip_name(st['구분2'] )
        else:
            name=''
            print('Something gone wrong, no standard name ') 
    return name    
def is_gyoyang(st):
    if '기초교양'in st:
        return 1
    elif '영어'in st:
        return 1
    elif '프랑스어'in st:
        return 1
    elif '일본어' in st:
        return 1
    elif'독일어'in st:
        return 1
    elif '스페인어'in st:
        return 1
    elif '러시아어'in st:
        return 1
    elif '사고와표현'in st:
        return 1
    elif'나눔리더십' in st:
        return 1
    elif '이화진선미' in st:
        return 1
    elif '기독교와세계'in st:
        return 1
    elif '융합기초' in st:
        return 1
    else:
        return 0
def is_pilgyo(st):
    if '융복합교양' in st:
        return 1
    elif  '큐브' in st:
        return 1
    return 0
def is_jeongi(st):
    if '기본이수' in st:
        return 1
    elif  '전공기초' in st:
        return 1
    return 0
def standard_to_coursetype(st):
    coursetype=-1
    if is_gyoyang(st):
        coursetype=2
    elif is_pilgyo(st):
        coursetype=3
    elif '전공필수' in st:
        coursetype=4
    elif is_jeongi(st):
        coursetype=5
    elif '전공선택' in st:
        coursetype=1
    
    return coursetype

class ParseFitDB:
    def __init__(self,resultdicts,outpath):
        self.resultdicts=resultdicts
        self.outpath=outpath
        if self.check_all_nav_same()==False:
            assert('nav 항목이 서로 다른 교과과정표 존재')
    def alldf_per_resultdict(self,resultdict): #done!
        keys=resultdict.keys()
        dfkeys=[f for f in keys if 'df' in f]
        #dfkeys 내용 확인하기 
        # print(dfkeys)
        all_dfs=[]
        for dfkey in dfkeys:
            dfs=list(resultdict[dfkey][1].values()) #list of df
            all_dfs+=dfs 
        
        result_alldf= pd.concat(all_dfs,axis=0)
        return result_alldf
    def alldf_all_resultdict(self): #done!
        
        dfs=[]
        subject_names=[]
        for resultdict in self.resultdicts:
            subject_name=resultdict['general_info']['subject_name']
            df=self.alldf_per_resultdict(resultdict)
            
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
            nav,nav_swhere=bar(resultdict['nav'],[i for i in range(0,len(list(resultdict['nav'])))])
            nav.append(navs)
        try:
            navs=pd.DataFrame(navs)
            if len(navs.drop_duplicates())>1:
                #error indicator
                print(len(navs.drop_duplicates()))
            else: #다 중복이면 (원하는 결과)
                self.nav=nav 
                self.nav_swhere=nav_swhere
                return True
        except:
            #error indicator
            print('하나의 데이터프레임으로 뭉치는 것도 안됨(column 수 다름)')
        return False
    def create_intersected(self):
        
        curr_ids=[]
        course_ids=[]
        for resultdict in self.resultdicts:
            #curr id 찾기
            curr_id=resultdict['currid']
            
            #df 추출
            df=self.alldf_per_resultdict(resultdict)
            df_copy=df.iloc[:,list(map(decrement,self.nav_swhere[1:]))].copy() #필요한 열만 추출하기
            rename_columns={k:v for k,v in zip(df_copy.columns,self.nav[1:])} #열 이름 설정하기 
            df_cut=df_copy.rename(columns=rename_columns) #열 이름 설정하기 
            all_course_id_bigo=df_cut[['영역명(학수번호)*:신설교과목','비고']].copy()#필요한 열만 확인하기
            bigo=all_course_id_bigo['비고'].apply(filter_bigo) #비고란 처리하기
            for course_id, bg in zip (list(all_course_id_bigo['영역명(학수번호)*:신설교과목']),bigo):
                if '[3]' in bg:
                    curr_ids.append(curr_id)
                    course_ids.append(course_id)
                else:
                    test=re.findall('\[[0-9]+\]',bg)
                    if len(test)>0:
                        print(course_id,curr_id,test)
    
          
        if len(curr_ids)>0:
            tadb=pd.DataFrame({'curr_id':curr_ids,'course_id':course_ids}).to_csv(osp.join(self.outpath,'intersected_listDB.txt'),header=None,index=False)
        else:
            tadb=pd.DataFrame({'curr_id':curr_ids,'course_id':course_ids},index=[0]) .to_csv(osp.join(self.outpath,'intersected_listDB.txt'),header=None,index=False)
            
    def create_course_prev_homo(self):
        #df0~df6을 합치고, df마다 소속된 subject_name을 list로 반환중임
        alldfs,subject_names=self.alldf_all_resultdict() 
        
        
        #ourseDB:::: courseDB 1차
        # '영역명(학수번호)*:신설교과목', '교과목명', '이수권장학년', '설정학기', '시간', '학점', '필수여부', '학사편입생제외여부', '개설학과', '2022학년2학기개설여부', '비고'
        coursedb=alldfs.iloc[:,list(map(decrement,self.nav_swhere[1:]))].copy()
        
        #courseDB:::: column 재지정-->good!
        rename_columns={k:v for k,v in zip(coursedb.columns,self.nav[1:])}
        coursedb=coursedb.rename(columns=rename_columns)
      
        #prev, homo, intersected DB::::
        prev_homo=coursedb[['영역명(학수번호)*:신설교과목','비고']].copy()
        prev_homo=prev_homo.rename(columns={'영역명(학수번호)*:신설교과목':'course_id','비고':'bigo'})
        bigo=prev_homo['bigo'].apply(filter_bigo)  #-가 여러개 있을 수 있음
        
        
        prevlist=[]
        homolist=[]
        
        for cid,i in zip(prev_homo['course_id'].tolist(), list(bigo)):
            
            if '-' in i: #여러개 있는 경우 
                print(len(str(i).split('-')),re.findall('\[[0-9]+\]',str(i)))
                for  j in str(i).split('-'): 
                    j_cid=j[3:]
                    if '[1]' in j: 
                        homolist.append((cid,j_cid))
                    elif '[2]' in j:
                        prevlist.append((cid,j_cid)) 
                        #[3]의 경우 타전공을 의미(intersected) 제외한다.
                    
            else:#한 개 있는 경우
                i_cid=i[3:]
                if '[1]' in i: 
                    homolist.append((cid,i_cid))
                elif '[2]' in i:
                    prevlist.append((cid,i_cid)) 
                else:
                    #다 0으로 잘 채워져있는 것 같다. 
                    #print('bigo:',i)
                    continue
        #내용 확인       
        #print(homolist,prevlist,intersectedlist) 
          
        if len(homolist)>0:
            homodb=pd.DataFrame(homolist,columns=['course_id', 'homo_course_id']) 
        else:
            homodb=pd.DataFrame(homolist,columns=['course_id', 'homo_course_id'],index=[0]) 
        if len(prevlist)>0:
            prevdb=pd.DataFrame(prevlist,columns=['course_id','previous_course_id'])
        else:
            prevdb=pd.DataFrame(prevlist,columns=['course_id','previous_course_id'],index=[0])
        
        homodb.to_csv(self.outpath+'homo_listDB.txt',index=False,header=None )
        prevdb.to_csv(self.outpath+'prev_listDB.txt',index=False,header=None)
        
        
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
        
        #print('\n\nALL MAJOR DB::::::::::\n',allmajordf.head(5))
        allmajordf.to_csv(self.outpath+'allmajorDB.txt',header=None,index=False)  

    def create_curr_stand_course_per_curriculum(self,resultdict):
            
            
            
        curr_id=resultdict['currid'] 
        
        
        #1.standard 모으기
        
        ## df 들 모으기
        keys=[]
        for key in resultdict.keys():
            if 'df' in key:
                keys.append(key)
        ## standard를 모으는 동시에, standard 별 수업 모으기 
        curr_standards=[]
        standard_course=[]
        for key in keys:
            s,k=resultdict[key] #standard list와 standard 별 id: df 
            
           
            
            ##standard_course 모으기 
            s_indices=index_interpreter(list(k.keys()))
            for standard_index,dataframe in zip(s_indices,list(k.values())):
                
                #print(s[standard_index],'\n---------\n',dataframe.iloc[:,decrement(self.nav_swhere[1])].values)
                #print(dataframe.columns)
                name=get_standard_name(s[standard_index])
                standard_course+=[(curr_id,name,course_id) for course_id in dataframe.iloc[:,decrement(self.nav_swhere[1])].values ]
            
            
            ###무지성 standard모으기 
            #st를 standard name, credit type, must_limit 구하기
            #NeedWork: small standard의 경우 mid나 big에 의해 필수 및 제한사항이 영향받을 수 있다. 

            #curr_standards+=[(curr_id,st) for st in s] 
            for s_i ,val in zip(s_indices,list(k.keys())):
                st=s[s_i]
                big,mid,small=tuple(map(int,val.split('-')))
                
                #일단 주어진 st에 모든 정보가 있는지 확인한다. 
                name=get_standard_name(st)
                try:
                    if st['diff_by_div']==True: 
                        credit_1=st['1_credit']
                        credit_2=st['2_credit']
                        curr_standards.append((curr_id,name+'(심화)',credit_1))
                        curr_standards.append((curr_id,name+'(기타)',credit_2))
                    else:
                        credit=st['credit'] 
                        curr_standards.append((curr_id,name,credit))
                except:
                    #'credit'not found 
                    #mid는 존재하는데 small이 존재하지 않을 경우는 없다    
                    credit=0
                    curr_standards.append((curr_id,name,credit))
       
        curr_standardsDB=pd.DataFrame(curr_standards,columns=['curr_id','standard_name','credit'])
        standard_courseDB=pd.DataFrame(standard_course,columns=['curr_id','standard_name','course_id'])

        
        return curr_standardsDB,standard_courseDB
        
        return curr_standardsDB,standard_courseDB
    def create_curr_stand_course_all_curriculum(self):
        #모으기
        curr_standards=[]
        standard_courses=[]
        ##curri_courses=[]
        
        for resultdict in self.resultdicts:
            c,s=self.create_curr_stand_course_per_curriculum(resultdict)#cc
            curr_standards.append(c)
            standard_courses.append(s)
            ##curri_courses.append(cc)
        
        #합치기
        curr_standardsDB=pd.concat(curr_standards,axis=0)
        standard_courseDB=pd.concat(standard_courses,axis=0)
        curri_courseDB=standard_courseDB.copy()
        curri_courseDB=curri_courseDB.rename(columns={'standard_name':'course_type'})
        curri_courseDB['course_type']=curri_courseDB['course_type'].apply(standard_to_coursetype)
        
        
        '''
        with open('log.txt','w') as f:
            t=curri_courseDB[curri_courseDB['course_type']==-1]
            s=''
            for _ in list(t['standard_name'].values):
                s+='\n'+_
            f.write(s)
            print(s)'''
            
        
        #저장하기
        curr_standardsDB.to_csv(self.outpath+'curr_standardsDB.txt',index=None,header=False)
        standard_courseDB.to_csv(self.outpath+'standard_courseDB.txt',index=None,header=False)
        standard_courseDB.to_csv(self.outpath+'standard_courseDB_header.txt',index=None,header=True)
        curri_courseDB.to_csv(self.outpath+'curri_courseDB.txt',index=None,header=False)
    
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
            #내용 확인
            #print(s)
            do=0
            try:
                if '전' not in s['구분'] and '기본이수' not in s['구분']:
                    gyo_num+=int(s['credit'])
                    do+=1
            except:
                pass #print('구분 or 필수여부 doesnt exist',s)
            try:
                if '전' not in s['구분2'] and do==0 and '기본이수' not in s['구분']:
                    gyo_num+=int(s['credit'])
            except:
                print('구분2 or credit doesnt exist',s)
                        
                    
            
        
        return {'curr_id':curr_id,'the_year':the_year,'subject_name':subject_name,'major_division':major_division,'elec_num':elec_num,'ge_info':gyo_num}
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
            
            #course_id 가져오기 
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
    def create_curri_course_by_standard(self):
        a=pd.read_csv(self.outpath+'standard_courseDB_header.txt')
        a['standard_name']=a['standard_name'].apply(standard_type)
        a.rename(columns={'standard_name':'course_type'})   
        a.to_csv(self.outpath+'curri_courseDB2.txt',index=False,header=None)
def standard_type(standard_name):
    if isinstance(standard_name,str):
        if '전공선택' in standard_name:
            return '1'
        elif ('전공기초' or  '기본') in standard_name:       
            return '4'
        else:
            return '3'
    return '-1'
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
    #p.create_intersected()
    #실제 교과목명임 
    #_,subject_names=p.alldf_all_resultdict()
    #print(subject_names)
    #p.check_all_nav_same()
    
    #p.create_curr_stand_course_all_curriculum()
    
    #p.create_curri_course_by_standard()
    p.create_curr_stand_course_all_curriculum()
    #p.create_allmajor() 
    #p.create_all_curriculum()
    
    