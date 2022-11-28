
import os
import shutil

for file in os.listdir('data/DB'):
    print(file)
    if file[-1]=='t':
        shutil.copyfile('D:\\5.학교 백업\\4학년 1학기\\사이버보안 졸업 프로젝트\\Parser\\data\\DB\\'+file, 'D:\\5.학교 백업\\4학년 1학기\\사이버보안 졸업 프로젝트\\Recommender\\original_data\\'+file)