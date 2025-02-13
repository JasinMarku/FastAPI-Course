from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# Define the database URL
# MySQL URL
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://fastapi_todo_db_owvq_user:B3wG9HCPImPw8gjsXd5AHBNOAE0KYdu2@dpg-cun6mj3tq21c73edghe0-a/fastapi_todo_db_owvq"
# Create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a base class for models
Base = declarative_base()