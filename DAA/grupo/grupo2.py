import math
import sklearn as skl
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
import numpy as np

from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score


from sklearn.linear_model import LinearRegression

from sklearn import metrics
from sklearn.svm import SVC

import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder



dfMath = pd.read_csv("Maths.csv")

dfPort = pd.read_csv("Portuguese.csv")


#dfPort['Portuguese']=1
#dfMath['Portuguese']='0'


#df = pd.concat([dfPort, dfMath])
df = dfMath

#df.to_csv("all.csv",index=False)

#df = pd.read_csv("all.csv")
#print(df.info())

corr_matrix = df.corr() 
f, ax = plt.subplots(figsize=(12, 16))
sns.heatmap(corr_matrix, vmin=-1, vmax=1, square=True, annot=True)
plt.show()

""""
 0   school      1044 non-null   object
 1   sex         1044 non-null   object
 2   age         1044 non-null   int64 
 3   address     1044 non-null   object
 4   famsize     1044 non-null   object
 5   Pstatus     1044 non-null   object
 6   Medu        1044 non-null   int64 
 7   Fedu        1044 non-null   int64 
 8   Mjob        1044 non-null   object
 9   Fjob        1044 non-null   object
 10  reason      1044 non-null   object
 11  guardian    1044 non-null   object
 12  traveltime  1044 non-null   int64 
 13  studytime   1044 non-null   int64 
 14  failures    1044 non-null   int64 
 15  schoolsup   1044 non-null   object
 16  famsup      1044 non-null   object
 17  paid        1044 non-null   object
 18  activities  1044 non-null   object
 19  nursery     1044 non-null   object
 20  higher      1044 non-null   object
 21  internet    1044 non-null   object
 22  romantic    1044 non-null   object
 23  famrel      1044 non-null   int64 
 24  freetime    1044 non-null   int64 
 25  goout       1044 non-null   int64 
 26  Dalc        1044 non-null   int64 
 27  Walc        1044 non-null   int64 
 28  health      1044 non-null   int64 
 29  absences    1044 non-null   int64 
 30  G1          1044 non-null   int64 
 31  G2          1044 non-null   int64 
 32  G3          1044 non-null   int64 
 33  subject     1044 non-null   object
"""



#print(df.nunique(axis=0))
#print(df['Mjob'].value_counts())
lb_make = LabelEncoder()
#df_skl = pd.read_csv("all.csv")

#print(df['Mjob_code'].value_counts())
#print(df_skl.info())

def parseBin(x):
    if x == 'yes':
        return 1
    else:
        return 0



df['schoolsup'] = df['schoolsup'].apply(parseBin)
df['famsup'] = df['famsup'].apply(parseBin)
df['paid'] = df['paid'].apply(parseBin)
df['activities'] = df['activities'].apply(parseBin)
df['nursery'] = df['nursery'].apply(parseBin)
df['higher'] = df['higher'].apply(parseBin)
df['romantic'] = df['romantic'].apply(parseBin)
df['internet'] = df['internet'].apply(parseBin)
df['sex'] = df['sex'].apply(lambda x : 0 if x=='F' else 1)
df['address'] = df['address'].apply(lambda x : 0 if x=='U' else 1)
df['famsize'] = df['famsize'].apply(lambda x : 0 if x=='LE3' else 1)
df['Pstatus'] = df['Pstatus'].apply(lambda x : 0 if x=='A' else 1)
df['school'] = df['school'].apply(lambda x : 0 if x=='GP' else 1)

df['Mjob_code'] = lb_make.fit_transform(df['Mjob'])
df['Fjob_code'] = lb_make.fit_transform(df['Fjob'])
df['reason_code'] = lb_make.fit_transform(df['reason'])
df['guardian_code'] = lb_make.fit_transform(df['guardian'])

df = df.drop(['Fjob','reason','guardian','Mjob'],axis=1)


#print(df.isna().sum())
# print(df.dtypes)
#print(df['Fjob'].value_counts())
#print(df['reason'].value_counts())
#print(df['guardian'].value_counts())



print(df['G3'].value_counts())

#df['G3'] = df['G3'].apply(lambda x : str(x))
#print(df.info())

x = df.drop(['G1', 'G2', 'G3'], axis=1)
y = df['G3'].to_frame()




#clf.fit(x,y)

clf = DecisionTreeRegressor(random_state=2022)

#scores = cross_val_score(clf,x,y,cv=10)
scores = cross_val_score(clf, x, y, scoring='neg_mean_squared_error', cv=10)

print( np.sqrt(np.abs(scores.mean())))

X_train,X_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=2021)

clf.fit(X_train,y_train)


#print(scores.mean())

predictions = clf.predict(X_test)

file = open("tentativa.csv","w+")



print('MAE:', mean_absolute_error(y_test, predictions))
print('MSE:', mean_squared_error(y_test, predictions))
print('RMSE:', np.sqrt(mean_squared_error(y_test, predictions)))