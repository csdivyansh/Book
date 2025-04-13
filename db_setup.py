from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from flask_login import UserMixin

Base = declarative_base()

class Client(Base, UserMixin):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default='client')

class Entity(Base):
    __tablename__ = 'entities'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship("Client")
    size = Column(Integer, nullable = False)
    description = Column(String, nullable=False)
    completed = Column(Boolean, default=False)

engine = create_engine('sqlite:///zdb.db')
Base.metadata.create_all(engine)