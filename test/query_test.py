import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model import DataManager

def test_query_data():
    data_manager = DataManager()
    measurement = "GMJuly2022_CELL002_BOL_1_P0C_5P0PSI_20220907_R0_CH041"
    tags = {"ChannelNumber": "CH041", "Pressure": "5P0PSI"}
    data = data_manager.query_data(tags=tags)
    # data = data_manager.query_data(measurement="GMJuly2022_CELL002_BOL_1_P0C_5P0PSI_20220907_R0_CH041")
    print(data)

if __name__ == "__main__":
    test_query_data()