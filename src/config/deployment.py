from dotenv import load_dotenv
import os

load_dotenv('influx.env')

class DevelopmentConfig():
        url = os.getenv('INFLUXDB_URL', 'http://localhost:8081')
        token = os.getenv('INFLUXDB_TOKEN')
        org = os.getenv('INFLUXDB_ORG')
        bucket = os.getenv('INFLUXDB_BUCKET')
        UPLOAD_FOLDER = '/tmp/myflaskapp_uploads'