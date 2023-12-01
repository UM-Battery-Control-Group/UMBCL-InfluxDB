import sys,os
sys.path.append(os.path.dirname(os.path.abspath("__file__")))
if os.name=="nt":
    sys.path.append(os.path.dirname(os.path.abspath("__file__"))+"\\src")
else:
    sys.path.append(os.path.dirname(os.path.abspath("__file__"))+"/src")


from src.model import DataManager

def test_query_data():
    data_manager = DataManager()
    measurement = "GMJuly2022_CELL004_EIS_3d_P25C_25P0PSI_20230324_R0_CH032"
    tags = {"ChannelNumber": "CH032", "Pressure": "25P0PSI"}
    data = data_manager.query_data(tags=tags)
    # data = data_manager.query_data(measurement="GMJuly2022_CELL002_BOL_1_P0C_5P0PSI_20220907_R0_CH041")
    print(data)

if __name__ == "__main__":
    test_query_data()