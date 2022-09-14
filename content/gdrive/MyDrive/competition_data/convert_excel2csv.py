import os
import pandas as pd
root='content\\gdrive\\MyDrive\\competition_data\\curri\\'
f=os.walk(root)
#('D:\5.학교 백업\4학년 1학기\사이버보안 졸업 프로젝트\Parser\content\gdrive\MyDrive\competition_data\curri'):
for files in f:
    for file in files[2]:
        read_file = pd.read_excel(root+file)
        print('::::::::::',file,'::::::::::::::::')
        read_file.to_csv(root+file[:-4]+'.csv')