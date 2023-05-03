import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

df_train = pd.read_csv("pbl5_demo/Project/hrv_dataset/data/final/train.csv")
df_train['condition'] = df_train['condition'].map({'no stress':0, 'interruption':1, 'time pressure':2})

#Tạo tập dữ liệu các giá trị đặc trưng sử dụng cho mô hình
subCols1=['HR','MEAN_RR','SDRR','RMSSD','pNN50']

(X_train, X_test, y_train, y_test) = train_test_split(df_train[subCols1], df_train['condition'], test_size=0.2)
model = RandomForestClassifier()
model.fit(X_train,y_train)
joblib.dump(model, 'RandomForestClassifier.joblib')