def is_gyoyang(st):
    if '이화진선미' in st:
        return 1
    elif '기독교와 세계'in st:
        return 1
    elif '기초교양'in st:
        return 1
    elif '영어'in st:
        return 1
    elif '프랑스어'in st:
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


li=['나눔리더십 외', '영어', '융복합교양(표현과예술)','전공기초','전공선택']
print(list(map(standard_to_coursetype,li)))
