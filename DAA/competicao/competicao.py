import math
import sklearn as skl
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
import numpy as np

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from sklearn.linear_model import LinearRegression

from sklearn import metrics
from sklearn.svm import SVC

import seaborn as sns
import matplotlib.pyplot as plt

from sklearn. datasets import make_blobs

from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import xgboost as xgb

from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline

#import f_classif
from sklearn.feature_selection import VarianceThreshold
from sklearn.feature_selection import SelectKBest
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer




df = pd.read_csv("training_data.csv")

test = pd.read_csv("test_data.csv")

# Info about columns and their types
#print(df.info())

# Check unique values on columns
print(df.nunique(axis=0))


# city_name e avg_precipitation só com um valor possível, por isso vamos retirar
df=df.drop(    ['city_name', 'avg_precipitation'], axis=1)
test=test.drop(['city_name', 'avg_precipitation'], axis=1)


# check for missing values
#print(df.isna1().sum())

# Make the values with a ',' NaN

roads = {}

def parse_roads(x,letter = ''):
   if type(x)!=str:
       return 0
   if x==','.strip():
      return 0
   x = x.replace(' ','')
   mylist = list(x.split(','))
   if '' in mylist:
      mylist.remove('')
   if letter == '':
      return len(mylist)
   res = list(map(lambda x: x.strip().startswith(letter),mylist))
   res = res.count(True)
   return 1 if res > 0 else 0

def parse_roads_unique(x):
   if type(x)!=str:
       return 0
   if x==','.strip():
      return 0
   x = x.replace(' ','')
   mylist = x.split(',')
   if '' in mylist:
      mylist.remove('')
   listKeys = list(dict.fromkeys(mylist))
   return len(listKeys)


df  ['affected_roads_N'] =   df["affected_roads"].apply(lambda x :parse_roads(x,'N'))
test['affected_roads_N'] = test["affected_roads"].apply(lambda x :parse_roads(x,'N'))

print(df['affected_roads_N'].value_counts())

df  ['affected_roads_I'] =   df["affected_roads"].apply(lambda x :parse_roads(x,'I'))
test['affected_roads_I'] = test["affected_roads"].apply(lambda x :parse_roads(x,'I'))

print(df['affected_roads_I'].value_counts())

df  ['affected_roads_R'] =   df["affected_roads"].apply(lambda x :parse_roads(x,'R'))
test['affected_roads_R'] = test["affected_roads"].apply(lambda x :parse_roads(x,'R'))

print(df['affected_roads_R'].value_counts())
df  ['affected_roads_E'] =   df["affected_roads"].apply(lambda x :parse_roads(x,'E'))
test['affected_roads_E'] = test["affected_roads"].apply(lambda x :parse_roads(x,'E'))

print(df['affected_roads_E'].value_counts())

df  ['affected_roads'] =   df["affected_roads"].apply(lambda x : parse_roads(x))
test['affected_roads'] = test["affected_roads"].apply(lambda x : parse_roads(x))

print(df['affected_roads'].value_counts())






def parse_delay(x):
    if x == 'UNDEFINED':
       return 0
    elif x== 'MODERATE':
       return 1
    else:
       return 2


df['magnitude_of_delay'] = df['magnitude_of_delay'].apply(parse_delay)
test['magnitude_of_delay'] = test['magnitude_of_delay'].apply(parse_delay)


def parse_rain(x):
    if x == 'Sem Chuva':
       return 0
    elif x== 'chuva fraca':
       return 1
    elif x== 'chuva moderada':
       return 2
    else:
        return 3

        

df['avg_rain'] = df['avg_rain'].apply(parse_rain)
test['avg_rain'] = test['avg_rain'].apply(parse_rain)



def parse_luminosity(x):
    if x == 'DARK':
       return 0
    elif x== 'LOW_LIGHT':
       return 1
    else:   
       return 2

        

