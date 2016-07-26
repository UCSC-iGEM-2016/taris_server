import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class Bioreactor_Data(Base):
	__tablename__ = 'Bio_Data'
	#motor_power= Column(Integer, primary_key=True)
	timedata = Column(String, primary_key=True) #Mark time of each entry

	temperature = Column(Integer, primary_key=True)
	pH = Column(Integer, primary_key=True)
	NaOH = Column(Integer, primary_key=True)
	heater = Column(Integer, primary_key = True)
	inFlow = Column(Integer, primary_key = True)
	outFlow = Column(Integer, primary_key = True)
	purifier = Column(Integer, primary_key = True)

userBase = declarative_base()

class user_log(userBase):
	__tablename__ = 'userInfo'
	username = Column(String, primary_key=True)
	password = Column(String, primary_key=True)
	timeOn = Column(String, primary_key=True)
	changeValue = Column(String, primary_key=True)



engine = create_engine('sqlite:///Bioreactor.db')
Base.metadata.create_all(engine)

userEngine = create_engine('sqlite:///userLog.db')
userBase.metadata.create_all(userEngine)

