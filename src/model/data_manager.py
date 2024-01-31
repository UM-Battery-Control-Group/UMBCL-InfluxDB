import os
import pandas as pd
import datetime
from src.utils import setup_logger
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, WriteApi
from influxdb_client.client.write_api import SYNCHRONOUS
from src.model import DataParser
from src.config import name_config as tag_keys

load_dotenv('influx.env')

class DataManager:

    def __init__(self) -> None:
        self.url = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
        self.token = os.getenv('INFLUXDB_TOKEN')
        self.org = os.getenv('INFLUXDB_ORG')
        self.bucket = os.getenv('INFLUXDB_BUCKET')
        self.logger = setup_logger()
        self.data_parser = DataParser()

    def write_data(self, file_path: str, data_type = ""):
        """
        Write the data from the Arbin file into the InfluxDB database

        Parameters
        ----------
        file_path : str
            The path to the Arbin file
        data_type : str (optional)
            The data type, i.e. "neware_vdf", "arbin", etc.
        """
        if data_type == "":
            # Determine the data type based on the file extension
            file_extension = file_path.split(".")[-1]
            if file_extension == "res":
                data_type = "arbin"
            elif file_extension == "csv":
                data_type = "neware_vdf"
            elif file_extension == "mpr":
                data_type = "biologic"
            elif file_extension == "xlsx":
                data_type = "neware"
            else:
                raise ValueError(f"File extension {file_extension} is not supported")
        tags = ["Cycler"]
        # Parse the data from the Arbin file
        if data_type.lower() == "neware_vdf":
            df = self.data_parser.parse_neware_vdf(file_path)
            tags.extend(tag_keys.NEWARE_NAME_KEYS)
        elif data_type.lower() == "arbin":
            df = self.data_parser.parse_arbin(file_path)
            tags.extend(tag_keys.ARBIN_NAME_KEYS)
        elif data_type.lower() == "biologic":
            df = self.data_parser.parse_biologic(file_path)
            tags.extend(tag_keys.BIOLOGIC_NAME_KEYS)
        elif data_type.lower() == "neware":
            df = self.data_parser.parse_neware(file_path)
            tags.extend(tag_keys.NEWARE_NAME_KEYS)
        else:
            raise ValueError(f"Data type {data_type} is not supported")

        measurement_name = file_path.split("/")[-1].split(".")[0]   # Use the file name as the measurement name
        if df is None:
            return
        
        # Write the data into the database
        with InfluxDBClient(url=self.url, token=self.token, org=self.org, timeout=100000) as client:
            self.logger.info(f"Start writing file {file_path} into InfluxDB database")
            write_api = client.write_api(write_options=SYNCHRONOUS)

            # Write the data into the database
            write_api.write(bucket=self.bucket, record=df, 
                            data_frame_measurement_name=measurement_name,
                            data_frame_tag_columns=tags,
                            data_frame_timestamp_column="Timestamp(epoch)")
            
            self.logger.info(f"Finish writing file {file_path} into InfluxDB database")

    def query_data(self, measurement=None, tags=None, start_time="-100y", end_time="now()"):
        """
        Query data from the InfluxDB database optionally by measurement, tag, and time range

        Parameters
        ----------
        measurement : str, optional
            The measurement name
        tags : dict, optional
            The dictionary of tags
        start_time : str, optional
            Start time for the query (default is "-100y")
            Input format: "2021-09-01T00:00:00Z" or "-3y" (3 years ago) or "-3d" (3 days ago)
        end_time : str, optional
            End time for the query (default is "now()")

        Returns
        -------
        dfs: dict
            The dictionary of dataframes, where the key is the measurement name and the value is the dataframe
        """
        measurement_filter = f'r["_measurement"] == "{measurement}"' if measurement else ''
        tag_filters = [f'r["{key}"] == "{value}"' for key, value in tags.items()] if tags else []
    
        # Combine filters
        filters = " and ".join(filter(None, [measurement_filter] + tag_filters))
        print(filters)
        if filters:
            filters = f'|> filter(fn: (r) => {filters})'
        
        query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: {start_time}, stop: {end_time})
                {filters}
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        return self._query_data(query)


    def _query_data(self, query):
        """
        Query data from the InfluxDB database

        Parameters
        ----------
        query : str
            The query string

        Returns
        -------
        dfs: dict
            The dictionary of dataframes, where the key is the measurement name and the value is the dataframe
        """
        with InfluxDBClient(url=self.url, token=self.token, org=self.org) as client:
            self.logger.info(f"Start querying data from InfluxDB database")
            query_api = client.query_api()
            result = query_api.query_data_frame(query=query)
            self.logger.info(f"Finish querying data from InfluxDB database")
            dfs = {}
            if isinstance(result, list):
                for df in result:
                    if '_measurement' in df:
                        measurement = df['_measurement'].iloc[0]
                        dfs[measurement] = df.sort_values(by='_time')
            elif '_measurement' in result:
                measurement = result['_measurement'].iloc[0]
                dfs[measurement] = result.sort_values(by='_time')
            return dfs
