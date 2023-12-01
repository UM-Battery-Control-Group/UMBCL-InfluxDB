# UMBCL_InfluxDB

This project seamlessly store the battery test record into the InfluxDataBase, offering an efficient solution for write and read data.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setting up a Virtual Environment](#setting-up-a-virtual-environment)
3. [Installing Dependencies](#installing-dependencies)
4. [Docker](#docker)
5. [Usage](#usage)
6. [License](#license)
7. [Questions](#questions)

## Prerequisites

- Python 3.7 or higher
- pip (comes with Python)
- Docker and Docker-compose (https://www.docker.com)

## Setting up a Virtual Environment

Virtual environments allow you to manage project-specific dependencies, which can prevent conflicts between versions.

1. **Install `virtualenv`** (If not installed)

    ```bash
    pip install virtualenv
    ```

2. **Navigate to your project directory**:

    ```bash
    cd /path/to/your/project
    ```

3. **Create a virtual environment**:

    ```bash
    virtualenv venv
    ```

4. **Activate the virtual environment**:

    - On macOS and Linux:

        ```bash
        source venv/bin/activate
        ```

    - On Windows:

        ```bash
        .\venv\Scripts\activate
        ```

    After activation, your command prompt should show the name of the virtual environment (`venv` in this case).

## Installing Dependencies

Once the virtual environment is activated, you can install the project's dependencies.

```bash
pip install -r requirements.txt
```

## Docker

Install docker: https://www.docker.com/products/docker-desktop/

1. Connect our network drive to your PC.  
2. Navigate to 'docker-compose.yml'.  
3. Update the 'volumns' to the path of our network drive and map that.

To start the container:

```bash
docker-compose up
```

To stop the container:

```bash
docker-compose down
```

To access the InfluxDB dashboard, navigate to localhost:8086. Log in using the credentials specified in the 'docker-compose.yml' file. Once logged in, locate the 'Data' section and select 'Tokens'. Copy the displayed token and then replace the existing token in the 'influx.env' file with this new one.

## Usage

To upload the neware file:

```python
    from src.model improt DataManager
    data_manager = DataManager()
    file_path = "path/to/the/file"
    data_manager.write_neware_vdf_data(file_path)
```

To make the query:

```python
    from src.model improt DataManager
    data_manager = DataManager()
    measurement = "GMJuly2022_CELL004_EIS_3d_P25C_25P0PSI_20230324_R0_CH032"
    tags = {"ChannelNumber": "CH032", "Pressure": "25P0PSI"}
    data = data_manager.query_data(tags=tags) 
    # OR data = data_manager.query_data(measurement=measurement)
```

To learn more about the write and query API, hover your cursor over the respective function to view a tooltip or pop-up with detailed instructions and information.

## License
This project is licensed under the MIT License.

## Questions

If you have any questions or encounter any bugs, please raise an issue in our repository or send an email to ziyiliu@umich.edu. We greatly appreciate your feedback.