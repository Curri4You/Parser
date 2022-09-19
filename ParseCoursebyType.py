from ast import excepthandler
from cmath import nan
import pandas as pd
import numpy as np
from utils import *
import re
import json


#give name 

class ParseCoursebyType:
    def __init__(self,outpath):
        pass
    def big_standard(self,df):
        
        return bigstandard,bigdfs
    def mid_standard(self,dfs):
        return midstandard,middfs
    def small_standard(self,dfs):
        return smallstandard,smalldfs
    def run(self, depth,df):
        if depth==3:
            bigstandard,bigdfs=self.big_standard(df)
            midstandard,middfs=self.mid_standard(bigdfs)
            smallstandard,smalldfs=self.small_standard(middfs)
            return {'depth':depth,'bigstandard':bigstandard,'midstandard':midstandard,'smallstandard':smallstandard,'dfs':smalldfs}
        elif depth==2:
            bigstandard,bigdfs=self.big_standard(df)
            midstandard,middfs=self.mid_standard(bigdfs)
            return {'depth':depth,'bigstandard':bigstandard,'midstandard':midstandard}
        elif depth==1:
            bigstandard,bigdfs=self.big_standard(df)
            return {'depth':depth,'bigstandard':bigstandard}
        else:
            print('depth other than 1,2,3 not implemented:::::::::::::::::')
		
      
#parse general info 
#parse big

#parse mid

#parse small 

#save as csv 
