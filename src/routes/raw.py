from flask import Blueprint, request, jsonify, current_app, send_file, render_template
from werkzeug.utils import secure_filename
from src.model.data_manager import DataManager
import os
from io import BytesIO
import zipfile

raw_blueprint = Blueprint('raw', __name__)
data_manager = DataManager()

@raw_blueprint.route('/')
def index():
    return render_template('raw/index.html')

@raw_blueprint.route('/upload')
def upload_form():
    return render_template('raw/upload.html')

@raw_blueprint.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file.save(filepath)  
        
        # Process the file and write the data to InfluxDB
        try:
            data_manager.write_data(filepath)  
            os.remove(filepath)  # Delete the file after processing
            return jsonify({"message": "File processed and deleted successfully"}), 200
        except Exception as e:
            os.remove(filepath)  # Make sure to delete the file if an error occurs
            return jsonify({"error": str(e)}), 500

@raw_blueprint.route('/query_and_download')
def query_and_download_form():
    return render_template('raw/query_and_download.html')

@raw_blueprint.route('/query_and_download', methods=['GET'])
def query_and_download():
    # Get the query parameters from the request
    measurement = request.args.get('measurement')
    start_time = request.args.get('start_time', '-100y')  
    end_time = request.args.get('end_time', 'now()')
    
    # Parse the tags from the request
    tags_str = request.args.get('tags')
    tags = {}
    if tags_str:
        try:
            tags_list = tags_str.split(',')
            for tag in tags_list:
                key, value = tag.split('=')
                tags[key] = value
        except ValueError:
            return jsonify({"error": "Invalid tags format"}), 400
    
    try:
        # Query the data from InfluxDB
        dfs = data_manager.query_data(measurement, start_time, end_time, tags)
        # Write the data to CSV files, based on the measurement
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for measurement_name, df in dfs.items():
                # Convert the dataframe to CSV and write it to the ZIP file
                csv_buffer = BytesIO()
                df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                zip_file.writestr(f"{measurement_name}.csv", csv_buffer.read())

        zip_buffer.seek(0)
        
        # Return the ZIP file as an attachment
        return send_file(zip_buffer, mimetype='application/zip', 
                         as_attachment=True, attachment_filename='measurements_data.zip')
    except Exception as e:
        return jsonify({"error": str(e)}), 500