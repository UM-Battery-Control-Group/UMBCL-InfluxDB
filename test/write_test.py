import sys,os
sys.path.append(os.path.dirname(os.path.abspath("__file__")))
if os.name=="nt":
    sys.path.append(os.path.dirname(os.path.abspath("__file__"))+"\\src")
else:
    sys.path.append(os.path.dirname(os.path.abspath("__file__"))+"/src")

from src.model import DataManager

def test_write_neware_vdf_data():
    data_manager = DataManager()
    # file_path = "/Users/yiliu/Documents/GitHub/UMBCL_InfluxDB/GMJuly2022_CELL004_EIS_3d_P25C_25P0PSI_20230324_R0_CH032.csv"
    # data_manager.write_neware_vdf_data(file_path)
    arbin_file_path = "/home/me-bcl/Lab_Share_Volt/PROJ_GMJULY2022/Cycler_Data_By_Cell/GMJuly2022_CELL901/GMJuly2022_CELL901REF_setRef_1_P25C_P5P0PSI_20230713_R0.res"
    arbin_data = data_manager.data_parser.parse_arbin(arbin_file_path)
    print(arbin_data.columns)
    
    neware_vdf_file_path = "/home/me-bcl/Lab_Share_Volt/PROJ_GMJULY2022/Cycler_Data_By_Cell/GMJuly2022_CELL002/GMJuly2022_CELL002_Test3_1_P0C_5P0PSI_20230505_R0_CH041.csv"
    neware_vdf_data = data_manager.data_parser.parse_neware_vdf(neware_vdf_file_path)
    print(neware_vdf_data.columns)

if __name__ == "__main__":
    test_write_neware_vdf_data()