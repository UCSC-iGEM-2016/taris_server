#############################################################
# setupDB.py:
#   The first application that creates our Bioreactor and changeLog databases.
#
#Date: August 8, 2016
#
#Written by:
#   Andrew Blair
#   Colin Hortman
#   Austin York
#   Lon Blauvelt
#   Henry Hinton
#
#Description:
#
#
#
################################################################
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class bioDec(Base):
    '''
    
    '''
    # Create the tablename that will be used to query the columns and rows later.
    __tablename__ = 'bio_Data'

    # Create the columns that will be used to input data from the parsed JSON file.
    # Primary key is a field in a table which uniquely identifies each row/record in a
    # database table. Primary keys must contain unique values. A primary value column cannot
    # have null values. A null value indicates that the value is unkown.
    timeData = Column('time', String, primary_key=True)
    temperature = Column('temperature', Integer)
    pH = Column('pH', Integer)
    NaOH = Column('NaOH', Integer)
    heater = Column('heater', Integer)
    inFlow = Column('inflow', Integer)
    outFlow = Column('outFlow', Integer)
    purifier = Column('purifier', Integer)


logBase = declarative_base()
class changeLog(logBase):
	'''
	user_Log creates a database that will hold the name of the person that edits a parameter for the bioreactor.
	'''

	__tablename__ = 'userInfo'

	# timeLog will take the server time when a user changes a parameter. Similar to timeData in bioDec.
	timeLog = Column('timeLog', Integer, primary_key=True)
	username = Column('username', String)
	password = Column('password', String)
	timeOn = Column('timeOn', String)
	changeValue = Column('changeValue', String)
	valueSet_to = Column('valueSet_to',String)

engine = create_engine('sqlite:///Bioreactor.db')
Base.metadata.create_all(engine)

logEngine = create_engine('sqlite:///changeLog.db')
logBase.metadata.create_all(logEngine)
