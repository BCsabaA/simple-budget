import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

print(f"\n📡 DATABASE_URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

print("\n📋 Available tables:")
for table_name in inspector.get_table_names():
    print(f" - {table_name}")

print("\n📦 Schema: ", inspector.default_schema_name)
