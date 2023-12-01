import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model import DataManager

def test_write_neware_vdf_data():
    data_manager = DataManager()
    file_path = "/Users/yiliu/Documents/GitHub/UMBCL_InfluxDB/GMJuly2022_CELL004_EIS_3d_P25C_25P0PSI_20230324_R0_CH032.csv"
    data_manager.write_neware_vdf_data(file_path)

if __name__ == "__main__":
    test_write_neware_vdf_data()