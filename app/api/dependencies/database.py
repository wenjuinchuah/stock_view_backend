from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

IS_PRODUCTION = True
DATABASE_NAME = "stock_view"
DATABASE_PREFIX = "db" if IS_PRODUCTION else "localhost"
URL_DATABASE = f"mysql+pymysql://root:@{DATABASE_PREFIX}:3306/"  # username:password@host:port/database

engine = create_engine(URL_DATABASE)

with engine.connect() as connection:
    connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))

engine = create_engine(URL_DATABASE + DATABASE_NAME)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
