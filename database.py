from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./cars.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class CarDB(Base):
    __tablename__ = "cars"
    id              = Column(Integer, primary_key=True, index=True)
    owner_name      = Column(String,  nullable=False)
    brand           = Column(String,  nullable=False)
    model           = Column(String,  nullable=False)
    year            = Column(Integer, nullable=False)
    fuel_type       = Column(String,  nullable=False)
    transmission    = Column(String,  nullable=False)
    owner           = Column(String,  nullable=False)
    km_driven       = Column(Integer, nullable=False)
    mileage         = Column(Float,   nullable=False)
    engine          = Column(Float,   nullable=False)
    max_power       = Column(Float,   nullable=False)
    predicted_price = Column(Float,   nullable=True)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
