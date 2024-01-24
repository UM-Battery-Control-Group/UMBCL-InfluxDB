FROM python:3.9-slim

# set work directory
WORKDIR /app

# copy project
COPY . .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# run server
CMD ["python", "app.py"]
