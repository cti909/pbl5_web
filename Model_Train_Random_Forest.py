
#Read in the dataset
import pandas as pd
import numpy as np
from hrvanalysis import get_time_domain_features
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

df_train = pd.read_csv("pbl5_demo/Project/hrv_dataset/data/final/train.csv")

df_train['condition'] = df_train['condition'].map({'no stress':0, 'interruption':1, 'time pressure':2})

#Tạo tập dữ liệu các giá trị đặc trưng sử dụng cho mô hình
subCols1=['HR','MEAN_RR','SDRR','RMSSD','pNN50']

#Chia tập dữ liệu thành 2 phần với tập kiểm tra chiếm 20%
(X_train, X_test, y_train, y_test) = train_test_split(df_train[subCols1], df_train['condition'], test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train,y_train)
y_pred = model.predict(X_test)

print(classification_report(y_test,y_pred))


# Lấy dữ liệu cơ sở dữ liệu của WebAPI sau đó trả lại nhãn Stress

#Code ở đây


#Thay thế mỗi dòng data
#Đồng thời trả lại nhãn trở lại Web thì thay thế thế nào.

data= [76, 80, 85, 91, 92, 87, 81, 90, 86, 83, 96, 94, 78, 82, 89, 93, 95, 77, 84, 88, 79, 97, 98, 100, 101, 102, 99, 103, 104, 105]
# Tạo danh sách RR:
new_data=[]

# Duyệt qua các phần tử trong danh sách ban đầu và thêm giá trị RR vào danh sách mới
# HR(bpm) ----> RR(ms)
#   60           1000
#   120          500
#   150          400
for num in data:
    new_data.append(1000*60/num)

time_domain_features = get_time_domain_features(new_data)

print(time_domain_features)

#Trích xuất các giá trị đặc trưng
#1. Mean_RR
mean_rr = time_domain_features['mean_nni']

#2. SDRR: độ lệch chuẩn của toàn bộ giá trị RR.
sdrr = time_domain_features['sdnn']

#3. RMSSD: căn bậc hai của trung bình bình phương khác biệt giữa hai giá trị RR liên tiếp.
rmssd = time_domain_features['rmssd']

#4. pNN50
pnn50 = time_domain_features['pnni_50']

#5. HR(Mean_HR)
hr = time_domain_features['mean_hr']
# Sử dụng mô hình để dự đoán trạng thái stress của dữ liệu mới
prediction = model.predict([[hr, mean_rr, sdrr, rmssd, pnn50]])


if prediction == 0:
    print("Dự đoán trạng thái stress của bộ dữ liệu mới: No Stress ")
if prediction == 1:
    print("Dự đoán trạng thái stress của bộ dữ liệu mới: Interruption ")
if prediction == 2:
    print("Dự đoán trạng thái stress của bộ dữ liệu mới: Time pressure")
print(prediction)
result_predict = -1
for i in range(len(prediction)):
    result_predict = prediction[i]
print(result_predict)