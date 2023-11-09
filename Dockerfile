FROM prefecthq/prefect:2.14.3-python3.11
COPY requirements.txt .
RUN pip install -r requirements.txt