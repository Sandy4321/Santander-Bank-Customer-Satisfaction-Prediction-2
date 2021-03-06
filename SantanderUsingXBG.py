# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 12:20:46 2016

@author: Bhavanana
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 17:35:57 2016

@author: Lyndon Quadros
"""
import pandas as pd
import Initial_feature_selection as IFS
import numpy as np
import xgboost as xgb

from sklearn.preprocessing import normalize
from sklearn.feature_selection import SelectFromModel
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import ExtraTreesClassifier



 
path = 'C:/Data Science and ML/Kaggle Santander/'
  
df_data = pd.read_csv(path+'train.csv', sep=',', header=0)
X_train, y_train, feat_ix_keep, pca, del_constants, del_identicals = IFS.final_feats(df_data)
   

"""preprocessing of test data using features obtained from preprocessing
of training data"""
test_data =  pd.read_csv(path+'test.csv', sep=',', header=0)
x_test = test_data.iloc[:,1:369]

"""Finding the first 2 PCs"""
x_test_projected = pca.fit_transform(normalize(x_test, axis=0))

"""Removing features with little variance, identical features and those deemed redundant by the 
L-1 regularized SVC"""
x_test = x_test.drop(labels=x_test.columns[del_constants],
                                 axis=1)
x_test = x_test.drop(labels=del_identicals, axis=1)
orig_feat_ix = np.arange(x_test.columns.size)
feat_ix_delete = np.delete(orig_feat_ix, feat_ix_keep)
X_test = x_test.drop(labels=x_test.columns[feat_ix_delete],
                                 axis=1)

"""Inserting the 2 PCs found above"""
X_test.insert(1, 'PCAOne', x_test_projected[:, 0])
X_test.insert(1, 'PCATwo', x_test_projected[:, 1])                                 

#Further feature selection using ExtraTreeClassifier
clf = ExtraTreesClassifier(random_state=1729,bootstrap =True,class_weight = "balanced")
selector = clf.fit(normalize(X_train), y_train)
fs = SelectFromModel(selector, prefit=True)
X_train = fs.transform(X_train)
X_test = fs.transform(X_test)

print(X_train.shape,  X_test.shape)

#building the xgboost claasifier using training model
m2_xgb = xgb.XGBClassifier(missing=np.nan, max_depth=6, 
n_estimators=350, learning_rate=0.025, nthread=4, subsample=0.95,
colsample_bytree=0.85, seed=4242)
metLearn = CalibratedClassifierCV(m2_xgb, method='isotonic', cv=10)
metLearn.fit(X_train,y_train)     

#classifying on Test data
custSat = metLearn.predict_proba(X_test)
#submission
submission = pd.DataFrame({ 'ID': test_data['ID'],
                            'TARGET': custSat })
submission.to_csv("Lyndon_Quadros_Submission.csv", index=False)                                          