from ast import excepthandler
from cmath import nan
import pandas as pd
import numpy as np
from utils import *
import re
import json

def general_info_extract(ser,columns=['flag','type','necessary','pyeonip_listen']):
	info=[]
	#내용이 있는 열만 모은다
	for element in ser:
		#열 내용 확인
		#print(':::::::::element',element)
		if element!='': 
			info.append(element)
	return pd.DataFrame([info],columns=columns)

def bar(eesoo):
  pattern=re.compile('\d+')#('\[\d+[^0-9]+\d+[^0-9]+')
  info=re.findall(pattern,eesoo)
  if len(info)!=2:
    print('bar calculation is wrong',eesoo,':::',info)
  return pd.DataFrame([info],columns=['num_course_bar','num_credit_bar'])

#need work: 임시로 그냥 미리 추출해놓은 것 씀
def import_columns():
    with open('nav_json.json','r') as f:
    	return json.load(f)['course_columns']
class ParseCourseSet:
    def __init__(self,df):
        self.orig_df=df.fillna('')#콜랩에서는 ''더니 여기에서는 또 Nan으로 나와서 전부 바꿔줌
        self.general_info=general_info_extract(self.orig_df.iloc[0])
        self.course_columns=import_columns()
    
    
    def take_away_big_standards(self):
        #핵심교양은 '핵심교양' 하나지만 기초교양은 '기초교양'이 여러개임
        df=self.orig_df.copy()
        num_big_standards=len(df)-len(df[df[0]==''])
        print(num_big_standards)
        self.num_big_standards=num_big_standards
        #만약 num_big_standards가 하나라면 single_big_standard를 실행한다.
        return num_big_standards
    def single_big_standard(self):
        #일단 big standard를 없앤다
        df=self.orig_df.copy().iloc[1:,1:]
        self.df=df
        #그리고 나머지 divisor를 찾는다
        l=df[1].values 
        divisor=[]
        for index,i in enumerate(l):
            try:
                int(i)
            except:
                if i!='':
                    divisor.append((index,i.strip(' ')))
        self.divisor=divisor
    def single_json_on_single_df(self):
        #prepare divisor and df
        self.single_big_standard()
        
        #init for use
        big_standards={}
        standards={}
        docs={}
        joined={'general_info':self.general_info.to_json()}#전송될 json
        course_columns=self.course_columns
        
        #init for shorter naming
        divisor=self.divisor
        courses=self.df.copy()
        
        #파싱 시작
        for i,tup in enumerate(divisor):
            index,val=tup
            start=index
            
            #:::::::::::::::::::::::::::::::대기준::::::::::::::::::::::::::::::::::::
            if '-' in val:
                if len(standards)!=0:#두 번째 이상 big standard인 경우 전 big_standard 것을 저장한다
                    key=list(big_standards.keys())[-1] #직전 big divisor의 val이 필요함
                    joined[key]={'big_standard':big_standards[key],'small_standard':standards,'docs':docs}
                    standards={}
                    docs={}
                biginfo=list(courses.iloc[index])#이수항목 빼고
                flag=pd.DataFrame([biginfo[0].strip(' ')],columns=['flag'])
                eesoo=bar(biginfo[2])
                other=[]
                for metainfo in biginfo[3:]:
                    if metainfo=='':
                        continue
                    else:
                        other.append(metainfo)
                if len(other)==1:#''가 아닌 항목이 1개라면 '필수'가 없는거고 2개라면 있는거다 
                    other.insert(0,'None')
                other=pd.DataFrame([other],columns=['necessary','pyeonip_listen'])
                big_standards[val]=pd.concat([flag,eesoo,other],axis=1).to_json()#big standards 저장
            
            #:::::::::::::::::::::::::::::::소기준:::::::::::::::::::::::::::::::::::                
            else:
                if '융복합' in val:##융복합교양이라면 index 2에 [1과목 3학점 이수], index 12에 편입생 들어야하는지 여부[Y/N]
                    eesoo=bar(courses.iloc[index,2])
                    pyeonip=pd.DataFrame([courses.iloc[index,12]],columns=['pyeonip_listen'])
                    standards[val]=pd.concat([eesoo,pyeonip],axis=1).to_json()#small standard 저장
                elif '큐브' in val:#-큐브,#큐브는 12번째 열은 '필수' 열이고 13번째 열은 편입생 제외여부 열이다
                    pilsoo=pd.DataFrame([courses.iloc[index,12]],columns=['necessary'])
                    pyeonip=pd.DataFrame([courses.iloc[index,13]],columns=['pyeonip_listen'])
                    standards[val]=pd.concat([pilsoo,pyeonip],axis=1).to_json()#small standard 저장
                else:
                    print(val,'is neither 융복합 nor 큐브')
            #데이터프레임 자르기
            if i==len(divisor)-1:#마지막이면
                doc=courses.iloc[start:]
                doc=doc.drop(labels=[2,4,5,6,7,9,19],axis='columns')
                docs[val]=doc.to_json()
            else:
                doc=h_courses.iloc[start:divisor[i+1][0]]
                doc=doc.drop(labels=[2,4,5,6,7,9,19],axis='columns')
                docs[val]=doc.to_json()
            
        #마지막 big standard를 위한 저장 
        if len(standards):
            print('마지막?')
            key=list(big_standards.keys())[-1]
            #직전 big divisor의 val이 필요함
            joined[key]={'big_standard':big_standards[key],'small_standard':standards,'docs':docs}
        return joined
    def run_singular(self,save_path):
        joined=self.single_json_on_single_df()
        with open(save_path,'w') as f:
            json.dump(joined,f)
        return joined
     
class ParseNav:
    pass

'''
nav=df.iloc[:a_index]
df0=df.iloc[a_index:h_index]#기초교양
df1=df.iloc[h_index:jg_index] #핵심교양
df2=df.iloc[jg_index:j_index]#전공기초
df3=df.iloc[j_index:g_index]#[교과과정안내]
'''
if __name__=='__main__':
    
    root='.\\content\\gdrive\\MyDrive\\competition_data\\curri\\'
    #한 개 df에 대해서만 test 해보자
    i=0
    dfs=[]
    for df in dataframe_generator(root,filenames):
        dfs=dataframe_splitter(df)
        if i==0:
            break
    
    h_courses=dfs[2]
    #print(h_courses.iloc[0])
    parser=ParseCourseSet(h_courses)
    #print(parser.general_info)
    joined=parser.run_singular(root+'h_json.json')
    print(joined['general_info'])

#주의
'''
general_info는 json으로 dump했을 때 
str(index):값
으로 표현되고 있다
'''