from statistics import mean
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import csv

train = pd.read_csv('glucose_hospital/谢老师 8.2 0.41.csv')
train = train.iloc[:, 6:8]
#train.drop(['Item'], axis = 1)
#print(train.shape[0])  rows
train.columns = ['Time', 'V']
train['V'] = train['V']*(-1)
#print(train.describe())
systolic_peak = []
systolic_peak_ratio = []
diastolic_peak = []
diastolic_peak_ratio = []
dicrotic_notch= []
dicrotic_notch_ratio = []
bottom = []
cofficient_rise = []
cofficient_decline = []
pulse_width = []
DEIT = []
dicrotic_notch_row = 0
bottom_row = 0
bottom_value = 0
systolic_peak_row = 0
systolic_peak_value = 0
diastolic_peak_row = 0


for i in range(10, train.shape[0]-20):
    # systolic_peak
    if train.iloc[i, 1] > train.iloc[i-10, 1] and train.iloc[i, 1] > train.iloc[i+10, 1] and train.iloc[i, 1] > train.iloc[i+1, 1] and train.iloc[i, 1] > train.iloc[i-1, 1]:
        systolic_peak_row = i
        systolic_peak_value = train.iloc[i, 1]  # 收缩峰 = 峰值 - 底部值   -----------
        if bottom_row != 0 and  0 < (systolic_peak_row - bottom_row) < 15:
            #print("i:", systolic_peak_row, " ", bottom_row-systolic_peak_row, " ", "s_peak_value:", train.iloc[i, 1]-bottom_value, "Peak:", train.iloc[i, 1], "bottom:", bottom_value)
            systolic_peak.append(train.iloc[i, 1] - bottom_value)
            systolic_peak_ratio.append((train.iloc[i, 1] - bottom_value)/bottom_value)
            cofficient_rise.append((systolic_peak_value-bottom_value)/(systolic_peak_row-bottom_row)) # 上升斜率 = (收缩峰 - 最低点)/（收缩峰时间 - 最低点时间）
        #print("sys_row:", systolic_peak_row)
        #print("bottom_row:", bottom_row)
        
    # dicrotic_notc
    if train.iloc[i, 1] < train.iloc[i-6, 1] and train.iloc[i, 1] < train.iloc[i+6, 1] and train.iloc[i, 1] > train.iloc[i+12, 1]:
        if bottom_row != 0 and  10 < (i - bottom_row) < 30:
            dicrotic_notch.append(train.iloc[i, 1] - bottom_value)
            #print("i:", i, " ", bottom_row-i, " ", "d_notc:", train.iloc[i, 1]-bottom_value)
            dicrotic_notch_ratio.append((train.iloc[i, 1] - bottom_value)/bottom_value)
        
    # diastolic_peak
    if train.iloc[i, 1] > train.iloc[i+10, 1] and train.iloc[i, 1] > train.iloc[i-5, 1] and train.iloc[i, 1] < train.iloc[i-12, 1] and train.iloc[i, 1] > train.iloc[i+1, 1] and train.iloc[i, 1] > train.iloc[i-1, 1]:
        if bottom_row != 0 and  15 < (i - bottom_row) < 30:
            diastolic_peak.append(train.iloc[i, 1] - bottom_value)
            diastolic_peak_ratio.append((train.iloc[i, 1] - bottom_value)/bottom_value)
            #print("i:", i, " ", bottom_row-i, " ", "d_peak:", train.iloc[i, 1]-bottom_value)
        diastolic_peak_row = i
        if systolic_peak_row != 0: #and diastolic_peak_row - systolic_peak_row :
            DEIT.append(diastolic_peak_row - systolic_peak_row)  # DEIT = 收缩峰到舒张峰的时长
        
    #bottom
    if train.iloc[i, 1] < train.iloc[i-15, 1] and train.iloc[i, 1] < train.iloc[i+15, 1] and train.iloc[i, 1] < train.iloc[i+1, 1] and train.iloc[i, 1] < train.iloc[i-1, 1] and train.iloc[i, 1] < train.iloc[i+3, 1] and train.iloc[i, 1] < train.iloc[i-3, 1]:
        bottom.append(train.iloc[i, 1])
        #print("i:", i, " ", bottom_row-i, " ", "d_peak:", train.iloc[i, 1])
        if i-bottom_row > 25:
            pulse_width.append((i - bottom_row))  # 脉冲宽度 = 两最低点时长差
        bottom_row = i
        bottom_value = train.iloc[i, 1]
        if systolic_peak_row != 0 and (bottom_row-systolic_peak_row) < 40:
            cofficient_decline.append((bottom_value-systolic_peak_value)/(bottom_row-systolic_peak_row)) # 下降斜率 = （最低点 - 收缩峰）/ （最低点时间 - 收缩峰时间）
    


systolic_peak_value = mean(systolic_peak)
diastolic_peak_value = mean(diastolic_peak)
dicrotic_notch_value = mean(dicrotic_notch)
bottom_value = mean(bottom)
cofficient_decline_value = mean(cofficient_decline)
cofficient_rise_value = mean(cofficient_rise)
pulse_width_value = mean(pulse_width)
DEIT_value = mean(DEIT)
glucose_feature = [systolic_peak_value, (-1)*mean(systolic_peak_ratio), diastolic_peak_value, (-1)*mean(diastolic_peak_ratio), dicrotic_notch_value, (-1)*mean(dicrotic_notch_ratio), (-1)*bottom_value, cofficient_decline_value, cofficient_rise_value, pulse_width_value, DEIT_value]
print(glucose_feature)

# with open(r'./train_hospital.csv',mode='a',newline='',encoding='utf8') as cfa:
#     wf = csv.writer(cfa)
#     data2 = [glucose_feature]
#     for i in data2:
#         wf.writerow(i)

