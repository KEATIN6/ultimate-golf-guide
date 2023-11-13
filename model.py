# -*- coding: utf-8 -*-
"""
Created on Sat Oct  1 16:58:22 2022

@author: pizzacoin
"""

# %%

from datetime import datetime
from sqlalchemy import Column, create_engine
from sqlalchemy import Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

# %%

class RoundOlv:
    def __init__(self, round_id, course_name, 
                 number_of_players, best_score, tee_time):
        self.round_id = round_id
        self.course_name = course_name
        self.number_of_players = number_of_players
        self.best_score = best_score
        self.tee_time = tee_time
        
    # %%

class PlayerOlv:
    def __init__(self, player_id, player_name, score, best_hole):
        self.player_id = player_id
        self.player_name = player_name
        self.score = score
        self.best_hole = best_hole
     
# %%

class ParkOlv:
    def __init__(self, park_id, park_name, county, privacy_type):
        self.park_id = park_id 
        self.park_name = park_name
        self.county = county
        self.privacy_type = privacy_type
        
# %%

class CoursePlayerOlv:
    def __init__(self, player_id, round_id, first_name, 
                 last_name, total_strokes, tee_time):
        self.player_id = player_id
        self.round_id = round_id
        self.first_name = first_name
        self.last_name = last_name
        self.player_name = first_name + ' ' + last_name
        self.total_strokes = total_strokes
        self.tee_time = tee_time

# %%

class CourseDetailsOlv:
    def __init__(self, description, data, keys=None):
        self.description = description
        self.set_data(data)
        self.to_dict()
        self.keys = keys
        
    def return_key(self, key):
        if key in self.keys.keys():
            return self.keys[key]
        
    def set_data(self, data):
        count = 1
        for (key, value) in data:
            setattr(self, f"key_{('0'+str(count))[-2:]}", key)
            setattr(self, f"value_{('0'+str(count))[-2:]}", value)
            count += 1
        
    def to_dict(self):
        data = {}
        for prop, value in vars(self).items():
            if "value_" in prop:
                data[int(prop[-2:])] = value
        return data
    
# %%

class CourseOlv:
    def __init__(self, course_id, course_name, no_of_holes, times_played, par):
        self.course_id = course_id 
        self.course_name = course_name
        self.no_of_holes = no_of_holes 
        self.times_played = times_played 
        self.par = par


# %% SETUP THE DATABASE ENGINE

engine = create_engine("sqlite:///UltimateGolfGuideDB.db", echo=True)
Base = declarative_base()
metadata = Base.metadata

# %%

class DatabaseObject:
    def setup(self, session):
        self.session = session
        return self
    
    def save(self) -> bool:
        self.session.add(self)
        self.session.commit()
        return True

# %% Ultimate Golf Guide (UGG) Data Model

class UGG_Park(Base, DatabaseObject):
    __tablename__ = "UGG_Parks"
    
    ParkID = Column(Integer, primary_key=True)
    CountyID = Column(Integer)
    PrivacyTypeID = Column(Integer)
    ParkName = Column(String)
    NoOfCourses = Column(Integer)
    NoOfHoles = Column(Integer)
    Website = Column(String)
    IsActive = Column(Integer)
    CreateDate = Column(DateTime)
    LastUpdated = Column(DateTime)
    
    def __init__(self, session, privacy_type_id, park_name, website):
        self.setup(session)
        self.PrivacyTypeID = privacy_type_id
        self.ParkName = park_name
        self.NoOfCourses = 0
        self.NoOfHoles = 0
        self.Website = website
        self.IsActive = 1
        self.CreateDate = datetime.now()
        self.LastUpdated = datetime.now() 
    
class UGG_Address(Base, DatabaseObject):
    __tablename__ = "UGG_Addresses"
    
    AddressID = Column(Integer, primary_key=True)
    StreetAddress = Column(String)
    City = Column(String)
    State = Column(String)
    ZipCode = Column(String)
    County = Column(String)
    
class UGG_ParkPrivacyType(Base, DatabaseObject):
    __tablename__ = "UGG_ParkPrivacyTypes"
    
    PrivacyTypeID = Column(Integer, primary_key=True)
    PrivacyType = Column(String)
    Description = Column(String)
    
class UGG_Course(Base, DatabaseObject):
    __tablename__ = "UGG_Courses"
    
    CourseID = Column(Integer, primary_key=True)
    ParkID = Column(Integer)
    AddressID = Column(Integer)
    CourseTypeID = Column(Integer)
    CourseName = Column(String)
    NoOfHoles = Column(Integer)
    NoOfTees = Column(Integer)
    Par = Column(Integer)
    DistMin = Column(Integer)
    DistMax = Column(Integer)
    IsActive = Column(Integer)
    LastUpdated = Column(DateTime)
    
    def __init__(self, park_id, couse_name, no_of_holes):
        self.ParkID = park_id
        self.CourseName = couse_name
        self.NoOfHoles = no_of_holes
        self.NoOfTees = 0 
        self.IsActive = 1 
        self.LastUpdated = datetime.now()
        
