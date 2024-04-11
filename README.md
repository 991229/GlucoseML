# GlucoseML
# 		Blood glucose monitor

## Requirements

This is my experiment eviroument
- python3.7.2

[**python库--模型计算**]（sklearn， pandas， matplotlib， numpy， math, tensorflow, csv, statistics, joblib, ）
[**python库--UI界面**] (tkinter, hashlib, time, PIL, threading, sys, ttkbootstrap)

```终端输入，下载库
$ pip install PackName
```


## Usage

### 1. 数据预处理
[**文件夹**]
- glucose_hospital [医院原始数据csv：时间+电压值(一个文件四个波形)，含有高血糖数据，bad中为不易识别的数据，文件名：名字、血糖值、激光光强值]
- glucose_sunshine_dataset [太阳光作为光源的数据，已处理]
- glucose_ultrared_dataset [近红外激光作为光源数据，已处理]
[**文件**]
- [text](glucose_data_delay0_abs.py) [数据处理文件，将波形转换为特征]

### 2. 模型训练评估并保存
[**文件**]
- [text](glucose_ML_NIR.py) [机器学习训练]
- [text](glucose_CNN_regression.py) [简单神经网络训练]

### 3.UI交互界面
[**文件**]
- [text]（NI&tkinter_BGmonitor.py）

UI更新画布
