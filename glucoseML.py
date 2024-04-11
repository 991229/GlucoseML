from sklearn.datasets import load_boston 
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn import metrics
import numpy as np
from math import sqrt
from sklearn.metrics import r2_score


#Linear Regression
from sklearn import linear_model
model_LinearRegression = linear_model.LinearRegression()
model_Ridge = linear_model.Ridge(0.06,)
model_Lasso = linear_model.Lasso(alpha = 0.001)
model_Logistic = linear_model.LogisticRegression()
#Decision Tree Regressor
from sklearn import tree
model_DecisionTreeRegressor = tree.DecisionTreeRegressor() #37.704
#SVM Regressor
from sklearn import svm
model_SVR = svm.SVR() # 31.55242834347166 %
#K Neighbors Regressor
from sklearn import neighbors
model_KNeighborsRegressor = neighbors.KNeighborsRegressor()
#Random Forest Regressor
from sklearn import ensemble
model_RandomForestRegressor = ensemble.RandomForestRegressor(n_estimators=80) #35.40301569369769 %
#Adaboost Regressor
from sklearn import ensemble
model_AdaBoostRegressor = ensemble.AdaBoostRegressor(n_estimators=50)
#Gradient Boosting Random Forest Regressor
from sklearn import ensemble
model_GradientBoostingRegressor = ensemble.GradientBoostingRegressor(n_estimators=200, learning_rate=0.07, loss='huber', min_samples_split=10, alpha=0.8, max_depth=10) #28.277542464643982 % 
# #bagging Regressor
from sklearn.ensemble import BaggingRegressor
model_BaggingRegressor = BaggingRegressor(n_estimators=100, max_features=7) #35.717573183137866 %
#ExtraTree Regressor
from sklearn.tree import ExtraTreeRegressor
model_ExtraTreeRegressor = ExtraTreeRegressor()
#
from sklearn.isotonic import IsotonicRegression
model_IR = IsotonicRegression()
#
from sklearn.preprocessing import PolynomialFeatures

train = pd.read_csv('../glucose/glucose_sunshine_dataset/train.csv')

train.shape #(342, 12)
print(train.shape)
X = train.iloc[:, 1:12]  # data
y = train.iloc[:, 0]   # label

#分割数据集，20%做测试集
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1) #16.544165176312944 %
#模型训练
# model_LinearRegression.fit(X_train, y_train)
# model_Ridge.fit(X_train, y_train)
# model_Lasso.fit(X_train, y_train)
# model_Logistic.fit(X_train, y_train)
# model_AdaBoostRegressor.fit(X_train, y_train)
# model_BaggingRegressor.fit(X_train, y_train)
# model_DecisionTreeRegressor.fit(X_train, y_train)
# model_ExtraTreeRegressor.fit(X_train, y_train)
Model = model_GradientBoostingRegressor.fit(X_train, y_train)
# 9.981682320900736 3.1593800532542358 2.339663437218698 0.8022481188510239
# model_RandomForestRegressor.fit(X_train, y_train)
# model_SVR.fit(X_train, y_train)
# model_KNeighborsRegressor.fit(X_train, y_train)
# #model_IR.fit_transform(X_train, y_train)
"""
poly=PolynomialFeatures(degree=2)
poly_x=poly.fit_transform(X_train)
model_LinearRegression.fit(poly_x, y_train)
"""
#查看截距
#print(regressor.intercept_)
#查看斜率
#coeff_df = pd.DataFrame(Model.coef_, X.columns, columns=['Coefficient'])
#print(coeff_df)

y_pred = Model.predict(X_test)
test_df = pd.DataFrame({'Actual':y_test, 'Predicted':y_pred})

test_df.to_csv("Sunshinepred.csv", index_label="index_label")
#print(test_df)
#print(len(test_df))
#print(y_pred)
#print(y_test)
#print(len(y_test))
#输出结果，第一列是序号，第二列是实际结果，第三列是预测的结果


#使用条形图来表示
test_df1 = test_df.head(50)
test_df1.plot(kind='bar', figsize=(16, 10))
plt.grid(which = 'major', linestyle = '-', linewidth = '0.5', color = 'green')
plt.grid(which = 'minor', linestyle = '-', linewidth = '0.5', color = 'black')
#plt.show()


mse_test = np.sum((y_pred - y_test) ** 2) / len(y_test)
rmse_test = sqrt(mse_test)
mae_test = np.sum(np.absolute(y_pred - y_test)) / len(y_test)
R2_score = r2_score(y_test ,y_pred)
mARD = (np.sum((np.absolute(y_pred - y_test) / y_test) * 100)) / len(y_test)
print(mse_test, rmse_test, mae_test, R2_score, mARD, "%")


import joblib
# joblib.dump(Model, "NIR_Model.pkl")
# print("############################################")
# print("model is saved.")





