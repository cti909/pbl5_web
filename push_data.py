import time
import random
import datetime
import requests
import json

def random_data():
    while True:
        frame_length = 30
        list_data_string = ""
        for i in range(frame_length):
            hr_test = random.randint(40, 150)
            if i != frame_length-1:
                list_data_string += str(hr_test) + ","
            else:
                list_data_string += str(hr_test)
            print(i, hr_test)
        print(list_data_string)

        data_list = list_data_string.split(",")
        for i in range(len(data_list)):
            data_list[i] = int(data_list[i])
        print(len(data_list), data_list)

        time_start = datetime.datetime.now()
        time_end = time_start + datetime.timedelta(seconds=30)
        time_start = time_start.strftime("%Y-%m-%d %H:%M:%S")
        time_end = time_end.strftime("%Y-%m-%d %H:%M:%S")

        data = {
            "data": list_data_string,
            "time_start": time_start,
            "time_end": time_end
        }
        # url = url_for('get_api', data=data_string )
        # url = "http://localhost:5000/save_data"

        url = "http://192.168.212.186:5000/save_data"
        response = requests.post(url, data=data)
        
        # response = requests.get(url)
        # print(response.text)
        time.sleep(10)
        
random_data()