class UGG_Hole(Base, DatabaseObject):
    __tablename__ = "UGG_Holes"
    
    HoleID = Column(Integer, primary_key=True)
    CourseID = Column(Integer)
    HoleNumber = Column(Integer)
    Par = Column(Integer)
    Handicap = Column(Integer)
    DistMin = Column(Integer)
    DistMax = Column(Integer)
    
    def __init__(self, session, course_id, hole_number, par, handicap=None):
        self.setup(session)
        self.CourseID = course_id
        self.HoleNumber = hole_number
        self.Par = par
        self.Handicap = handicap
    
class UGG_CourseType(Base, DatabaseObject):
    __tablename__ = "UGG_CourseTypes"
    
    CourseTypeID = Column(Integer, primary_key=True)
    TypeName = Column(String)
    Description = Column(String)
    
class UGG_CourseTee(Base, DatabaseObject):
    __tablename__ = "UGG_CourseTees"
    
    CourseTeeID = Column(Integer, primary_key=True)
    CourseID = Column(Integer)
    TeeColorID = Column(Integer)
    Difficulty = Column(Float)
    Slope = Column(Integer)
    Distance = Column(Integer)
    
    def __init__(self, session, course_id, tee_color_id, difficulty, slope):
        self.setup(session)
        self.CourseID = course_id
        self.TeeColorID = tee_color_id
        self.Difficulty = difficulty
        self.Slope = slope
        
class UGG_HoleTee(Base, DatabaseObject):
    __tablename__ = "UGG_HoleTees"
    
    HoleTeeID = Column(Integer, primary_key=True)
    CourseTeeID = Column(Integer)
    HoleID = Column(Integer)
    Distance = Column(Integer)
    
    def __init__(self, session, course_tee_id, hole_id, distance):
        self.setup(session)
        self.CourseTeeID = course_tee_id
        self.HoleID = hole_id
        self.Distance = distance
    
class UGG_TeeColor(Base, DatabaseObject):
    __tablename__ = "UGG_TeeColors"
    
    TeeColorID = Column(Integer, primary_key=True)
    Color = Column(String)
    Description = Column(String)
        
class UGG_Golfer(Base, DatabaseObject):
    __tablename__ = "UGG_Golfers"
    
    GolferID = Column(Integer, primary_key=True)
    FirstName = Column(String)
    LastName = Column(String)
    Email = Column(String)
    PhoneNumber = Column(String)
    County = Column(String)
    
class UGG_County(Base, DatabaseObject):
    __tablename__ = "UGG_Counties"
    
    CountyID = Column(Integer, primary_key=True)
    CountyName = Column(String)
    State = Column(String)
    CreateDate = Column(DateTime)
    LastUpdated = Column(DateTime)
    
    
class UGG_Round(Base, DatabaseObject):
    __tablename__ = "UGG_Rounds"
    
    RoundID = Column(Integer, primary_key=True)
    CourseID = Column(Integer)
    TeeTime = Column(DateTime) 
    TimeFinished = Column(DateTime)
    NoOfPlayers = Column(Integer)
    
    def __init__(self, session, course_id, no_of_players):
        self.setup(session)
        self.CourseID = course_id
        self.NoOfPlayers = no_of_players
    
class UGG_Player(Base, DatabaseObject):
    __tablename__ = "UGG_Players"
    
    PlayerID = Column(Integer, primary_key=True)
    GolferID = Column(Integer)
    RoundID = Column(Integer)
    CourseTeeID = Column(Integer)
    TotalStrokes = Column(Integer)
    Order = Column(Integer)
    CreateDate = Column(DateTime)
    
    def __init__(self, golfer_id, round_id, order=None):
        self.GolferID = golfer_id
        self.RoundID = round_id
        self.Order = order
        self.CreateDate = datetime.now()
    
class UGG_Score(Base, DatabaseObject):
    __tablename__ = "UGG_Scores"
    
    ScoreID = Column(Integer, primary_key=True)
    PlayerID =  Column(Integer)
    HoleTeeID = Column(Integer)
    ScoringTermID = Column(Integer)
    Strokes = Column(Integer)
    
class UGG_ScoringTerm(Base, DatabaseObject):
    __tablename__ = "UGG_ScoringTerms"
    
    ScoringTermID = Column(Integer, primary_key=True)
    ScoringTerm = Column(String)
    AmountToPar = Column(Integer)
    Meaning = Column(String)
    
# %%

Base.metadata.create_all(engine)

# %%