df['luminosity'] = df['luminosity'].apply(parse_luminosity)
test['luminosity'] = test['luminosity'].apply(parse_luminosity)


# Check correlations
corr_matrix = df.corr() 
f, ax = plt.subplots(figsize=(12, 16))
sns.heatmap(corr_matrix, vmin=-1, vmax=1, square=True, annot=True);
plt.show()


df['record_date'] = pd.to_datetime(df['record_date'], format = '%Y-%m-%d %H:%', errors='coerce')
test['record_date'] = pd.to_datetime(test['record_date'], format = '%Y-%m-%d %H:%', errors='coerce')

#df['record_date_year'] = df['record_date'].dt.year
df['record_date_month'] = df['record_date'].dt.month
df['record_date_day'] = df['record_date'].dt.day
df['record_date_hour'] = df['record_date'].dt.hour
df['record_date_dayOfWeek'] =  df['record_date'].dt.dayofweek

#df['record_date_minute'] = df['record_date'].dt.minute

#test['record_date_year'] =  test['record_date'].dt.year
test['record_date_month'] = test['record_date'].dt.month
test['record_date_day'] =   test['record_date'].dt.day
test['record_date_hour'] =  test['record_date'].dt.hour
test['record_date_dayOfWeek'] =  test['record_date'].dt.dayofweek
#test['record_date_minute'] =  test['record_date'].dt.minute


df=df.drop(['record_date'], axis=1)
test=test.drop(['record_date'], axis=1)
#print(df.info())


print(df.nunique(axis=0))

print("Duplicated:",df.duplicated().sum())
#print(df.drop_duplicated)

def parse_incidentes(x):
   if x == 'None':
       return 0
   elif x== 'Low':
       return 1
   elif x== 'Medium':
       return 2
   elif x== 'High':
       return 3
   elif x== 'Very_High':
       return 4

def parse_incidentes_reverse(x):
   if x == 0:
         return 'None'
   elif x== 1:
         return 'Low'
   elif x== 2:
         return 'Medium'
   elif x== 3:
         return 'High'
   elif x== 4:
         return 'Very_High'  

df  ['incidents'] = df  ['incidents'].apply(parse_incidentes)
#test['incidents'] = test['incidents'].apply(parse_incidentes)


X = df.drop(['incidents'],axis=1)
y = df['incidents'].to_frame()

X_train,X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=2021)


#clf = DecisionTreeClassifier(random_state=2022)


def randomForest(X,y):
   clf = RandomForestClassifier(n_estimators=300)
   clf.fit(X,y.values.ravel())
   predictions = clf.predict(test)

   #clf.fit(X_train,y_train)

   scores = cross_val_score(clf,X,y.values.ravel(),cv=10)
   print(scores.mean())
   file = open("tentativa.csv","w+")

   file.write("RowId,Incidents\n")

   i = 1
   for num in predictions:
      file.write(str(i) + "," +parse_incidentes_reverse(num) +"\n")
      #file.write(str(i) + "," +predictions[i-1] +"\n")
      i+=1



randomForest(X,y)



#grafico de barras
incidents_count = df['incidents'].value_counts()
sns.set(style="darkgrid")
sns.barplot(incidents_count.index, incidents_count.values, alpha=0.9)
plt.title('Frequency Distribution of Incidents')
plt.ylabel('Number of Occurrences', fontsize = 12)
plt.xlabel('Incidents', fontsize=12)
plt.show()



def kmeans(X,y):
   clf = KMeans(n_clusters=2,random_state=2022)
   X_train,X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=2021)
   clf.fit(X_train,y_train.values.ravel())
   predictions = clf.predict(X_test)
   print(accuracy_score(y_test, predictions)) 
   
#kmeans(X,y)

def vectorMachine(X,y):
   clf = SVC(random_state=2022)
   scores = cross_val_score(clf,X,y.values.ravel(),cv=5)
   print(scores)
   
#vectorMachine(X,y)