__author__ = '123'
# coding=utf-8
import pymysql
from sqlalchemy import Column, String, create_engine, Integer
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base

if __name__ == '__main__':
    engine = create_engine("mysql+pymysql://root:123456@192.168.1.17:3308/dididu_exchange", echo=True)
    session = Session(engine)
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    r = session.query(Base.classes).all()