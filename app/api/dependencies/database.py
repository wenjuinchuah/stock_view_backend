from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# username:password@host:port/database
URL_DATABASE = "mysql+pymysql://root:@localhost:3306/"
PRODUCTION_DATABASE = "stock_view"
TEST_DATABASE = "stock_view_test"
IN_PRODUCTION = True

engine = create_engine(
    URL_DATABASE + (PRODUCTION_DATABASE if IN_PRODUCTION else TEST_DATABASE)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
