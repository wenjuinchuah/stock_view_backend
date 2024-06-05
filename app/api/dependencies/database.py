from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# username:password@host:port/database
IS_PRODUCTION = True
DATABASE_PREFIX = "db" if IS_PRODUCTION else "localhost"
URL_DATABASE = f"mysql+pymysql://root:@{DATABASE_PREFIX}:3306/"

engine = create_engine(URL_DATABASE + "stock_view")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
