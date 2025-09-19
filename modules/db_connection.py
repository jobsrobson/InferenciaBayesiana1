import json
import sqlalchemy
from pathlib import Path
import os

if "DB_USER" in os.environ:
    # Credenciais do ambiente (Streamlit Cloud)
    CREDENTIALS_PATH = None
    def get_db_credentials():
        return {
            "db_user": os.environ["db_user"],
            "db_password": os.environ["db_password"],
            "db_host": os.environ["db_host"],
            "db_port": os.environ.get("db_port", "5432"),
            "db_name": os.environ["db_name"],
            "db_schema": os.environ.get("db_schema", "public"),
        }
else:
    # Credenciais locais via arquivo
    CREDENTIALS_PATH = Path(__file__).parent.parent / 'credentials.json'

def get_db_credentials():
    with open(CREDENTIALS_PATH, 'r') as f:
        creds = json.load(f)
    return creds

def create_pg_engine():
    creds = get_db_credentials()
    user = creds['db_user']
    password = creds['db_password']
    host = creds['db_host']
    port = creds['db_port']
    db = creds['db_name']
    schema = creds.get('db_schema', 'public')
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    engine = sqlalchemy.create_engine(url, connect_args={"options": f"-c search_path={schema}"})
    return engine
