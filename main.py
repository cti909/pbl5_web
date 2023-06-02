from flask import Flask, jsonify, render_template, request, session
import mysql.connector
import datetime
import joblib
import pandas as pd
import numpy as np
import warnings
import math
from hrvanalysis import get_time_domain_features
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import matplotlib
import json

matplotlib.use("Agg")
import io
import base64
from datetime import datetime

# ----------------------------- create app, connect database ------------------------
# create app
app = Flask(__name__)
app.secret_key = "secret_key"
app.config["SECRET_KEY"] = "super-secret-key"

# connect database mysql
mydb = mysql.connector.connect(
    host="localhost", user="root", password="", database="pbl5"
)
mycursor = mydb.cursor()
warnings.filterwarnings("ignore")
# ----------------------------- end  ------------------------


# ----------------------------- function ------------------------
# predict array heart rate
def predict(data):
    # new_data = []
    # for num in data:
    #     new_data.append(1000 * 60 / num)
    # time_domain_features = get_time_domain_features(new_data)
    # # Trích xuất các giá trị đặc trưng
    # # 1. Mean_RR
    # mean_rr = time_domain_features["mean_nni"]
    # # 2. SDRR: độ lệch chuẩn của toàn bộ giá trị RR.
    # sdrr = time_domain_features["sdnn"]
    # # 3. RMSSD: căn bậc hai của trung bình bình phương khác biệt giữa hai giá trị RR liên tiếp.
    # rmssd = time_domain_features["rmssd"]
    # # 4. pNN50
    # pnn50 = time_domain_features["pnni_50"]
    # # 5. HR(Mean_HR)
    # hr = time_domain_features["mean_hr"]
    # # Sử dụng mô hình để dự đoán trạng thái stress của dữ liệu mới
    # prediction = model.predict([[hr, mean_rr, sdrr, rmssd, pnn50]])
    
    rr_hr = []
    for hr in data:
        rr_hr.append(60000/hr)

    rr_data = get_time_domain_features(rr_hr)
    med_rr = rr_data['median_nni']
    mean_rr = rr_data['mean_nni']
    hr = rr_data['mean_hr']
    sdrr = rr_data['sdnn']
    rmssd = rr_data['rmssd']
    sdrr_rmssd = sdrr/rmssd
    predict = model.predict([[med_rr, mean_rr, hr, sdrr_rmssd]])
    label_predict = ""
    if predict == 0:
        print("Dự đoán trạng thái stress của bộ dữ liệu mới: Stress")
        label_predict = "Stress"
    if predict == 1:
        print("Dự đoán trạng thái stress của bộ dữ liệu mới: No Stress")
        label_predict = "No Stress"
    return label_predict

# ----------------------------- end ------------------------

