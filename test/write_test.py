import sys,os

sys.path.append(os.path.dirname(os.path.abspath("__file__")))
if os.name=="nt":
    sys.path.append(os.path.dirname(os.path.abspath("__file__"))+"\\src")
else:
    sys.path.append(os.path.dirname(os.path.abspath("__file__"))+"/src")

from src.model import DataManager

def test_write_neware_vdf_data():
    data_manager = DataManager()

    arbin_file_path = "/home/me-bcl/Lab_Share_Volt/PROJ_GMJULY2022/Cycler_Data_By_Cell/GMJuly2022_CELL901/GMJuly2022_CELL901REF_setRef_1_P25C_P5P0PSI_20230713_R0.res"
    data_manager.write_data(arbin_file_path, "arbin")

    neware_vdf_file_path = "/home/me-bcl/Lab_Share_Volt/PROJ_GMJULY2022/Cycler_Data_By_Cell/GMJuly2022_CELL002/GMJuly2022_CELL002_Test3_1_P0C_5P0PSI_20230505_R0_CH041.csv"
    data_manager.write_data(neware_vdf_file_path, "neware_vdf")

    biologic_file_path = "/home/me-bcl/Lab_Share_Volt/Raw Cycler Data/Biologic/GMJuy2022/GMJuly2022_CELL102_EIS_3d_P25C_5P0PSI_20230717_R0_CA8.mpr"
    data_manager.write_data(biologic_file_path, "biologic")

    neware_file_path = '/home/me-bcl/Lab_Share_Volt/PROJ_GMJULY2022/Cycler_Data_By_Cell/GMJuly2022_CELL009/GMJuly2022_CELL009_DEAD_1_P0C_15P0PSI_20221124_R0_CH046_20221124224959_37_2_6_2818580182.xlsx'
    data_manager.write_data(neware_file_path, "neware")
    

if __name__ == "__main__":
    test_write_neware_vdf_data()