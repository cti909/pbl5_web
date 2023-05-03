str ="64,73,113,42,55,85,47,108,138,82,121,92,88,40,150,66,101,115,56,146,94,136,141,57,105,101,100,65,114,99"
data_list = str.split(",")
for i in range(len(data_list)):
    data_list[i] = int(data_list[i])
print(len(data_list),data_list)