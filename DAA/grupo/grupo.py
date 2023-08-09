import math
import sklearn as skl
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
import numpy as np

from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from matplotlib.ticker import StrMethodFormatter


from sklearn.linear_model import LinearRegression

from sklearn import metrics
from sklearn.svm import SVC

import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder

from xgboost import XGBClassifier
import xgboost as xgb
from sklearn.model_selection import KFold




df = pd.read_csv('music_genre.csv')


# Check for missing values
print(df.isna().sum())

df = df.dropna(axis=0)



def correlation(df):
    corr_matrix = df.corr() 
    f, ax = plt.subplots(figsize=(12, 16))
    sns.heatmap(corr_matrix, vmin=-1, vmax=1, square=True, annot=True)
    plt.show()



correlation(df)

# check for duplicates
print("Duplicated:" + str(df.duplicated().sum()))


# length of track name 
df['track_name_length'] = df['track_name'].apply(lambda x: len(x))

# check if remix in track name
#df['isRemix'] = df['track_name'].apply(lambda x: 1 if 'remix' in x.lower() else 0)
#print(df['isRemix'].value_counts())


df = df.drop(['instance_id','obtained_date','artist_name','track_name'],axis=1)


print(df['music_genre'].value_counts())

#Join genre Rap and Hip-Hop
df['music_genre'] = df['music_genre'].apply(lambda x : 'Rap' if x == 'Hip-Hop' else x)
df['music_genre'] = df['music_genre'].apply(lambda x : 'Jazz/Blues' if x == 'Jazz' or x== 'Blues' else x)

df = df[df.music_genre != 'Alternative']





lb_make = LabelEncoder()

# handle missing values on tempo
df['tempo'] = df['tempo'].apply(lambda x : 0 if x == '?' else float(x))
mean = df['tempo'].mean()
df['tempo'] = df['tempo'].apply(lambda x : mean if x == 0 else float(x))

#Label encoding mode
df['mode'] = df['mode'].apply(lambda x : 1 if x == 'Major' else 0)



# handle missing values on duration
mean = df['duration_ms'].mean()
df['duration_ms'] = df['duration_ms'].apply(lambda x : mean if x == -1 else x)


#print(df.isna().sum())

df['key'] = lb_make.fit_transform(df['key'])



df = df.drop(['energy'], axis=1)



print(df.info())


x = df.drop(['music_genre'], axis=1)
y = df['music_genre'].to_frame()



correlation(df)


def decisionTree(x,y):
    clf = DecisionTreeClassifier(random_state=2022)

    scores = cross_val_score(clf,x,y,cv=10)
    print(scores.mean())
    print(scores)

    X_train,X_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=2021)
    clf.fit(X_train,y_train)

    predictions = clf.predict(X_test)
    print(accuracy_score(y_test, predictions))





def randomForest(x,y):
    clf = RandomForestClassifier(random_state=2022, n_estimators=100)


    predictions = cross_val_predict(clf,x,y.values.ravel(),cv=5)
    print(accuracy_score(y, predictions))
    #precision = recall_score(y, predictions, average=None)
    precision = precision_score(y, predictions, average=None)
    print(precision)
    sns.set(style="darkgrid")
    ax = sns.barplot(y=precision, x=sorted(y['music_genre'].unique()))
    plt.show()
    conf = confusion_matrix(y, predictions)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.matshow(conf, cmap=plt.cm.Oranges, alpha=0.3)
    genre = sorted(y['music_genre'].unique())
    for i in range(conf.shape[0]):
        for j in range(conf.shape[1]):
            ax.text(x=j, y=i,s=conf[i, j], va='center', ha='center', size='xx-large')
    plt.xlabel('Predictions', fontsize=18)
    plt.ylabel('Actuals', fontsize=18)
    plt.xticks(range(len(genre)), genre, rotation=90, fontsize=14)
    plt.yticks(range(len(genre)), genre, fontsize=14)
    plt.title('Confusion Matrix', fontsize=18)
    plt.show()


def vectorMachine(x,y):
    clf = SVC(random_state=2022)


    X_train,X_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=2021)
    clf.fit(X_train,y_train.values.ravel())
    predictions = clf.predict(X_test)
    print(accuracy_score(y_test, predictions))

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


def logisticRegression(x,y):
    clf = LogisticRegression(random_state=2022,solver='liblinear',max_iter=1000)
    scores = cross_val_score(clf,x,y.values.ravel(),cv=10)

    print(scores.mean())
    


# Y tem de ser inteiros
def xgboost(x,y):
    clf = XGBClassifier(random_state = 2022)
    scores = cross_val_score(clf,x,y.values.ravel(),cv=4)
    print(scores.mean())
    #clf.fit(x,y)




randomForest(x,y)



plt.hist('popularity', 9, facecolor='blue', alpha=0.5)
plt.show()


plt.show()



music_genre_count = df['music_genre'].value_counts()
sns.set(style="darkgrid")
sns.barplot(music_genre_count.index, music_genre_count.values, alpha=0.9)
plt.title('Frequency Distribution of Music Genre')
plt.ylabel('Number of Occurrences', fontsize = 12)
plt.xlabel('Music Genre', fontsize=12)
plt.show()






