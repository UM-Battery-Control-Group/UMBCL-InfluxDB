import csv
import datetime
import cellpy
from galvani import BioLogic
import pandas as pd
from src.utils import setup_logger
from src.config import TZ_INFO, name_config, field_config

class DataParser:

    def __init__(self) -> None:
        self.logger = setup_logger()
        self.tz_info = TZ_INFO

    def parse_neware_vdf(self, file_path: str) -> pd.DataFrame:
        """
        Parse the Neware VDF file into a pandas dataframe

        Parameters
        ----------
        file_path : str
            The path to the Neware VDF file

        Returns
        -------
        pandas.DataFrame
            The dataframe containing the data from the Neware VDF file
        """
        try:
            # Try to read the file
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # Try to find the line where the data starts
            start_line = 0
            for i, line in enumerate(lines):
                if "[DATA START]" in line:
                    start_line = i + 1
                    break

            # If the data start line is not found, return None
            if start_line == 0:
                self.logger.error(f"No data start marker found in {file_path}")
                return None

            # Parse the metadata
            metadata_lines = lines[:start_line - 1]
            vdf_meta = {line.split(':')[0].strip(): line.split(':')[1].strip() for line in metadata_lines if ':' in line}
            measurement_name = file_path.split("/")[-1].split(".")[0]  # Use the file name as the measurement name
            neware_vdf_meta = self._measurement_name_to_metadata(measurement_name, "neware_vdf")
            if neware_vdf_meta is None:
                return None
            vdf_meta.update(neware_vdf_meta)

            # Read the DataFrame
            df = pd.read_csv(file_path, delimiter='\t', skiprows=start_line, nrows=1)
            header = df.columns
            units = df.iloc[0]
            new_header = [f'{h} ({u})' for h, u in zip(header, units)]

            neware_vdf_df = pd.read_csv(file_path, delimiter='\t', skiprows=start_line + 2, header=None, names=new_header)

            # Read the DataFrame again with the new header
            neware_vdf_df = pd.read_csv(file_path, delimiter='\t', skiprows=start_line + 2, header=None, names=new_header)

            self._add_meta_data(neware_vdf_df, vdf_meta)
            self._rename_columns(neware_vdf_df, "neware_vdf")
            neware_vdf_df["Timestamp(epoch)"] = neware_vdf_df["Timestamp(epoch)"].apply(self._timestamp_to_datetime)

            return neware_vdf_df

        except Exception as e:
            self.logger.error(f"Failed to parse Neware VDF file {measurement_name}: {e}")
            return None

    def parse_biologic(self, file_path: str) -> pd.DataFrame:
        """
        Parse the Biologic file into a pandas dataframe

        Parameters
        ----------
        file_path : str
            The path to the Biologic file

        Returns
        -------
        pandas.DataFrame
            The dataframe containing the data from the Biologic file
        """
        try:
            self.logger.info(f"Start parsing Biologic file {file_path}")
            df, start_time = self._read_mpr(file_path)
            if df is None:
                return None
            
            measurement_name = file_path.split("/")[-1].split(".")[0]   # Use the file name as the measurement name
            biologic_meta = self._measurement_name_to_metadata(measurement_name, "biologic")
            if biologic_meta is None:
                return None
            
            self._add_meta_data(df, biologic_meta)
            self._rename_columns(df, "biologic")
            # Add the timestamp column
            total_time = pd.to_timedelta(df['Total Time'])
            df["Timestamp(epoch)"] = start_time + total_time

            return df
        
        except Exception as e:
            self.logger.error(f"Failed to parse Biologic file {file_path}: {e}")
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
        try:
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

            self._add_meta_data(arbin_raw_df, arbin_meta)
            self._rename_columns(arbin_raw_df, "arbin")

            return arbin_raw_df
        
        except Exception as e:
            self.logger.error(f"Failed to parse Arbin file {file_path}: {e}")
            return None
        
    def parse_neware(self, file_path: str) -> pd.DataFrame:
        """
        Parse the Neware file into a pandas dataframe

        Parameters
        ----------
        file_path : str
            The path to the Neware file

        Returns
        -------
        pandas.DataFrame
            The dataframe containing the data from the Neware file
        """
        try:
            self.logger.info(f"Start parsing Neware file {file_path}")
            neware_df = self._read_xlsx(file_path)
            if neware_df is None:
                return None

            # Add the timestamp for the neware data
            neware_df['Date'] = pd.to_datetime(neware_df['Date'])
            total_time = pd.to_timedelta(neware_df['Total Time'])
            neware_df['Timestamp(epoch)'] = neware_df['Date'][0] + total_time

            measurement_name = file_path.split("/")[-1].split(".")[0]   # Use the file name as the measurement name
            neware_meta = self._measurement_name_to_metadata(measurement_name, "neware")
            if neware_meta is None:
                return None
            
            self._add_meta_data(neware_df, neware_meta)
            self._rename_columns(neware_df, "neware")

            return neware_df
        
        except Exception as e:
            self.logger.error(f"Failed to parse Neware file {file_path}: {e}")
            return None
    
    def _add_meta_data(self, df: pd.DataFrame, meta: dict) -> pd.DataFrame:
        """
        Add the meta data to the dataframe

        Parameters
        ----------
        df : pandas.DataFrame
            The dataframe
        meta : dict
            The dictionary containing the meta data

        Returns
        -------
        pandas.DataFrame
            The dataframe with meta data
        """
        for key, value in meta.items():
            df[key] = value
        return df
    
    def _rename_columns(self, df: pd.DataFrame, measurement_type: str) -> pd.DataFrame:
        """
        Rename the columns based on the field config

        Parameters
        ----------
        df : pandas.DataFrame
            The dataframe
        type : str
            The type of the measurement, e.g. "arbin", "neware", "neware_vdf", "biologic"

        Returns
        -------
        pandas.DataFrame
            The dataframe with renamed columns
        """
        rename_dict = {}
        if measurement_type.lower() == "arbin":
            rename_dict = {arbin: stored for stored, arbin in zip(field_config.STORED_FIELD_NAMES, field_config.ARBIN_FIELD_NAMES) if arbin is not ""}
        elif measurement_type.lower() == "neware":
            rename_dict = {neware: stored for stored, neware in zip(field_config.STORED_FIELD_NAMES, field_config.NEWARE_FIELD_NAMES) if neware is not ""}
        elif measurement_type.lower() == "neware_vdf":
            rename_dict = {vdf: stored for stored, vdf in zip(field_config.STORED_FIELD_NAMES, field_config.NEWARE_VDF_FIELD_NAMES) if vdf is not ""}
        elif measurement_type.lower() == "biologic":
            rename_dict = {bio: stored for stored, bio in zip(field_config.STORED_FIELD_NAMES, field_config.BIOLOGIC_FIELD_NAMES) if bio is not ""}
        else:
            self.logger.error(f"Unknown measurement type {measurement_type}")
            return None
        
        try:
            df.rename(columns=rename_dict, inplace=True)
            return df

        except Exception as e:
            self.logger.error(f"Failed to rename columns: {e}")
            return None

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
            metadata = {"Cycler": "Arbin"}
            name_keys = name_config.ARBIN_NAME_KEYS
        elif measurement_type.lower() == "neware":
            metadata = {"Cycler": "Neware"}
            name_keys = name_config.NEWARE_NAME_KEYS
        elif measurement_type.lower() == "neware_vdf":
            metadata = {"Cycler": "VDF"}
            name_keys = name_config.NEWARE_VDF_NAME_KEYS
        elif measurement_type.lower() == "biologic":
            metadata = {"Cycler": "Biologic"}
            name_keys = name_config.BIOLOGIC_NAME_KEYS
        else:
            self.logger.error(f"Unknown measurement type {measurement_type}")
            return None
        
        try:
            # Split the measurement name by "_" and zip it with the name keys 
            metadata.update(dict(zip(name_keys, measurement_name.split("_"))))

            return metadata
        
        except Exception as e:
            self.logger.error(f"Failed to format the Neware VDF file name {measurement_name}: {e}")
            return None
        
    def _read_xlsx(self, file_path: str):
        """
        Read the xlsx file, get the 'record' sheet and return the dataframe

        Parameters
        ----------
        file_path : str
            The path to the xlsx file

        Returns
        -------
        raw_data : pandas.DataFrame
            The raw data
        """
        try:
            # Read the xlsx file
            xlsx = pd.ExcelFile(file_path)
            # Get the 'record' sheet
            raw_data = pd.read_excel(xlsx, sheet_name="record")
            self.logger.info(f"Loaded xlsx file from {file_path} successfully")
            
            return raw_data

        except Exception as e:
            self.logger.error(f"Failed to load xlsx file from {file_path}: {e}")
            return None

    def _read_mpr(self, file_path: str):
        """
        Read the mpr file of Biologic, get the data and return the dataframe

        Parameters
        ----------
        file_path : str
            The path to the mpr file

        Returns
        -------
        df : pandas.DataFrame
            The dataframe
        start_timestamp : datetime.datetime
            The start timestamp
        """
        try:
            # Read the mpr file
            mpr_file = BioLogic.MPRfile(file_path)
            # Get the start time
            start_time = mpr_file.timestamp
            df = pd.DataFrame(mpr_file.data)
            self.logger.info(f"Loaded mpr file from {file_path} successfully")

            return df, start_time
        
        except Exception as e:
            self.logger.error(f"Failed to load mpr file from {file_path}: {e}")
            return None

    def _read_cellpy(self, file_path: str):
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