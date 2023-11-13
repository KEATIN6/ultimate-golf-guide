# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 08:21:07 2023

@author: pizzacoin
"""

def player_scores(course_id):
    player_scores_query = f"""
        SELECT PlayerID, PLR.RoundID, FirstName, LastName, 
            TotalStrokes, TeeTime
        FROM UGG_Golfers GFR
        JOIN UGG_Players PLR ON PLR.GolferID=GFR.GolferID
        JOIN UGG_Rounds RND ON RND.RoundID=PLR.RoundID
        WHERE CourseID={course_id}
        ORDER BY TotalStrokes DESC
    """
    return player_scores_query


def number_of_players(round_id):
    number_of_players_query = f"""
        SELECT NoOfPlayers
        FROM UGG_Rounds RND
        WHERE RND.RoundID={round_id}
    """
    return number_of_players_query

def playing_golfer_ids(round_id):
    playing_golfer_ids_query = f"""
        SELECT GolferID
        FROM UGG_Players PLR
        WHERE PLR.RoundID={round_id}
    """
    return playing_golfer_ids_query


def all_rounds():
    all_rounds_query = """
        SELECT RND.RoundID, CRS.CourseName, RND.NoOfPlayers, BestScore ,TeeTime
        FROM UGG_Rounds RND 
        JOIN UGG_Courses CRS ON CRS.CourseID=RND.CourseID
        LEFT JOIN (
        	SELECT RoundID, MIN(TotalStrokes)[BestScore]
        	FROM UGG_Players PYR
        	GROUP BY RoundID
        ) PYR ON PYR.RoundID=RND.RoundID
    """
    return all_rounds_query


def players_round(round_id):
    players_round_query = f"""
        SELECT PLY.PlayerID, FirstName, LastName, TotalStrokes, ScoringTerm
        FROM UGG_Players PLY
        JOIN UGG_Golfers GLF ON GLF.GolferID=PLY.GolferID
        LEFT JOIN (
        	SELECT PlayerID, ScoringTerm,
        		ROW_NUMBER()OVER(PARTITION BY SCR.PlayerID ORDER BY STM.ScoringTermID)[ScoreRow]
        	FROM UGG_Scores SCR
        	JOIN UGG_ScoringTerms STM ON STM.ScoringTermID=SCR.ScoringTermID
        ) SCR ON SCR.ScoreRow=1 AND SCR.PlayerID=PLY.PlayerID
        WHERE PLY.RoundID={round_id}
    """
    return players_round_query
