from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./inventory.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Inventory(Base):
    __tablename__ = "inventories"
    product_id = Column(Integer, primary_key=True, index=True)
    cantidad = Column(Integer, nullable=False, default=0)

def init_db():
    Base.metadata.create_all(bind=engine)
