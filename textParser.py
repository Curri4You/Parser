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
    
    def prepare_files(self,filepath):
        
        #open file
        for filename in os.listdir(filepath):
            filename_full=filepath+'\\'+filename
            self.descriptors.append(open(filename_full,'r'))
            
        #extract info rows and leave only the course rows

        return self.descriptors
    
    def files2pd(self):
        pass


if __name__=="__main__":
	a=textParser()
	a.prepare_files('D:\\5.학교 백업\\4학년 1학기\\사이버보안 졸업 프로젝트\\Parser\\txt')
	print('Result\n\n',a.descriptors)