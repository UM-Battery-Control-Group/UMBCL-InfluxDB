import sys,os
sys.path.append(os.path.dirname(os.path.abspath("__file__")))
if os.name=="nt":
    sys.path.append(os.path.dirname(os.path.abspath("__file__"))+"\\src")
else:
    sys.path.append(os.path.dirname(os.path.abspath("__file__"))+"/src")


from src.model import DataManager

def test_query_data():
    data_manager = DataManager()
    measurement = "GMJuly2022_CELL102_EIS_3d_P25C_5P0PSI_20230717_R0_CA8"
    # measurement = "GMJuly2022_CELL009_DEAD_1_P0C_15P0PSI_20221124_R0_CH046_20221124224959_37_2_6_2818580182"
    tags = {"Pressure": "5P0PSI"}
    # tags = {"ProjectName": "GMJuly2022"}
    data = data_manager.query_data(tags=tags)
    print(data)
    # data = data_manager.query_data(measurement=measurement)
    # print(data[measurement]["_time"])
    # data = data_manager.query_data(measurement="GMJuly2022_CELL002_BOL_1_P0C_5P0PSI_20220907_R0_CH041")
    # print(data["GMJuly2022_CELL002_Test3_1_P0C_5P0PSI_20230505_R0_CH041"]["_time"])

if __name__ == "__main__":
    test_query_data()