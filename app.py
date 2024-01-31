import sys,os,time
sys.path.append(os.path.dirname(os.path.abspath("__file__")))
if os.name=="nt":
    sys.path.append(os.path.dirname(os.path.abspath("__file__"))+"\\src")
else:
    sys.path.append(os.path.dirname(os.path.abspath("__file__"))+"/src")

import argparse
from src.model import DataManager

# Example usage:
# --write /data/PROJ_GMJULY2022/Cycler_Data_By_Cell/GMJuly2022_CELL901/GMJuly2022_CELL901REF_setRef_1_P25C_P5P0PSI_20230713_R0.res arbin
# --write /data/PROJ_GMJULY2022/Cycler_Data_By_Cell/GMJuly2022_CELL002/GMJuly2022_CELL002_Test3_1_P0C_5P0PSI_20230505_R0_CH041.csv neware_vdf

# --query GMJuly2022_CELL102_EIS_3d_P25C_5P0PSI_20230717_R0_CA8 Pressure=5P0PSI
# --query GMJuly2022_CELL009_DEAD_1_P0C_15P0PSI_20221124_R0_CH046_20221124224959_37_2_6_2818580182 ProjectName=GMJuly2022

def create_parser():
    parser = argparse.ArgumentParser(description="Data processing tool")
    parser.add_argument('--write', nargs='+', metavar=('FILE_PATH', '[DATA_TYPE]'),
                        help='Write data to the database')
    # recursive write using -r
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Recursively write data from a directory to the database')

    parser.add_argument('--query', nargs='*', metavar=('MEASUREMENT', 'TAGS'),
                        help='Query data from the database')
    return parser

def main():
    data_manager = DataManager()
    parser = create_parser()

    while True:
        print("Enter command(write or query) or 'exit' to quit:")
        cmd_input = input()

        if cmd_input == 'exit':
            break

        try:
            args, _ = parser.parse_known_args(cmd_input.split())
            if args.write:
                file_path = args.write[0]
                data_type = args.write[1] if len(args.write) > 1 else None
                if args.recursive:
                    for root, dirs, files in os.walk(file_path):
                        for file in files:
                            data_manager.write_data(os.path.join(root, file)) 
                            time.sleep(1)           
                else:
                    data_manager.write_data(file_path, data_type)
            elif args.query:
                measurement, tags = None, None
                if args.query and '=' in args.query[0]:
                    tags = args.query[0]
                else:
                    measurement = args.query[0] if args.query else None
                    tags = args.query[1] if len(args.query) > 1 else None
                tags_dict = dict(tag.split('=') for tag in tags.split(',')) if tags else None
                data = data_manager.query_data(measurement=measurement, tags=tags_dict)
                print(data)
            else:
                print("Invalid command")
        except Exception as e:
            print("An error occurred:", e)

if __name__ == "__main__":
    main()
