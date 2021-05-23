#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 21 12:06:50 2021

@author: yuxia
"""

import sudoku_cv_picprocess as picprocess
import numpy as np
import cv2
from matplotlib import pyplot as plt
import pandas as pd
#%%
grid = [8,0,0,0,1,0,0,0,9,
        0,5,0,8,0,7,0,1,0,
        0,0,4,0,9,0,7,0,0,
        0,6,0,7,0,1,0,2,0,
        5,0,8,0,6,0,1,0,7,
        0,1,0,5,0,2,0,9,0,
        0,0,7,0,4,0,6,0,0,
        0,8,0,3,0,9,0,4,0,
        3,0,0,0,5,0,0,0,8]
grid1 = [0,0,0,6,0,4,7,0,0,
         7,0,6,0,0,0,0,0,9,
         0,0,0,0,0,5,0,8,0,
         0,7,0,0,2,0,0,9,3,
         8,0,0,0,0,0,0,0,5,
         4,3,0,0,1,0,0,7,0,
         0,5,0,2,0,0,0,0,0,
         3,0,0,0,0,0,2,0,8,
         0,0,2,3,0,1,0,0,0]
grid2 = [0,0,0,0,7,0,0,0,0,
         0,0,6,0,0,0,7,0,0,
         2,0,0,8,0,3,0,0,5,
         0,0,8,0,0,0,5,0,0,
         0,2,0,4,0,9,0,3,0,
         9,0,0,6,0,7,0,0,2,
         5,0,9,0,0,0,3,0,8,
         0,0,3,0,0,0,9,0,0,
         0,7,0,9,0,4,0,5,0]
grid = np.array(grid).reshape(9,9)
path ='/Users/yuxia/SuDoKu/Test13.jpeg'
model_path = '/Users/yuxia/SuDoKu/PyTorch/PytorchModel_AddFonts_space_duplicate.pt'
model_path1 = '/Users/yuxia/SuDoKu/PyTorch/PytorchModel_AddFonts+MNIST_space_Revised.pt'
#pred = picprocess.predict_board1(path,model_path)
#pred1 = picprocess.predict_board1(path,model_path1)
#print(pred)
#print(pred1)

#%%
test_list = pd.read_csv('/Users/yuxia/SudoKu/test_result.csv')
accuracy= []
for i in range(len(test_list)):
    correct = 0
    correct1 = 0
    path = test_list.iloc[i,0].strip()
    pred = picprocess.predict_board1(path,'/Users/yuxia/SuDoKu/PyTorch/PytorchModel_AddFonts+MNIST_space_Revised.pt')
    pred = pred.reshape(81)
    #print(pred)
    pred1 = picprocess.predict_board1(path,'/Users/yuxia/SuDoKu/PyTorch/PytorchModel_AddFonts_space_duplicate.pt')
    pred1 = pred1.reshape(81)
    #print(pred1)
    #print(test_list.iloc[i,1:])
    for j in range(81):
        ans = test_list.iloc[i,j+1]
        #print(ans)
        if pred[j] == ans: correct +=1
        if pred1[j] == ans: correct1 += 1
    accuracy.append([correct,correct1])
#print(test_list.iloc[8,:])

