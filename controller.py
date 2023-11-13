# -*- coding: utf-8 -*-
"""
Created on Tue May 30 21:43:21 2023

@author: pizzacoin
"""

# %%

from model import CourseDetailsOlv
from model import CoursePlayerOlv
from model import CourseOlv
from model import ParkOlv
from model import PlayerOlv
from model import RoundOlv
from model import UGG_Course
from model import UGG_CourseTee
from model import UGG_Hole
from model import UGG_HoleTee
from model import UGG_Park
from model import UGG_ParkPrivacyType 
from model import UGG_Player
from model import UGG_TeeColor
from model import UGG_Round
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import model
import sql

# %%

def connect_to_database():
    engine = create_engine("sqlite:///UltimateGolfGuideDB.db", echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

# %%

def get_player_olv(session, round_id):
    players = []
    results = session.execute(sql.players_round(round_id)).all()
    for result in results:
        players.append(PlayerOlv(
            result[0], result[1] + ' ' + result[2], result[3], result[4]))
    return players

def get_active_golf_courses(session):
    results = session.query(
        UGG_Course
    ).filter(
        model.UGG_Course.IsActive == 1
    ).all()
    return [(c.CourseID, c.CourseName) for c in results]

def get_privacy_types(session):
    results = session.query(
        UGG_ParkPrivacyType    
    ).all()
    return [(r.PrivacyTypeID, r.PrivacyType) for r in results]

def get_park_names(session):
    results = session.query(
        UGG_Park
    ).filter(
        UGG_Park.IsActive == 1
    ).all()
    return [r.ParkName for r in results]

def get_round_by_id(session, round_id):
    results = session.query(
        UGG_Round    
    ).filter(
        UGG_Round.RoundID == round_id
    ).all()
    return results[0]

def get_course_by_id(session, course_id):
    results = session.query(
        UGG_Course    
    ).filter(
        UGG_Course.CourseID == course_id
    ).all()
    return results[0]
    
def get_course_tees(session, course_id):
    results = session.query(
        UGG_CourseTee, UGG_TeeColor
    ).filter(
        UGG_CourseTee.CourseID == course_id
    ).filter(
        UGG_CourseTee.TeeColorID == UGG_TeeColor.TeeColorID
    ).all()
    return [(c[0].CourseTeeID, c[1].Color) for c in results]

def get_parks(session):
    results = session.execute("""
        SELECT P.ParkID, P.ParkName, CountyName, T.PrivacyType
        FROM UGG_Parks P
        JOIN UGG_Counties C ON C.CountyID=P.CountyID
        JOIN UGG_ParkPrivacyTypes T ON T.PrivacyTypeID=P.PrivacyTypeID
    """).all()
    parks = []
    for result in results:
        park = ParkOlv(result[0], result[1], result[2], result[3])
        parks.append(park)
    return parks

def get_courses(session, park_id):
    results = session.execute(f"""
        SELECT C.CourseID, CourseName, NoOfHoles, C.Par
        FROM UGG_Courses C 
        WHERE C.ParkID = {park_id}
    """).all()
    courses = []
    for result in results:
        course = CourseOlv(result[0], result[1], result[2], 0, result[3])
        courses.append(course)
    return courses

def update_hole(session, course_id, hole_number, par):
    results = session.query(
        UGG_Hole  
    ).filter(
        UGG_Hole.HoleNumber == hole_number
    ).filter(
        UGG_Hole.CourseID ==  course_id
    ).all()
    if results:
        hole = results[0]
        hole.Par = par
        hole.setup(session)
    else:
        hole = UGG_Hole(session, course_id, hole_number, par)
    hole.save()
    return hole

def update_holes(session, course_id, data):
    total = 0
    for hole_number in data.keys():
        update_hole(session, course_id, hole_number, data[hole_number])
        total += int(data[hole_number])
    results = session.query(UGG_Course).filter(
        UGG_Course.CourseID == course_id).all()[0]
    results.Par = total
    results.setup(session)
    results.save()
    
def update_distance(session, course_id, course_tee_id, hole_number, distance):
    print(course_tee_id)
    results = session.query(
        UGG_HoleTee 
    ).join(
        UGG_Hole, UGG_Hole.HoleID == UGG_HoleTee.HoleID
    ).filter(
        UGG_Hole.HoleNumber == hole_number
    ).filter(
        UGG_HoleTee.CourseTeeID ==  course_tee_id
    ).all()
    if results:
        hole_tee = results[0]
        print(results[0])
        hole_tee.Distance = distance
        hole_tee.setup(session)
    else:
        print("AHHHH")
        hole_id = get_hole_id(session, course_id, hole_number)
        hole_tee = UGG_HoleTee(session, course_tee_id, hole_id, distance)
    hole_tee.save()
    return hole_tee

def update_distances(session, course_id, course_tee_id, data):
    total = 0
    for hole_number in data.keys():
        update_distance(session, course_id, course_tee_id, 
                        hole_number, data[hole_number])
        total += int(data[hole_number])
        print(total)
    
def get_tee_color_id(session, color):
    results = session.execute(f"""
        SELECT TeeColorID
        FROM UGG_TeeColors
        WHERE Color LIKE '{color}'
    """).all()
    if results:
        return results[0][0]
    
def get_hole_id(session, course_id, hole_number):
    results = session.execute(f"""
        SELECT HoleID
        FROM UGG_Holes
        WHERE CourseID={course_id}
        AND HoleNumber={hole_number}
    """).all()
    if results:
        return results[0][0]
    
def create_hole_tees(session, course_id, course_tee_id, no_of_holes):
    for hole_number in range(no_of_holes):
        hole_id = get_hole_id(session, course_id, hole_number+1)
        hole = UGG_HoleTee(session, course_tee_id, hole_id, None)
        hole.save()
        
        
def create_course_tees(session, course, color, difficulty=None, slope=None):
    tee_color_id = get_tee_color_id(session, color)
    course_tee = UGG_CourseTee(
        session, course.course_id, tee_color_id, difficulty, slope)
    course_tee.save()
    create_hole_tees(
        session, course.course_id, course_tee.CourseTeeID, course.no_of_holes)
    
def get_tee_color_values(session, course_id, color=None):
    query = f"""
        SELECT Color, 
        	T1.Distance, T2.Distance, T3.Distance, T4.Distance, T5.Distance, T6.Distance,
        	T7.Distance, T8.Distance, T9.Distance, T10.Distance, T11.Distance, T12.Distance,
        	T13.Distance, T14.Distance, T15.Distance, T16.Distance, T17.Distance, T18.Distance,
        	T1.HoleTeeID, T2.HoleTeeID, T3.HoleTeeID, T4.HoleTeeID, T5.HoleTeeID, 
            T6.HoleTeeID, T7.HoleTeeID, T8.HoleTeeID, T9.HoleTeeID, T10.HoleTeeID, 
            T11.HoleTeeID, T12.HoleTeeID, T13.HoleTeeID, T14.HoleTeeID, T15.HoleTeeID, 
            T16.HoleTeeID, T17.HoleTeeID, T18.HoleTeeID, CT.CourseTeeID
        FROM UGG_TeeColors TC
        JOIN UGG_CourseTees CT ON CT.TeeColorID=TC.TeeColorID
        LEFT JOIN UGG_Holes H1 ON H1.CourseID=CT.CourseID AND H1.HoleNumber=1
        LEFT JOIN UGG_HoleTees T1 ON T1.HoleID=H1.HoleID AND T1.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H2 ON H2.CourseID=CT.CourseID AND H2.HoleNumber=2
        LEFT JOIN UGG_HoleTees T2 ON T2.HoleID=H2.HoleID AND T2.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H3 ON H3.CourseID=CT.CourseID AND H3.HoleNumber=3
        LEFT JOIN UGG_HoleTees T3 ON T3.HoleID=H3.HoleID AND T3.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H4 ON H4.CourseID=CT.CourseID AND H4.HoleNumber=4
        LEFT JOIN UGG_HoleTees T4 ON T4.HoleID=H4.HoleID AND T4.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H5 ON H5.CourseID=CT.CourseID AND H5.HoleNumber=5
        LEFT JOIN UGG_HoleTees T5 ON T5.HoleID=H5.HoleID AND T5.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H6 ON H6.CourseID=CT.CourseID AND H6.HoleNumber=6
        LEFT JOIN UGG_HoleTees T6 ON T6.HoleID=H6.HoleID AND T6.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H7 ON H7.CourseID=CT.CourseID AND H7.HoleNumber=7
        LEFT JOIN UGG_HoleTees T7 ON T7.HoleID=H7.HoleID AND T7.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H8 ON H8.CourseID=CT.CourseID AND H8.HoleNumber=8
        LEFT JOIN UGG_HoleTees T8 ON T8.HoleID=H8.HoleID AND T8.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H9 ON H9.CourseID=CT.CourseID AND H9.HoleNumber=9
        LEFT JOIN UGG_HoleTees T9 ON T9.HoleID=H9.HoleID AND T9.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H10 ON H10.CourseID=CT.CourseID AND H10.HoleNumber=10
        LEFT JOIN UGG_HoleTees T10 ON T10.HoleID=H10.HoleID AND T10.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H11 ON H11.CourseID=CT.CourseID AND H11.HoleNumber=11
        LEFT JOIN UGG_HoleTees T11 ON T11.HoleID=H11.HoleID AND T11.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H12 ON H12.CourseID=CT.CourseID AND H12.HoleNumber=12
        LEFT JOIN UGG_HoleTees T12 ON T12.HoleID=H12.HoleID AND T12.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H13 ON H13.CourseID=CT.CourseID AND H13.HoleNumber=13
        LEFT JOIN UGG_HoleTees T13 ON T13.HoleID=H13.HoleID AND T13.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H14 ON H14.CourseID=CT.CourseID AND H14.HoleNumber=14
        LEFT JOIN UGG_HoleTees T14 ON T14.HoleID=H14.HoleID AND T14.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H15 ON H15.CourseID=CT.CourseID AND H15.HoleNumber=15
        LEFT JOIN UGG_HoleTees T15 ON T15.HoleID=H15.HoleID AND T15.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H16 ON H16.CourseID=CT.CourseID AND H16.HoleNumber=16
        LEFT JOIN UGG_HoleTees T16 ON T16.HoleID=H16.HoleID AND T16.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H17 ON H17.CourseID=CT.CourseID AND H17.HoleNumber=17
        LEFT JOIN UGG_HoleTees T17 ON T17.HoleID=H17.HoleID AND T17.CourseTeeID=CT.CourseTeeID
        LEFT JOIN UGG_Holes H18 ON H18.CourseID=CT.CourseID AND H18.HoleNumber=18
        LEFT JOIN UGG_HoleTees T18 ON T18.HoleID=H18.HoleID AND T18.CourseTeeID=CT.CourseTeeID
        WHERE CT.CourseID={course_id}
    """
    
    if color:
        query_02 = f"""    AND TC.Color LIKE '{color}'"""
        query = query + query_02
    
    data_list = []
    results = session.execute(query).all()
    for result in results:
        data = tuple(zip(result[19:], result[1:19]))
        key = {"course_tee_id": result[37]}
        data_list.append(CourseDetailsOlv(result[0], data, key))
    return data_list



def get_par_values(session, course_id):
    query = f"""
        SELECT C.CourseID, 
        	H1.Par, H2.Par, H3.Par, H4.Par, H5.Par, H6.Par,
        	H7.Par, H8.Par, H9.Par, H10.Par, H11.Par, H12.Par,
        	H13.Par, H14.Par, H15.Par, H16.Par, H17.Par, H18.Par,
        	H1.HoleID, H2.HoleID, H3.HoleID, H4.HoleID, H5.HoleID, 
            H6.HoleID, H7.HoleID, H8.HoleID, H9.HoleID, H10.HoleID, 
            H11.HoleID, H12.HoleID, H13.HoleID, H14.HoleID, H15.HoleID, 
            H16.HoleID, H17.HoleID, H18.HoleID
        FROM UGG_Courses C 
        LEFT JOIN UGG_Holes H1 ON H1.CourseID=C.CourseID AND H1.HoleNumber=1
        LEFT JOIN UGG_Holes H2 ON H2.CourseID=C.CourseID AND H2.HoleNumber=2
        LEFT JOIN UGG_Holes H3 ON H3.CourseID=C.CourseID AND H3.HoleNumber=3
        LEFT JOIN UGG_Holes H4 ON H4.CourseID=C.CourseID AND H4.HoleNumber=4
        LEFT JOIN UGG_Holes H5 ON H5.CourseID=C.CourseID AND H5.HoleNumber=5
        LEFT JOIN UGG_Holes H6 ON H6.CourseID=C.CourseID AND H6.HoleNumber=6
        LEFT JOIN UGG_Holes H7 ON H7.CourseID=C.CourseID AND H7.HoleNumber=7
        LEFT JOIN UGG_Holes H8 ON H8.CourseID=C.CourseID AND H8.HoleNumber=8
        LEFT JOIN UGG_Holes H9 ON H9.CourseID=C.CourseID AND H9.HoleNumber=9
        LEFT JOIN UGG_Holes H10 ON H10.CourseID=C.CourseID
        	AND H10.HoleNumber=10
        LEFT JOIN UGG_Holes H11 ON H11.CourseID=C.CourseID
        	AND H11.HoleNumber=11
        LEFT JOIN UGG_Holes H12 ON H12.CourseID=C.CourseID
        	AND H12.HoleNumber=12
        LEFT JOIN UGG_Holes H13 ON H13.CourseID=C.CourseID
        	AND H13.HoleNumber=13
        LEFT JOIN UGG_Holes H14 ON H14.CourseID=C.CourseID
        	AND H14.HoleNumber=14
        LEFT JOIN UGG_Holes H15 ON H15.CourseID=C.CourseID
        	AND H15.HoleNumber=15
        LEFT JOIN UGG_Holes H16 ON H16.CourseID=C.CourseID
        	AND H16.HoleNumber=16
        LEFT JOIN UGG_Holes H17 ON H17.CourseID=C.CourseID
        	AND H17.HoleNumber=17
        LEFT JOIN UGG_Holes H18 ON H18.CourseID=C.CourseID
        	AND H18.HoleNumber=18
        WHERE C.CourseID = {course_id}
    """
    results = session.execute(query).all()
    data = tuple(zip(results[0][19:], results[0][1:19]))
    key = {"course_id": course_id}
    return CourseDetailsOlv("Par", data, key)

def get_golfers(session):
    results = session.execute("""
        SELECT IFNULL(LastName||', ', '')||FirstName, GolferID
        FROM UGG_Golfers
        ORDER BY 1
    """).all()
    if results:
        return results
    return []

def get_hole_tee(session, course_tee_id, hole_number):
    results = session.execute(f"""
        SELECT HoleTeeID
        FROM UGG_Holes HS
        JOIN UGG_HoleTees HT ON HT.HoleID=HS.HoleID
        WHERE HS.HoleNumber={hole_number}
        AND HT.CourseTeeID={course_tee_id}
    """).all()
    try:
        return results[0][0]
    except:
        return None
    
def get_tee_colors(session, course_id):
    results = session.execute(f"""
        SELECT TC.TeeColorID, Color
        FROM UGG_TeeColors TC
        LEFT JOIN UGG_CourseTees CT ON CT.TeeColorID=TC.TeeColorID
            AND CourseID={course_id}
        WHERE CT.CourseTeeID IS NULL
    """).all()
    return results
    

def get_player_scores(session, course_id):
    results = session.execute(sql.player_scores(course_id)).all()
    return [CoursePlayerOlv(
        result[0], result[1], result[2], result[3], result[4], result[5]) 
        for result in results]

def get_player_ids(session, round_id):
    results = session.execute(sql.playing_golfer_ids(round_id)).all()
    if results:
        return [result[0] for result in results]
    return []

    
def get_number_of_players(session, round_id=None, default_value=4):
    if round_id:
        query = sql.number_of_players(round_id)
        results = session.execute(query).all()
        if results:
            print(results)
            return results[0][0]
    return default_value

def create_course(session, park_id, course_name, no_of_holes):
    course = UGG_Course(park_id, course_name, no_of_holes)
    session.add(course)
    session.commit()

def create_players(session, round_id, golfer_ids):
    for order, golfer_id in enumerate(golfer_ids):
        results = session.query(
            UGG_Player
        ).filter(
            round_id == UGG_Player.RoundID
        ).filter(
            golfer_id == UGG_Player.GolferID
        ).all()
        if results:
            player = results[0]
            player.Order = order + 1
        else:
            player = UGG_Player(golfer_id, round_id, order + 1)
        session.add(player)
        session.commit()

    
def get_all_rounds(session):
    results = session.execute(sql.all_rounds()).all()
    rounds = []
    for result in results:
        rounds.append(
            RoundOlv(result[0], result[1], result[2], result[3], result[4]))
    return rounds
    

    
# %%

def save_hole_tees(session, course_tee_id, data):
    data = {1: '11', 2: '2', 3: '2', 4: '4', 5: '4', 6: '5', 7: '4', 8: '3', 
            9: '8', 10: '6', 11: '3', 12: '5', 13: '2', 14: '2', 15: '5', 
            16: '3', 17: '5', 18: '6'}
    for hole_number in range(1, 19):
        print(f"Hole # {hole_number}:")
        print(data[hole_number])
        print(get_hole_tee(session, course_tee_id, hole_number))
        print()
        