import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("key.json")
# chưa config key.json
firebase_admin.initialize_app(cred, {
    # 'databaseURL': 'https://pbl5-6a704-default-rtdb.firebaseio.com/'
    'databaseURL': 'https://vidieukhien-6a66b-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

@app.route("/firebase/show")
def get_data():
    ref = db.reference('location')
    data = ref.get()
    # Xử lý dữ liệu
    return 'Data: {}'.format(data)

# @app.route('/firebase/create')
def update_firebase():
    with open('data.json') as file:
        data = json.load(file)

    date = datetime.now()
    formatted_str = date.strftime("%Y-%m-%dT%H:%M:%S")
    
    new_location = { formatted_str : {  
        "longitude": "108.153862",
        "latitude": "16.07546",
        "status": 1
    }}

    data.update(new_location)

    with open('data.json', 'w') as file:
        json.dump(data, file)

    ref = db.reference('location')
    ref.update(data)

    return formatted_str

# kiem tra trong 5p co stress ko
# @app.route('/check')
def check_stress():
    time_now = datetime.now()
    new_time = time_now - datetime.timedelta(minutes=5)
    time_now = time_now.strftime("%Y-%m-%d %H:%M:%S")
    new_time = new_time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "SELECT * FROM heart_rate WHERE posting_time < '" + time_now + "' and posting_time > '"+ new_time + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    count = 0
    if myresult:
        for ptu in myresult:
            if ptu[2] == "Stress":
                count += 1
    if count >= 3:
        return True
    else:
        return False 

# ----------------------------- show html ------------------------
# show array heart rate
@app.route("/")
def heart_rate():
    return render_template("heart_rate.html")


# location
@app.route("/location", methods=["GET"])
def location():
    sql = "SELECT * FROM location ORDER BY id DESC LIMIT 1;"
    mycursor.execute(sql)
    myresult = mycursor.fetchone()
    longitude = myresult[1]
    latitude = myresult[2]
    posting_time = myresult[3]
    posting_time = posting_time.strftime("%Y-%m-%d %H:%M:%S")
    return render_template("location.html", longitude=longitude, latitude=latitude)


@app.route("/statistic_heart_rate", methods=["GET"])
def statistic_heart_rate():
    record_limit = 50
    page = request.args.get("page")
    date = request.args.get("date")
    date_search = ""
    if date == None:
        date_search = ""
    else:
        date_search = date
    sql = "SELECT * FROM heart_rate WHERE posting_time LIKE '" + date_search + "%'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    datas = myresult[0:record_limit]
    _page_current = 1
    _page_count = math.ceil(len(myresult) / record_limit)

    if page != None:
        _page_current = int(page)
        datas = myresult[
            (_page_current - 1) * record_limit : _page_current * record_limit
        ]

    return render_template(
        "statistic_heart_rate.html",
        datas=datas,
        page_count=_page_count,
        page_current=_page_current,
        date=date_search,
    )


@app.route("/statistic_location", methods=["GET"])
def statistic_location():
    record_limit = 50
    page = request.args.get("page")
    date = request.args.get("date")
    date_search = ""
    if date == None:
        date_search = ""
    else:
        date_search = date
    sql = "SELECT * FROM location WHERE posting_time LIKE '" + date_search + "%'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    datas = myresult[0:record_limit]
    _page_current = 1
    _page_count = math.ceil(len(myresult) / record_limit)

    if page != None:
        _page_current = int(page)
        datas = myresult[
            (_page_current - 1) * record_limit : _page_current * record_limit
        ]

    return render_template(
        "statistic_location.html",
        datas=datas,
        page_count=_page_count,
        page_current=_page_current,
        date=date_search,
    )


@app.route("/statistic_analysis", methods=["GET"])
def statistic_analysis():
    date = request.args.get("date")
    labels = []
    hr_means = []
    times = []
    plt.clf()
    check = True
    if date != None:
        sql = "SELECT * FROM heart_rate WHERE posting_time LIKE '" + date + "%'"
        mycursor.execute(sql)
        result = mycursor.fetchall()
        # print(result[:4])
        if result:
            for line in result:
                _, _, hr_mean, time, label = line
                hr_means.append(hr_mean)
                labels.append(label)
                times.append(time.strftime("%H:%M:%S"))
        else:
            check = False
        print(labels)
        print(hr_means)
        print(times)
    else:
        return render_template("statistic_analysis.html")
    
    if check:
        counts = {}
        for item in labels:
            if item in counts:
                counts[item] += 1
            else:
                counts[item] = 1

        stress_types = list(counts.keys())
        stress_counts = list(counts.values())

        # Vẽ biểu đồ tròn
        plt.pie(
            stress_counts,
            labels=stress_types,
            autopct="%1.2f%%",
            colors=["red", "green", "blue"],
        )

        # Tùy chỉnh định dạng và tiêu đề
        plt.title("Tỉ lệ các loại stress trong ngày")

        # Chuyển đồ thị thành đối tượng hình ảnh dạng base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        labels_img = base64.b64encode(buffer.getvalue()).decode("utf-8")

        plt.clf()
        # Vẽ đồ thị đường
        plt.plot(hr_means)
        plt.xlabel("")
        plt.ylabel("Giá trị Heart Rate")
        plt.title("Biểu đồ Heart Rate Means")
        # Chuyển đồ thị thành đối tượng hình ảnh dạng base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        hr_means_img = base64.b64encode(buffer.getvalue()).decode("utf-8")

        plt.clf()
        time_objects = [datetime.strptime(t, "%H:%M:%S") for t in times]

        # Tạo danh sách khoảng thời gian cho mỗi nhãn liên tục
        time_ranges = []
        current_label = labels[0]
        start_time = time_objects[0]
        for i in range(1, len(labels)):
            if labels[i] != current_label:
                end_time = time_objects[i - 1]
                time_ranges.append((start_time, end_time, current_label))
                current_label = labels[i]
                start_time = time_objects[i]
        # Xử lý cho trường hợp cuối cùng
        end_time = time_objects[-1]
        time_ranges.append((start_time, end_time, current_label))

        # Tạo biểu đồ
        fig, ax = plt.subplots()

        # Vẽ các khoảng thời gian như các đoạn thẳng ngang trên trục x
        for start, end, label in time_ranges:
            ax.hlines(label, start, end)

        # Cấu hình trục x để hiển thị thời gian
        x_ticks = [t.strftime("%H:%M:%S") for t in time_objects]
        ax.set_xticks(time_objects)
        ax.set_xticklabels(x_ticks, rotation=45)

        plt.xlabel("Time")
        plt.ylabel("Labels")
        plt.title("Label Distribution over Time")

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        time_labels_img = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return render_template(
            "statistic_analysis.html",
            date=date,
            labels_img=labels_img,
            hr_means_img=hr_means_img,
            time_labels_img=time_labels_img,
        )
    else:
        return render_template(
            "statistic_analysis.html",
            date=date
        )


# ----------------------------- end ------------------------


# --------------------- get data from database -----------------------
@app.route("/get_heart_rate", methods=["GET"])
def get_heart_rate():
    try:
        # posting_time = "2023-04-13 20:16:39"
        # data= [76, 80, 85, 91, 92, 87, 81, 90, 86, 83, 96, 94, 78, 82, 89, 93, 95, 77, 84, 88, 79, 97, 98, 100, 101, 102, 99, 103, 104, 105]
        mycursor.execute("SELECT * FROM heart_rate ORDER BY id DESC LIMIT 1")
        result = mycursor.fetchone()
        if result is not None:
            id = result[0]
            heart_rate_data = result[1]
            heart_rate_mean = result[2]
            posting_time = result[3]
            result = result[4]
        else:
            id = 0
            heart_rate_data = [0] * 60  # array 0
            heart_rate_mean = 0
            posting_time = "0000-00-00 00:00:00"
            result = "None"

        data = heart_rate_data.split(",")
        for i in range(len(data)):
            data[i] = int(data[i])
        posting_time = posting_time.strftime("%Y-%m-%d %H:%M:%S")

        return jsonify(
            heart_rate_data=data,
            posting_time=posting_time,
            heart_rate_mean=heart_rate_mean,
            result=result,
        )
    except Exception as e:
        print("error:", str(e))


@app.route("/get_location", methods=["GET"])
def get_location():
    try:
        sql = "SELECT * FROM location ORDER BY id DESC LIMIT 1;"
        mycursor.execute(sql)
        myresult_location = mycursor.fetchone()
        longitude = myresult_location[1]
        latitude = myresult_location[2]
        posting_time = myresult_location[3]
        posting_time = posting_time.strftime("%Y-%m-%d %H:%M:%S")
        return jsonify(
            longitude=longitude, latitude=latitude, posting_time=posting_time
        )
    except Exception as e:
        print("error:", str(e))

# ------------------------ end -------------------


# ------------------------ get data from board, save in db -------------------
# get heart rate data
@app.route("/save_heart_rate", methods=["POST"])
def save_heart_rate():
    data = request.form["data"]
    print(data)
    # convert string to list number
    data_list = data.split(",")
    for i in range(len(data_list)):
        data_list[i] = int(data_list[i])
    data_mean = sum(data_list) / len(data_list)
    print(len(data_list))
    posting_time = datetime.now()
    posting_time = posting_time.strftime("%Y-%m-%d %H:%M:%S")
    label_predict = predict(data_list)
    # get last id
    mycursor.execute("SELECT id FROM heart_rate ORDER BY id DESC LIMIT 1")
    result = mycursor.fetchone()
    if result is not None:
        hr_id_last = result[0] + 1
    else:
        hr_id_last = 1
    # save in db
    sql = f"INSERT INTO heart_rate (id, heart_rate_data, heart_rate_mean, posting_time, result) VALUES ({hr_id_last},'{data}',{data_mean},'{posting_time}','{label_predict}');"
    mycursor.execute(sql)
    mydb.commit()
    return str(1)


# get location data and save to database
@app.route("/save_location", methods=["POST"])
def save_location():
    data = request.form["data"]
    print("", data)
    # chuyen chuoi thanh list number
    data_list = data.split(",")
    longitude = data_list[0]
    latitude = data_list[1]
    posting_time = datetime.now()
    print(posting_time)
    posting_time = posting_time.strftime("%Y-%m-%d %H:%M:%S")

    mycursor.execute("SELECT id FROM location ORDER BY id DESC LIMIT 1")
    result = mycursor.fetchone()
    if result is not None:
        location_id_last = result[0] + 1
    else:
        location_id_last = 1
    sql_location = f"INSERT INTO location (id, longitude, latitude, posting_time) VALUES ({location_id_last},{longitude},{latitude},'{posting_time}');"
    mycursor.execute(sql_location)
    mydb.commit()
    return str(1)
# ----------------------------- end ------------------------




if __name__ == "__main__":
    model = joblib.load("model.pkl")  # model is global variable
    # app.run(host="192.168.9.186",port=5000,debug=True)
    app.run(debug=True)
