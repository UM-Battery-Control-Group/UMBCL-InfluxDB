import csv
import datetime
import cellpy
import pandas as pd
from src.utils import setup_logger
from src.config import TZ_INFO, name_config

class DataParser:

    def __init__(self) -> None:
        self.logger = setup_logger()
        self.tz_info = TZ_INFO

    def parse_neware_vdf(self, file_path: str) -> pd.DataFrame:
        try:
            # 读取整个文件的行到一个列表中
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # 查找数据开始的行号
            start_line = 0
            for i, line in enumerate(lines):
                if "[DATA START]" in line:
                    start_line = i + 1
                    break

            # 如果文件没有数据开始的标记
            if start_line == 0:
                self.logger.error(f"No data start marker found in {file_path}")
                return None

            # 处理元数据
            metadata_lines = lines[:start_line - 1]
            vdf_meta = {line.split(':')[0].strip(): line.split(':')[1].strip() for line in metadata_lines if ':' in line}
            measurement_name = file_path.split("/")[-1].split(".")[0]  # Use the file name as the measurement name
            neware_vdf_meta = self._measurement_name_to_metadata(measurement_name, "neware_vdf")
            if neware_vdf_meta is None:
                return None
            vdf_meta.update(neware_vdf_meta)

            # 从数据开始行读取 DataFrame
            neware_vdf_df = pd.read_csv(file_path, delimiter='\t', skiprows=start_line)

            # 更新列名
            neware_vdf_df.columns = [col.replace('\\', '').replace(' ', '_') for col in neware_vdf_df.columns]

            # 添加元数据到 DataFrame
            for key, value in vdf_meta.items():
                neware_vdf_df[key] = value

            return neware_vdf_df

        except Exception as e:
            self.logger.error(f"Failed to parse Neware VDF file {measurement_name}: {e}")
            return None

        
    def parse_arbin(self, file_path: str) -> pd.DataFrame:
        """
        Parse the Arbin file into a pandas dataframe

        Parameters
        ----------
        file_path : str
            The path to the Arbin file

        Returns
        -------
        pandas.DataFrame
            The dataframe containing the data from the Arbin file
        """
        arbin_raw_df, arbin_summary_df, arbin_steps_df = self._read_cellpy(file_path)
        if arbin_raw_df is None:
            self.logger.error(f"The Arbin file {file_path} is empty")
            return None
        
        # Define the meta data and data
        measurement_name = file_path.split("/")[-1].split(".")[0]   # Use the file name as the measurement name
        arbin_meta = self._measurement_name_to_metadata(measurement_name, "arbin")
        if arbin_meta is None:
            return None
        
        self.logger.info(f"Start parsing Arbin file {measurement_name}")
        # Add the meta data to every row of the raw data
        for key, value in arbin_meta.items():
            arbin_raw_df[key] = value

        return arbin_raw_df

    def _measurement_name_to_metadata(self, measurement_name: str, measurement_type: str) -> dict:
        """
        Format the Neware VDF file name: 
            [ProjectName]_[DeviceID]_[TestType]_[ProcedureVersion]_[Temperature]_[Pressure]_[TestDate]_[RunNumber]_[ChannelNumber]

        Parameters
        ----------
        measurement_name : str
            The name of the Neware VDF file
        measurement_type : str
            The type of the measurement, e.g. "arbin", "neware", "neware_vdf", "biologic"

        Returns
        -------
        dict
            The dictionary containing the metadata
        """
        name_keys = []
        if measurement_type.lower() == "arbin":
            name_keys = name_config.ARBIN_NAME_KEYS
        elif measurement_type.lower() == "neware":
            name_keys = name_config.NEWARE_NAME_KEYS
        elif measurement_type.lower() == "neware_vdf":
            name_keys = name_config.NEWARE_VDF_NAME_KEYS
        elif measurement_type.lower() == "biologic":
            name_keys = name_config.BIOLOGIC_NAME_KEYS
        else:
            self.logger.error(f"Unknown measurement type {measurement_type}")
            return None
        
        try:
            # Split the measurement name by "_" 
            metadata = dict(zip(name_keys, measurement_name.split("_")))

            return metadata
        
        except Exception as e:
            self.logger.error(f"Failed to format the Neware VDF file name {measurement_name}: {e}")
            return None

    def _read_cellpy(self, file_path: str) -> tuple:
        """
        Read the cellpy file and return the iterator of rows

        Parameters
        ----------
        file_path : str
            The path to the cellpy file

        Returns
        -------
        raw_data : pandas.DataFrame
            The raw data
        summary_data : pandas.DataFrame
            The summary data
        steps_data : pandas.DataFrame
            The steps data
        """
        try:
            # Use cellpy to read the file and convert it to a list of rows
            cell = cellpy.cellreader.get(file_path, instrument="arbin_res")
            data = cell.data
            raw_data = data.raw
            summary_data = data.summary
            steps_data = data.steps
            self.logger.info(f"Loaded cellpy file from {file_path} successfully")

            return raw_data, summary_data, steps_data

        except Exception as e:
            self.logger.error(f"Failed to load cellpy file from {file_path}: {e}")
            return None
        
    def _timestamp_to_datetime(self, timestamp: float) -> datetime.datetime:
        """
        Convert the timestamp to datetime

        Parameters
        ----------
        timestamp : float
            The timestamp
        
        Returns
        -------
        datetime.datetime
            The datetime
        """
        return datetime.datetime.fromtimestamp(timestamp/1000, tz=self.tz_info)