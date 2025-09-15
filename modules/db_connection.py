import json
import sqlalchemy
from pathlib import Path

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
