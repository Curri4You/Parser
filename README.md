# ParseCourseByType_robust

## ParseCourseByType

### init(outpath,resultdict):
input:
outpath / str / 저장 위치 path
resultdict / dict / data_splitter()의 결과 {'nav','gyo','df0'...'df6'}

### pretty_standard_bynav(raw_standard,type='not big')
input:
raw_standard / pd.Series / standard가 담긴 행 그대로
type / str / 'not big' 혹은 'big' 
(type이 not big이면 resultdict['nav'] 기준 첫 것을 빼고 진행해야하며, big 이면 안 빼고 진행해야한다.)
output:
finalstandard / dictionary /
bar 함수를 통해서 얻던 standard를 key:value 쌍으로 이쁘게 바꾼 것 
'구분', '구분2(optional)', '필수여부', '학사편입생제외여부'
'diff_by_div'
		--> (True): 1_credit, 2_credit (str인 숫자)
		--> (False): credit (str 인 숫자)

'credittype'
		--> 'per_div' (심화, 그 외 구분되어 필수 이수 학점 알려줌), 
				'1_credit'
				'2_credit'
		--> 'section'(영역있음),
				'section'
				'credit'
		--> 'course'(과목수있음) 
				'course'
				'credit'
		--> 'whole'(그냥)
				'credit'

### general_info():
output: {'college': 대학, 'div':학부, 'subject_name': 전공, 'type': 주복부구분,}
(이때 주복부구분은 types={'주전공':1,'복수전공':2,'부전공':3,'연계전공':4} 참고)

### mid only()
### mid_small()

### small_only()

### run(df )
input:
df / pandas.DataFrame / 
### run_parser(resultdict)
input: 
resultdict / dicti /data_splitter의 결과

output: 
newresultdict / dict / 

key
'elec_num' / resultdict['elec_num']
'nav' / resultdict['nav']
'currid' / resultdict['currid']
'year' / resultdict['year']
'general_info' / parser.general_info() {'college': 대학, 'div':학부, 'subject_name': 전공, 'type': 주복부구분,}
dfN: (standards, df_dict)
/ standards  / list of finalstandard
/ df_dift  / '1-1-1':df 



## Outside class
### flattenlist(nestedlist)
input: nestedlist / list /
output: flattened 된 nestedlist
깊이가 어떻게 되든 다 1*N의 리스트로 만들어주는 recursvie한 함수

### flattendict(dictnestedlist)
input: dictnestedlist / list /
output: dictionary로 구성된 리스트
recursive하지 않아서 [[{dict},{dict}],{dict}] 와 같이 1개 깊이 정도의 nestedlist만 풀어서 하나의 dictionary로 바꾸어줌 

### has_mid(a)
input: a / s / 구분자 string인 a
output: '-'를 가지는 mid 구분자라면 True, 아니면 False

### has_small(a)
input: a / s / 구분자 string
output: '#'나 '['을 가지는 small 구분자라면 True, 아니면 False

### depth(example,col)
input: 
example / df /  수업과 미처 추출되지 않은 standard행이 있을 수 있는 dataframe, column은 resultdict 내 df들과 같다.
col / int / 구분자를 찾을 위치를 의미한다. resultdict['nav']인 리스트 속'구분'행이 포함되게 자르면 1, 안 포함되게 자르면 0을 넣어야 한다. 
output:
midstandard만 있으면 2
smallstandard만 있으면 1
둘 다 있으면 3
둘 다 없으면 0
반환

### bar(ser,cols)
input:
ser / pd.Series / na도 막 들어가있는 df 행으로 standard 정보 행을 받아야 한다.
cols / iterable / 주로 리스트를 받는데 curriculum 속 df의 column으로 대게 1~20의 숫자가 string으로 변환된 것이다.
output:
keys / list / ser 중 의미있는 정보를 모은 리스트
key_indices / list / cols 대비 keys의 열 위치 리스트 

### find_index(df,col,signs)
input:
df / pd.DataFrame / standard와 course가 혼합되어있는 dataframe
col / int /  구분자를 찾을 위치를 의미한다. resultdict['nav']인 리스트 속'구분'행이 포함되게 자르면 1, 안 포함되게 자르면 0을 넣어야 한다. 
signs / str / '[ #'와 같이 ' '로 구분된 sign들의 집합이거나 '#'와 같은 단일 sign으로 되어있다
output:
_index / list / 정수 리스트 

