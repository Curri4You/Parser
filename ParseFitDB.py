'''
g,h,j,js
{'ids':final_ids,'dfs':final_dfs,'standards':final_standards}

final_ids: ['1-1-0']
final_dfs

''' 
import json
import pandas as pd
import numpy as np
from ParseCoursebyType import *
from collections import deque


'''
    USER_TABLE
    
    ################
    파서로부터 받아올 수 있는 DB가 아니다. 가입시 정보를 받아서 전처리를 해야 넣을 수 있다. . 
    ################
    필요한 것: user_id,user_password, user_name,student_id,major_name,major_division(부복수전공),university_name,college_name
    
'''
  
'''   
    ALL_MAJOR
    
    ################
    모든 전공 정보를 긁어와야하므로, 모든 CURRICULUM을 종합해서 만들어야 한다. 
    ################
    필요한 것:major_id,university_name,college_name,major_name
    파서에서 구할 수 있는 것: 전부
    
    general ifno: {'college': '엘텍공과대학', 'div': ' 소프트웨어학부', 'subject_name': ' 컴퓨터공학', 'type': 1, 'year': 2020, 'curr_id': 0}
    nav: (['구분', '영역명(학수번호)*:신설교과목', '교과목명', '이수권장학년', '설정학기', '시간', '학점', '필수여부', '학사편입생제외여부', '개설학과', '2022학년2학기개설여부', '비고'], [1, 2, 4, 8, 9, 11, 12, 13, 14, 16, 18, 19])
    
'''
def allmajorDB(all_curriculum):
    #목적: json파일로
    #all_curriculum: list of parser resultdict 
    #매번 호출될 때 all_curriculum에 담긴 건 겹치는 curriculum은 없을 것이라고 가정한다. 
    
    #open filename tracking csv
    last=-1
    try:
        f=open('allmajor_filename.txt','r')
        last=deque(f,1)[0]
        f.close()
    except:
        f=open('allmajor_filename.txt','a')
        last='0'
        f.write(last)
        f.close()
    
    allmajor_df=[]
    
    
    for curriculum in all_curriculum:
        general_info=curriculum['general_info']
        #print(general_info)
        subject_id=find_subject_id(general_info['div'])
        university_name='이화여자대학교'
        college_name=general_info['college']
        major_name=general_info['div']
        
        new_df=[subject_id,university_name,college_name,major_name]
        #print(new_df)
        allmajor_df.append(new_df)
    allmajor_df=pd.DataFrame(allmajor_df,columns=['subject_id','university_name','college_name','major_name'])
    last=str(int(last)+1)
    print(allmajor_df)
    filename='data\\major\\'+last+'.txt'
    allmajor_df.to_csv(filename)
'''   
    COURSE
    
    ################
    모든 COURSE 정보를 긁어와야하므로, 모든 CURRICULUM을 종합해서 만들어야 한다. 
    ################
    필요한 것:course_id(학수번호) subject_id,professor(강의계획표 or 직접입력), is_english(불가),is_online(불가), credit, course_anme, syllabus_id(강의계획표)
    파서에서 구할 수 있는 것: course_id(학수번호), subject_id, credit, course_name
    
    general ifno: {'college': '엘텍공과대학', 'div': ' 소프트웨어학부', 'subject_name': ' 컴퓨터공학', 'type': 1, 'year': 2020, 'curr_id': 0}
    nav: (['구분', '영역명(학수번호)*:신설교과목', '교과목명', '이수권장학년', '설정학기', '시간', '학점', '필수여부', '학사편입생제외여부', '개설학과', '2022학년2학기개설여부', '비고'], [1, 2, 4, 8, 9, 11, 12, 13, 14, 16, 18, 19])
    
'''
def find_subject_id(name):
    try:#파일이 열리면
        file=pd.read_csv('subject_id.csv')
        
        #찾으면 
        retrieval=file[file['subject_name']==name]
        
        if len(retrieval)>0:
            return int(retrieval['subject_id'])
        else:
            new_id= int(file['subject_id'].iloc[-1]+1)
            new_row=pd.DataFrame([[name,new_id]],columns=['subject_name','subject_id'])
            file.append(new_row)
            file.to_csv('subject_id.csv')
            return new_id
    except:
        file=pd.DataFrame([[name,0]],columns=['subject_name','subject_id'])
        file.to_csv('subject_id.csv')
        return 0
    
    
def all_df(dfs):
    df_list=[]
    for choice in ['g','h','j','js']:
        tmp=dfs[choice]
        for df in tmp['dfs']:
            df_list.append(df)
    
    return pd.concat(df_list,axis=0)

def save_courselist(df,filename,filetype=0):
    #flush it in csv
    #flush it in json
    #just yield 
    if filetype==0:
        df.to_json('data\\course\\'+filename)
    elif filetype==1:
        df.to_csv('data\\course\\'+filename)
    
def courseDB(all_curriculum):
    #목적: json파일로
    #all_curriculum: list of parser resultdict 
    
    #track filename
    last=-1
    try:
        f=open('course_json_filename.txt','r')
        last=deque(f,1)[0]
        f.close()
    except:
        f=open('course_json_filename.txt','a')
        last='0'
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
        
        #print(df.columns)
        tmp=df.iloc[:,[course_id_index,subject_id_index,credit_index,course_name_index]]
        prev_cols=tmp.columns
        new_cols=['course_id','subject_id','credit','course_name']
        rename_dict={p:n for p,n in zip(prev_cols,new_cols)}
        tmp=tmp.rename(columns=rename_dict)
        #tmp.rename(columns={course_id_index:'course_id',subject_id_index:'subject_id',credit_index:'credit',course_name_index:'course_name'},inplace=True)
        print(tmp)
        #씨발 왜 하나만 되는 거야 
        tmp['subject_id']=tmp['subject_id'].map(find_subject_id)
        
        
        #turn anme into filename
        #filename=last+'.json'
        filename=last+'.txt'
        save_courselist(tmp,filename,1)
    
    with open('course_json_filename.txt','a') as f:
        f.write(last)
        
        
        

    

if __name__=='__main__':
    
    sample_path='content/gdrive/MyDrive/competition_data/curri/h_json.json'
    
    filenames=['20sabo_xls.csv','20comgong_xls.csv']   
    root='.\\content\\gdrive\\MyDrive\\competition_data\\curri\\'
    result= run_parser(root,filenames)
    
    resultdicts=[]
    for resultdict in result:
        resultdicts.append(resultdict)
        for choice in ['g','h','j','js']:
            chosen=resultdict[choice]
            #print(chosen.keys())
            #print(chosen['dfs'])
        
    allmajorDB(resultdicts)
    #courseDB(resultdicts)
    #check json
    
    #print(pd.read_json('data\\major\\1.json'))
    #print(pd.read_json('data\\course\\3.json'))
        