#파일 열기

import pandas as pd
import os


class textParser():
    def __init__(self):
        self.descriptors=[]
        self.document_info={}
        self.elements=[]
    def print_dependencies(self):
        pass
    
    def prepare_file(self,filepath):
        
        #open file
        self.descriptors.append(open(filepath,'r'))
        info=None
        content=None
        myPanda=pd.DataFrame(content,columns=[])
        
        #extract info rows and leave only the course rows
        return myPanda 
    def prepare_files(self,path):
     	for filename in os.listdir(path):
            filepath=path+'\\'+filename
            info, content=self.prepare_file(filepath)
            
        return self.descriptors
    
    



if __name__=="__main__":
	a=textParser()
	a.prepare_files('D:\\5.학교 백업\\4학년 1학기\\사이버보안 졸업 프로젝트\\Parser\\txt')
	print('Result\n\n',a.descriptors)