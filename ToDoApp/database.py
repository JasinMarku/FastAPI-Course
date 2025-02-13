from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# Define the database URL
# MySQL URL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:test1234!@127.0.0.1:3306/TodoApplicationDatabase"

# Create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a base class for models
Base = declarative_base()