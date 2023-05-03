from flask import Flask, jsonify, render_template, request, session
import mysql.connector
import datetime
import joblib
import pandas as pd
import numpy as np
import math
from hrvanalysis import get_time_domain_features
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SECRET_KEY'] = 'super-secret-key'

# ket noi csdl mysql bang python
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="pbl5"
)
mycursor = mydb.cursor()

# -----------------

def predict(data):
    # model = joblib.load('RandomForestClassifier.joblib')
    # data= [76, 80, 85, 91, 92, 87, 81, 90, 86, 83, 96, 94, 78, 82, 89, 93, 95, 77, 84, 88, 79, 97, 98, 100, 101, 102, 99, 103, 104, 105]
    new_data=[]
    for num in data:
        new_data.append(1000*60/num)
    time_domain_features = get_time_domain_features(new_data)
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
    label_predict = ""
    if prediction == 0:
        print("Dự đoán trạng thái stress của bộ dữ liệu mới: No Stress ")
        label_predict = "No Stress"
    if prediction == 1:
        print("Dự đoán trạng thái stress của bộ dữ liệu mới: Interruption ")
        label_predict = "Interruption"
    if prediction == 2:
        print("Dự đoán trạng thái stress của bộ dữ liệu mới: Time pressure")
        label_predict = "Time pressure"
    return label_predict

@app.route('/')
def show_chart():
    return render_template('show_chart.html')

@app.route('/statistic_hr', methods=['GET'])
def statistic_hr():
    record_limit = 20
    page = request.args.get('page')
    sort_field = request.args.get('sort_field')
    sort_name = request.args.get('sort_name')
    # search = request.args.get('search')

    sql = "SELECT * FROM hr ORDER BY time_start ASC"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    datas = myresult[0:record_limit]
    _page_current = 1
    _sort_field = "time"
    _sort_name = "asc"
    # _search = ""
    _page_count = math.ceil(len(myresult)/record_limit)

    if page != None:
        _page_current = int(page)
        _sort_field = sort_field
        _sort_name = sort_name
        # _search = search
        sql = "SELECT * FROM hr ORDER BY "+sort_field+" "+sort_name
        print(sql)
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        datas = myresult[(_page_current-1)*record_limit : _page_current*record_limit]
        
    return render_template("statistic_hr.html",
                           datas = datas,
                           page_count = _page_count,
                           page_current = _page_current,
                           sort_field = _sort_field,
                           sort_name = _sort_name
                           )

@app.route('/statistic_predict', methods=['GET'])
def statistic_predict():
    sql = "SELECT * FROM predict"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return render_template("statistic_predict.html", datas=myresult)

@app.route('/statistic_analysis', methods=['GET'])
def statistic_analysis():
    sql = "SELECT * FROM predict"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return render_template("statistic_analysis.html", datas=myresult)

# lay du lieu tu database
@app.route('/predict_data', methods=['GET'])
def predict_data():
    # time_start = "2023-04-13 20:16:39"
    # time_end = "2023-04-13 20:16:40"
    # data= [76, 80, 85, 91, 92, 87, 81, 90, 86, 83, 96, 94, 78, 82, 89, 93, 95, 77, 84, 88, 79, 97, 98, 100, 101, 102, 99, 103, 104, 105]
    mycursor.execute("SELECT * FROM predict ORDER BY id DESC LIMIT 1")
    result_predict = mycursor.fetchone()
    label_predict = result_predict[1]
    hr_id =result_predict[3]

    mycursor.execute("SELECT * FROM hr WHERE id = "+str(hr_id))
    result_hr = mycursor.fetchone()
    data_string = result_hr[1]

    data = data_string.split(",")
    print(data)
    print(len(data_string.split(",")))
    for i in range(len(data)):
        data[i] = int(data[i])
        print(data[i])
    print(data)

    time_start = result_hr[3]
    time_start = time_start.strftime("%Y-%m-%d %H:%M:%S")
    time_end = result_hr[4]
    time_end = time_end.strftime("%Y-%m-%d %H:%M:%S")
    
    # if 'id_last' in session:
    #     session['id_last'] = 0
    # else:
    #     session['id_last'] = hr_id
    
    return jsonify(time_start=time_start, 
                   time_end=time_end, 
                   label_predict=label_predict,
                   data=data)

@app.route('/save_data', methods=['POST'])
def get_data():
    data = request.form['data']
    # chua post duoc thoi gian do esp qua tai
    # time_start = request.form['time_start']
    # time_end = request.form['time_end']
    print(data)

    #chuyen chuoi thanh list number 
    data_list = data.split(",")
    for i in range(len(data_list)):
        data_list[i] = int(data_list[i])
    data_mean = sum(data_list) / len(data_list)

    time_end = datetime.datetime.now()
    time_start = time_end - datetime.timedelta(seconds=30)
    time_end = time_end.strftime("%Y-%m-%d %H:%M:%S")
    time_start = time_start.strftime("%Y-%m-%d %H:%M:%S")

    sql_hr = f"INSERT INTO hr (hr_values, hr_mean, time_start, time_end) VALUES ('{data}',{data_mean},'{time_start}','{time_end}');"
    mycursor.execute(sql_hr)
    mydb.commit()

    mycursor.execute("SELECT id FROM hr ORDER BY id DESC LIMIT 1")
    result = mycursor.fetchone()
    hr_id_last = result[0]
    posting_time = datetime.datetime.now()
    posting_time = posting_time.strftime("%Y-%m-%d %H:%M:%S")
    label_predict = predict(data_list)

    sql_predict = f"INSERT INTO predict (result, posting_time, hr_id) VALUES ('{label_predict}','{posting_time}',{hr_id_last});"
    mycursor.execute(sql_predict)
    mydb.commit()

    return jsonify(data_list = data_list)


# @app.route('/HR/<string:value>', methods=['GET'])
# def get_api(value):
#     hr_value = float(value)
#     date_string = str(datetime.datetime.now())
#     posting_time = datetime.datetime.strptime(date_string.split(".")[0], '%Y-%m-%d %H:%M:%S')


#     sql = "SELECT id FROM hr ORDER BY id DESC LIMIT 1"
#     mycursor.execute(sql)
#     myresult = mycursor.fetchone()
#     if myresult == None:
#         id = 0
#     else:
#         id = myresult[0] + 1
#     sql = f"INSERT INTO hr (id, hr_value, posting_time) VALUES ({id}, {hr_value},'{posting_time}');"
#     mycursor.execute(sql)
#     mydb.commit()
    
#     # neu > 300 record thi xoa het de lam lai
#     if id > 30:
#         sql = "DELETE FROM hr"
#         mycursor.execute(sql)
#         mydb.commit()

#     return jsonify(value = hr_value, posting_time= posting_time)

if __name__ == "__main__":
    model = joblib.load('RandomForestClassifier.joblib')
    # app.run(host="192.168.212.186",port=5000,debug=True)
    app.run(debug=True)
    
