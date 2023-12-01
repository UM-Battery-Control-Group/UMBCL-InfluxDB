import csv
import datetime
from influxdb_client import Point
from src.utils import setup_logger
from src.config import TZ_INFO, name_config

class DataParser:

    def __init__(self) -> None:
        self.logger = setup_logger()
        self.tz_info = TZ_INFO

    def parse_neware_vdf(self, file_path):
        """
        Parse the Neware VDF file into a pandas dataframe

        Parameters
        ----------
        file_path : str
            The path to the Neware VDF file

        Returns
        -------
        pandas.DataFrame
            The pandas dataframe containing the data from the Neware VDF file
        """
        vdf_row_itr = self._read_csv(file_path)
        if vdf_row_itr is None:
            self.logger.error(f"The Neware VDF file {file_path} is empty")
            return None
        # Define the meta data and data
        data_start = False
        headers = []
        units = []
        points = []
        measurement_name = file_path.split("/")[-1].split(".")[0]   # Use the file name as the measurement name
        vdf_meta = self._neware_measurement_name_to_metadata(measurement_name)
        self.logger.info(f"Start parsing Neware VDF file {measurement_name}")
        try:
            # Iterate through the rows
            for row in vdf_row_itr:
                # Skip the empty rows
                if len(row) == 0:
                    continue
                # Meta data stored before the data starts
                if not data_start:
                    # Check if the row is the start of the data
                    if "[DATA START]" in row:
                        data_start = True
                        continue
                    # Parse the meta data, meta data is stored in the format of "key: value" in row[0]
                    vdf_meta[row[0].split(":")[0].replace(' ', '_')] = row[0].split(":")[1].strip()
                else:
                    # The first row of the data is the column names, second row is the units, put them into header together
                    if len(headers) == 0:
                        headers = row[0].split('\t')
                        headers = [header.replace('\\', '').replace(' ', '_') for header in headers]
                        continue
                    if len(units) == 0:
                        units = row[0].split('\t')
                        headers = [header + "(" + unit + ")" for header, unit in zip(headers, units)]
                        continue
                    # Generate the data points
                    point = Point(measurement_name)
                    for key, value in vdf_meta.items():
                        point = point.tag(key, value)
                    values = row[0].split('\t')
                    for header, value in zip(headers, values):
                        if header == 'Timestamp(epoch)':
                            # Convert the timestamp to datetime
                            t = self._timestamp_to_datetime(float(value))
                            self.logger.debug(f"Start parsing Neware VDF file {measurement_name} at {t}")
                            point = point.time(t)
                            continue
                        point = point.field(header, value)
                    points.append(point)
            self.logger.info(f"Finished parsing Neware VDF file {measurement_name}")   
            return points
        except Exception as e:
            self.logger.error(f"Failed to parse Neware VDF file {measurement_name}")
            self.logger.error(e)
            return None

    def _neware_measurement_name_to_metadata(self, measurement_name):
        """
        Format the Neware VDF file name: 
            [ProjectName]_[DeviceID]_[TestType]_[ProcedureVersion]_[Temperature]_[Pressure]_[TestDate]_[RunNumber]_[ChannelNumber]

        Parameters
        ----------
        measurement_name : str
            The name of the Neware VDF file

        Returns
        -------
        dict
            The dictionary containing the metadata
        """
        try:
            # Split the measurement name by "_" 
            metadata = dict(zip(name_config.NEWARE_NMAE_KEYS, measurement_name.split("_")))
            return metadata
        except Exception as e:
            self.logger.error(f"Failed to format the Neware VDF file name {measurement_name}")
            self.logger.error(e)
            return None
        
    def _read_csv(self, file_path):
        """
        Read the csv file and return the iterator of rows

        Parameters
        ----------
        file_path : str
            The path to the csv file

        Returns
        -------
        iter
            The iterator of rows from the csv file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # Use csv.reader to read the file and convert it to a list of rows
                rows = list(csv.reader(f))
            self.logger.info(f"Loaded csv file from {file_path} successfully")
            return iter(rows)
        except Exception as e:
            self.logger.error(f"Failed to load csv file from {file_path}")
            self.logger.error(e)
            return None
        
    def _timestamp_to_datetime(self, timestamp):
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