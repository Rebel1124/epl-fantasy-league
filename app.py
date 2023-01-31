# Initial imports
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import numpy as np
import random
#import datetime as dt
from pathlib import Path
import math
import os
from scipy.stats import poisson,skellam
import statistics
from statistics import mode
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
#from datetime import date, timedelta
import streamlit as st
from PIL import Image
import re
#import time

from dotenv import load_dotenv
import json
from dataclasses import dataclass
from typing import Any, List
from web3 import Web3

from wallet_functions import generate_account, get_balance, send_transaction

import warnings

warnings.filterwarnings("ignore")

# App Inputs for user selection
games=6
targTeam = 'Man United'
teama = 'Man United'
teamb = 'Liverpool'
graph_value= 'Points'


# User selection menus
teams = ['Arsenal',
         'Aston Villa',
         'Bournemouth',
         'Brentford',
         'Brighton',
         'Chelsea',
         'Crystal Palace',
         'Everton',
         'Fulham',
         'Leeds',
         'Leicester',
         'Liverpool',
         'Man City',
         'Man United',
         'Newcastle',
         "Nott'm Forest",
         'Southampton',
         'Tottenham',
         'West Ham',
         'Wolves']



graph_options = ['Won', 'Draw', 'Lost', 'Goals For', 'Goals Against', 'Shots For', 'Shots Against', 'T-Shots For','T-Shots Against', 'Points']

banner2 = Image.open('football_logo/banner2.jpg')
st.image(banner2, width=707)
st.markdown(" ")

load_dotenv()
    
# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))
#w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))


####### Functions to import data and plot graphs and tables ###################################################################################

@st.cache(allow_output_mutation=True)
def data(file):
    df = pd.read_csv(file)
    return df

seasons = data("Processed_Data/seasons.csv")
team_merge = data("Processed_Data/team_merge.csv")
merged_stats = data("Processed_Data/merged_stats.csv")
elements = data("FPL_Data/elements.csv")
history = data("FPL_Data/all_history_df_current.csv")



#@st.cache(allow_output_mutation=True)
def changeName(position):
    if(position == 'Goalkeeper'):
        return 'a'
    elif(position == 'Defender'):
        return 'b'
    elif(position == 'Midfielder'):
        return 'c'
    else:
        return 'd'


elements['positionName'] = elements['position'].apply(changeName)

def colorScale(x):
    if (x == 'platin'):
        return 'grey'
    elif (cati == 'gold'):
        return 'darkgoldenrod'
    elif (cati == 'silver'):
        return 'darkgrey'
    else:
        return 'burlywood'


## Simulate match using Poisson Distribution Model
@st.cache(allow_output_mutation=True)
def simulate_match(home_goals_avg, away_goals_avg, max_goals=10):
    team_pred = [[poisson.pmf(i, team_avg) for i in range(0, max_goals+1)] for team_avg in [home_goals_avg, away_goals_avg]]
    return(np.outer(np.array(team_pred[0]), np.array(team_pred[1])))


@st.cache(allow_output_mutation=True)
def matchProb(homePower, awayPower):
    matrix = simulate_match(homePower,awayPower)
    probHomeWin = np.sum(np.tril(matrix, -1))
    probDraw = np.sum(np.diag(matrix))
    probAwayWin = np.sum(np.triu(matrix, 1))
    
    results = [probHomeWin, probDraw, probAwayWin]
    return results



@st.cache(allow_output_mutation=True)
def tables(team, previousGames, targetTeam):
    
    team = team[-previousGames:]
    
    results =[]
    colours = []
    
    for i in range(0, previousGames):
        if((team['HomeTeam'].iloc[i] == targetTeam) & (team['FTR'].iloc[i] == 'H')):
            results.append('Won')
            colours.append('#98FB98')
        elif((team['AwayTeam'].iloc[i] == targetTeam) & (team['FTR'].iloc[i] == 'A')):
            results.append('Won')
            colours.append('#98FB98')
        elif((team['FTR'].iloc[i] == 'D')):
            results.append('Draw')
            colours.append('#E3CF57')
        else:
            results.append('Lost')
            colours.append('#F08080')

    
    
    head = ['<b>Date<b>', '<b>HomeTeam<b>', '<b>AwayTeam<b>', '<b>FTHG<b>', '<b>FTAG<b>', '<b>HS<b>','<b>AS<b>','<b>HST<b>',
            '<b>AST<b>','<b>FTR<b>', '<b>Result<b>']
    labels = []
    date = team['gameDate'].tolist()
    hTeam = team['HomeTeam'].tolist()
    aTeam = team['AwayTeam'].tolist()
    hg = team['FTHG'].tolist()
    ag = team['FTAG'].tolist()
    hs = team['HS'].tolist()
    ash = team['AS'].tolist()
    hst = team['HST'].tolist()
    ast = team['AST'].tolist()
    res = team['FTR'].tolist()
    
    fig = go.Figure(data=[go.Table(
        columnorder = [1,2,3,4,5,6,7,8,9,10,11],
        columnwidth = [60,80,80,35,35,35,35,35,35,35,35],
        header=dict(values=head,
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[date, hTeam, aTeam, hg, ag, hs, ash, hst, ast, res, results],
                   fill_color=[['lavender'], ['lavender'],['lavender'],['lavender'],['lavender'],['lavender'],
                               ['lavender'],['lavender'],['lavender'],['lavender'], colours],
                   align='left'))
    ])
    

    fig.update_layout(height=(25*games), width=700, margin=dict(l=0, r=0, b=0,t=0))
    
    return fig




@st.cache(allow_output_mutation=True)
def teamTables(teamiFPL):
    
    teamiFPL['strength'] = teamiFPL.apply(lambda x: round((x['strength']),2), axis=1)
    
    name = teamiFPL['web_name'].tolist()
    position = teamiFPL['position'].tolist()
    status = teamiFPL['statusFull'].tolist()
    strength = teamiFPL['strength'].tolist()
    category = teamiFPL['str-cat'].tolist()
    
    
    head = ['Name', 'Pos', 'Status', 'Score', 'Cat']
    
    count = len(name)
    
    fig = go.Figure(data=[go.Table(
        
        columnorder = [1,2,3,4,5],
        columnwidth = [58,52,35, 35, 35],
        
        header=dict(values=head,
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[name, position, status, strength, category],
                   fill_color='lavender',
                   align='left'))
    ])   

    fig.update_layout(height=(count*25), width=300, margin=dict(l=0, r=0, b=0,t=0))
    
    return fig



@st.cache(allow_output_mutation=True)
def playerTables(filter):
      
    name = filter['web_name'].tolist()
    position = filter['position'].tolist()
    cost = filter['now_cost'].tolist()
    sel = filter['selected_by_percent'].tolist()
    minutes = filter['minutes'].tolist()
    goals = filter['goals_scored'].tolist()
    assists = filter['assists'].tolist()
    saves = filter['saves'].tolist()
    form = filter['form'].tolist()
    pts = filter['total_points'].tolist()
    bps = filter['bps'].tolist()
    ict_index = filter['ict_index'].tolist()
    
    head = ['Name', 'Pos', 'Cost', 'Pick', 'Min', 'Goals', 'Assists', 'Saves', 'Form', 'Points', 'Bonus', 'ICT']
    
    count = len(name)
    
    fig = go.Figure(data=[go.Table(
        
        columnorder = [1,2,3,4,5,6,7,8,9,10,11,12],
        columnwidth = [70,50,30,30,30,30,30,30,30,30,30,30],
        
        header=dict(values=head,
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[name, position, cost, sel, minutes, goals, assists, saves, form, pts, bps, ict_index],
                   fill_color='lavender',
                   align='left'))
    ])   

    fig.update_layout(height=(count*22), width=710, margin=dict(l=0, r=0, b=0,t=0))
    
    return fig




@st.cache(allow_output_mutation=True)
def playerStatistics(playerGames, games):
    
    playerGames = playerGames[-games:]
    
    
    
    date = playerGames['Date'].tolist()
    opponent = playerGames['opponent'].tolist()
    minutes = playerGames['minutes'].tolist()
    goals= playerGames['goals_scored'].tolist()
    assists = playerGames['assists'].tolist()
    saves = playerGames['saves'].tolist()
    pts = playerGames['total_points'].tolist()
    bps = playerGames['bps'].tolist()
    inf = playerGames['influence'].tolist()
    cre = playerGames['creativity'].tolist()
    thr = playerGames['threat'].tolist()
    ict_index = playerGames['ict_index'].tolist()
    
    head = ['Date', 'Opp', 'Min', 'Goals', 'Assists', 'Saves', 'Points', 'Bonus', 'Influence', 'Create', 'Threat', 'ICT']
    
    
    fig22 = go.Figure(data=[go.Table(
        
        columnorder = [1,2,3,4,5,6,7,8,9,10,11,12],
        columnwidth = [55,55,20,25,25,25,25,25,30,25,25,25],
        
        header=dict(values=head,
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[date, opponent, minutes, goals, assists, saves, pts, bps, inf, cre, thr, ict_index],
                   fill_color='lavender',
                   align='left'))
    ])   

    fig22.update_layout(height=(games*25), width=710, margin=dict(l=0, r=0, b=0,t=0))
    
    return fig22


@st.cache(allow_output_mutation=True)
def stats(homeTeam, target, games, graph, num):
    
    homeTeam = homeTeam[-games:]

    homewon = 0
    homedraw = 0
    homelost = 0
    homegoalsfor = 0
    homegoalsagainst = 0
    
    homeshotsfor = 0
    homeshotsagainst = 0
    homeshotsTargetfor = 0
    homeshotsTargetagainst = 0
    
    homepoints = 0
    
    awaywon = 0
    awaydraw = 0
    awaylost = 0
    awaygoalsfor = 0
    awaygoalsagainst = 0
    
    awayshotsfor = 0
    awayshotsagainst = 0
    awayshotsTargetfor = 0
    awayshotsTargetagainst = 0
    
    awaypoints = 0
    
    lenth = homeTeam.shape[0]
    
    for i in range(0, lenth):
        if (homeTeam['HomeTeam'].iloc[i] == target):
            
            homegoalsfor += homeTeam['FTHG'].iloc[i]
            homegoalsagainst += homeTeam['FTAG'].iloc[i]
            
            homeshotsfor += homeTeam['HS'].iloc[i]
            homeshotsagainst += homeTeam['AS'].iloc[i]
            homeshotsTargetfor += homeTeam['HST'].iloc[i]
            homeshotsTargetagainst += homeTeam['AST'].iloc[i]
            
            
            
            if(homeTeam['FTR'].iloc[i] == 'H'):
                homewon += 1
                homepoints += 3
            elif(homeTeam['FTR'].iloc[i]=='D'):
                homedraw += 1
                homepoints += 1
            else:
                homelost += 1
                homepoints += 0
                
        else:
            awaygoalsfor += homeTeam['FTAG'].iloc[i]
            awaygoalsagainst += homeTeam['FTHG'].iloc[i]
            
            awayshotsfor += homeTeam['AS'].iloc[i]
            awayshotsagainst += homeTeam['HS'].iloc[i]
            awayshotsTargetfor += homeTeam['AST'].iloc[i]
            awayshotsTargetagainst += homeTeam['HST'].iloc[i]
            
            
            
            if(homeTeam['FTR'].iloc[i] == 'A'):
                awaywon += 1
                awaypoints += 3
            elif(homeTeam['FTR'].iloc[i]=='D'):
                awaydraw += 1
                awaypoints += 1
            else:
                awaylost += 1
                awaypoints += 0
                
            
    Won = homewon + awaywon
    Draw = homedraw + awaydraw
    Lost = homelost + awaylost
    GoalsFor = homegoalsfor + awaygoalsfor
    GoalsAgainst = homegoalsagainst + awaygoalsagainst
    
    ShotsFor = homeshotsfor + awayshotsfor
    ShotsAgainst = homeshotsagainst + awayshotsagainst
    targetShotsFor = homeshotsTargetfor + awayshotsTargetfor
    targetShotsAgainst = homeshotsTargetagainst + awayshotsTargetagainst
    
    
    Points = homepoints + awaypoints


    home = [homewon, homedraw, homelost, homegoalsfor, homegoalsagainst, homeshotsfor, homeshotsagainst,
            homeshotsTargetfor, homeshotsTargetagainst, homepoints]
    away = [awaywon, awaydraw, awaylost, awaygoalsfor, awaygoalsagainst, awayshotsfor, awayshotsagainst,
            awayshotsTargetfor, awayshotsTargetagainst, awaypoints]
    total = [Won, Draw, Lost, GoalsFor, GoalsAgainst, ShotsFor, ShotsAgainst, targetShotsFor, targetShotsAgainst, Points]
    
    
    head = ['<b>Statistic<b>', '<b>Home<b>', '<b>Away<b>', '<b>Total<b>']
    labels = ['Won', 'Draw', 'Lost', 'Goals For', 'Goals Against', 'Shots For', 'Shots Against', 'T-Shots For','T-Shots Against', 'Points']
    
    index = labels.index(graph)
    
    fig = go.Figure(data=[go.Table(
        
        columnorder = [1,2,3,4],
        columnwidth = [60,40,40,40],
        
        header=dict(values=head,
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[labels, home, away, total],
                   fill_color='lavender',
                   align='left'))
    ])   

    fig.update_layout(height=230, width=630, margin=dict(l=0, r=0, b=0,t=0))
    
    figx = go.Figure()
    
    figx.add_trace(
        go.Bar(
            x=['Home', 'Away', 'Total'],
            y=[home[index], away[index], total[index]],
            name=graph,
            text=[home[index], away[index], total[index]],
            textposition='auto'
        )
    )
    
    
    if (num==1):
         figx.update_traces(marker_color='rgb(255,185,15)', marker_line_color='rgb(205,149,12)', marker_line_width=1.5, opacity=0.6, texttemplate='%{text:.0f}')
    elif(num==2):
        figx.update_traces(marker_color='rgb(238,0,0)', marker_line_color='rgb(139,0,0)', marker_line_width=1.5, opacity=0.6, texttemplate='%{text:.0f}')
    else:
        figx.update_traces(marker_color='RGB(255,131,250)', marker_line_color='RGB(205,105,201)', marker_line_width=1.5, opacity=0.6, texttemplate='%{text:.0f}')
    
    figx.update_layout(
        xaxis=dict(autorange=True, title_text='Ground', title_font={"size": 10}, tickfont={"size":10}),
        yaxis=dict(autorange=True, title_text=graph, title_font={"size": 10}, tickfont={"size":10}),
        height=230,
        width=630,
        margin=dict(l=0, r=0, b=0,t=0),
        plot_bgcolor='rgb(255,255,255)',
    )
    
    graphs = [fig, figx]
    
    return graphs


#Function to display FPL team data
@st.cache(allow_output_mutation=True)
def teamFpl(elements, team):
    
    
    df = elements.loc[(elements['team'] == team)]
    df = df.sort_values(by=['positionName', 'bps_per_90'], ascending=True)
    
    df = df[['web_name', 'position', 'statusFull', 'strength', 'str-cat']]
      
    return df


# Function to calculate the Probability
@st.cache(allow_output_mutation=True)
def Probability(rating1, rating2):
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))


# Function to get team lineups
@st.cache(allow_output_mutation=True)
def lineup(elements, team):

    df = elements.loc[(elements['team'] == team) & (elements['statusFull'] == 'avail')]
    df = df.sort_values(by=['minutes', 'strength'], ascending=False)
    squad = df['web_name'].values
    lineup = squad[0:11]
    
    return lineup



# Function for points
@st.cache(allow_output_mutation=True)
def teamStrength(elements, team, line):
    
    df = elements.loc[(elements['team'] == team)]
    df = df.sort_values(by=['minutes', 'strength'], ascending=False)
    df = df[['web_name', 'strength']]
    filter1 = df.loc[(df['web_name'].isin(line))]
    
    score = filter1['strength'].sum()
    
    return score


@st.cache(allow_output_mutation=True)
def filterElements(elements, team):
    
    df = elements.loc[(elements['team'] == team)]
    df = df.sort_values(by=['positionName'], ascending=True)
    df = df[['web_name', 'position', 'now_cost', 'selected_by_percent', 'minutes', 'goals_scored', 'assists', 'saves', 'form', 
             'total_points', 'bps', 'ict_index']]
    return df


@st.cache(allow_output_mutation=True)
def filterPlayer(history, name):
    
    df = history.loc[(history['name'] == name)]
    df = df[['Date', 'opponent', 'minutes', 'goals_scored', 'assists', 'saves', 'total_points', 'bps', 'influence', 'creativity', 'threat', 'ict_index']]
    return df



@st.cache(allow_output_mutation=True)
def filterNames(elements, team):
    
    df = elements.loc[(elements['team'] == team)]
    df = df.sort_values(by=['positionName'], ascending=True)
    playerNames = df['web_name'].unique()
    
    return playerNames



@st.cache(allow_output_mutation=True)
def statshead2head(Teams, teama, teamb, games, graph):
    
    Teams = Teams[-games:]
    
    team1won = 0
    team1draw = 0
    team1lost = 0
    team1goalsfor = 0
    team1goalsagainst = 0
    
    team1shotsfor = 0
    team1shotsagainst = 0
    team1shotsTargetfor = 0
    team1shotsTargetagainst = 0
    
    team1points = 0
    
    team2won = 0
    team2draw = 0
    team2lost = 0
    team2goalsfor = 0
    team2goalsagainst = 0
    
    team2shotsfor = 0
    team2shotsagainst = 0
    team2shotsTargetfor = 0
    team2shotsTargetagainst = 0
    
    
    team2points = 0
    
    legth = Teams.shape[0]
    
    for i in range(0, legth):
        if (Teams['HomeTeam'].iloc[i] == teama):
            team1goalsfor += Teams['FTHG'].iloc[i]
            team1goalsagainst += Teams['FTAG'].iloc[i]
            
            team1shotsfor = Teams['HS'].iloc[i]
            team1shotsagainst = Teams['AS'].iloc[i]
            team1shotsTargetfor = Teams['HST'].iloc[i]
            team1shotsTargetagainst = Teams['AST'].iloc[i]
            
            if(Teams['FTR'].iloc[i] == 'H'):
                team1won += 1
                team1points += 3
            elif(Teams['FTR'].iloc[i] == 'D'):
                team1draw += 1
                team1points += 1
            else:
                team1lost += 1
                team1points += 0
                
        elif (Teams['AwayTeam'].iloc[i] == teama):
            team1goalsfor += Teams['FTAG'].iloc[i]
            team1goalsagainst += Teams['FTHG'].iloc[i]
            
            
            team1shotsfor = Teams['AS'].iloc[i]
            team1shotsagainst = Teams['HS'].iloc[i]
            team1shotsTargetfor = Teams['AST'].iloc[i]
            team1shotsTargetagainst = Teams['HST'].iloc[i]
            
            
            if(Teams['FTR'].iloc[i] == 'A'):
                team1won += 1
                team1points += 3
            elif(Teams['FTR'].iloc[i] == 'D'):
                team1draw += 1
                team1points += 1
            else:
                team1lost += 1
                team1points += 0
                
        if (Teams['HomeTeam'].iloc[i] == teamb):
            team2goalsfor += Teams['FTHG'].iloc[i]
            team2goalsagainst += Teams['FTAG'].iloc[i]
            
            team2shotsfor = Teams['HS'].iloc[i]
            team2shotsagainst = Teams['AS'].iloc[i]
            team2shotsTargetfor = Teams['HST'].iloc[i]
            team2shotsTargetagainst = Teams['AST'].iloc[i]
            
            if(Teams['FTR'].iloc[i] == 'H'):
                team2won += 1
                team2points += 3
            elif(Teams['FTR'].iloc[i] == 'D'):
                team2draw += 1
                team2points += 1
            else:
                team2lost += 1
                team2points += 0
                
                
        elif (Teams['AwayTeam'].iloc[i] == teamb):
            team2goalsfor += Teams['FTAG'].iloc[i]
            team2goalsagainst += Teams['FTHG'].iloc[i]
            
            team2shotsfor = Teams['AS'].iloc[i]
            team2shotsagainst = Teams['HS'].iloc[i]
            team2shotsTargetfor = Teams['AST'].iloc[i]
            team2shotsTargetagainst = Teams['HST'].iloc[i]
            
            if(Teams['FTR'].iloc[i] == 'A'):
                team2won += 1
                team2points += 3
            elif(Teams['FTR'].iloc[i] == 'D'):
                team2draw += 1
                team2points += 1
            else:
                team2lost += 1
                team2points += 0
                             
    team1 = [team1won, team1draw, team1lost, team1goalsfor, team1goalsagainst, team1shotsfor,
             team1shotsagainst, team1shotsTargetfor, team1shotsTargetagainst, team1points]
    team2 = [team2won, team2draw, team2lost, team2goalsfor, team2goalsagainst, team2shotsfor,
             team2shotsagainst, team2shotsTargetfor, team2shotsTargetagainst, team2points]          
              
    head = ['<b>Statistic<b>', '<b>'+teama+'<b>', '<b>'+teamb+'<b>']
    labels = ['Won', 'Draw', 'Lost', 'Goals For', 'Goals Against', 'Shots For', 'Shots Against',
              'T-Shots For', 'T-Shots Against','Points']
    
    index = labels.index(graph)
    
    fig = go.Figure(data=[go.Table(
        header=dict(values=head,
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[labels, team1, team2],
                   fill_color='lavender',
                   align='left'))
    ])   

    fig.update_layout(height=230, width=630, margin=dict(l=0, r=0, b=0,t=0))
    
    
    figx = go.Figure()
    
    figx.add_trace(
        go.Bar(
            x=[teama, teamb],
            y=[team1[index], team2[index]],
            name=graph,
            text=[team1[index], team2[index]],
            textposition='auto'
        )
    )
    
    figx.update_traces(marker_color='RGB(255,106,106)', marker_line_color='RGB(205,85,85)', marker_line_width=1.5, opacity=0.6, texttemplate='%{text:.0f}')
    
    figx.update_layout(
        xaxis=dict(title_text='Team', title_font={"size": 10}, tickfont={"size":10}),
        yaxis=dict(title_text=graph, title_font={"size": 10}, tickfont={"size":10}),
        width=630,
        height=230,
        margin=dict(l=0, r=0, b=0,t=0),
        plot_bgcolor='rgb(255,255,255)',
    )
    
    graphs = [fig, figx]
    
    return graphs


def playerRank(elements, category, model):
    
    if(model == 'zScore'):
        df = elements.loc[(elements['str-cat'] == category)]
    elif(model == 'kMeans'):
        df = elements.loc[(elements['kMeans-cat'] == category)]
    else:
        df = elements.loc[(elements['pcaKMeans-cat'] == category)]
       
    df = df.sort_values(by=['strength'], ascending=False)
    
    df = df[['web_name', 'teamName', 'position', 'now_cost', 'form', 'points_per_game', 'bps_per_90', 'ict_index_per_90', 'value_season', 
             'value_bps', 'ict_index_value', 'strength', 'str-cat', 'kMeans-cat', 'pcaKMeans-cat', 'description']]
    return df


@st.cache(allow_output_mutation=True)
def playerRankTables(filter):
   
    
    name = filter['web_name'].tolist()
    team = filter['teamName'].tolist()
    pos = filter['position'].tolist()
    cost = filter['now_cost'].tolist()
    form = filter['form'].tolist()
    ppg = filter['points_per_game'].tolist()
    bpspg = filter['bps_per_90'].tolist()
    ictpg = filter['ict_index_per_90'].tolist()
    ppc = filter['value_season'].tolist()
    bpspc = filter['value_bps'].tolist()
    ictpc = filter['ict_index_value'].tolist()
    score1 = filter['strength'].tolist()
    
    score = []
    
    for i in score1:
        score.append(round(float(i),2))
    
    
    head = ['Name', 'Team', 'Pos', 'Cost', 'Form', 'Pts/Game', 'Bps/Game', 'ICT/Game', 'Pts/Cost', 'Bps/Cost', 'ICT/Cost', 'Score']
    
    count = len(name)
    
    fig = go.Figure(data=[go.Table(
        
        columnorder = [1,2,3,4,5,6,7,8,9,10,11,12],
        columnwidth = [60,60,42,25,25,30,30,30,30,30,30,30],
        
        header=dict(values=head,
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[name, team, pos, cost, form, ppg, bpspg, ictpg, ppc, bpspc, ictpc, score],
                   fill_color='lavender',
                   align='left'))
    ])   

    fig.update_layout(height=(count*25), width=710, margin=dict(l=0, r=0, b=0,t=0))
    
    return fig


@st.cache(allow_output_mutation=True)
def playerScatter(data):

    fig = go.Figure(data=go.Scatter(x=data['now_cost'],
                                    y=data['strength'],
                                    mode='markers',
                                    marker_color=colors,
                                    text=data['description'])) # hover text goes here

    
    fig.update_layout(
    xaxis=dict(autorange=True, title_text='Cost', title_font={"size": 14}, tickfont={"size":10}),
    yaxis=dict(autorange=True, title_text='Strength', title_font={"size": 14}, tickfont={"size":10}),
    height=230,
    width=630,
    margin=dict(l=0, r=0, b=0,t=0),
    plot_bgcolor='rgb(255,255,255)',
    )
    
    
    return fig


@st.cache(allow_output_mutation=True)
def playerScatterAll(data, model):   
    
    if (model == 'zScore'):
        
        x0 = data['now_cost'].loc[(data['str-cat'] == 'bronze')]
        x1 = data['now_cost'].loc[(data['str-cat'] == 'silver')]
        x2 = data['now_cost'].loc[(data['str-cat'] == 'gold')]
        x3 = data['now_cost'].loc[(data['str-cat'] == 'platin')]
        
        y0 = data['strength'].loc[(data['str-cat'] == 'bronze')]
        y1 = data['strength'].loc[(data['str-cat'] == 'silver')]
        y2 = data['strength'].loc[(data['str-cat'] == 'gold')]
        y3 = data['strength'].loc[(data['str-cat'] == 'platin')]
        
        d0 = data['description'].loc[(data['str-cat'] == 'bronze')]
        d1 = data['description'].loc[(data['str-cat'] == 'silver')]
        d2 = data['description'].loc[(data['str-cat'] == 'gold')]
        d3 = data['description'].loc[(data['str-cat'] == 'platin')]
        

    elif (model == 'kMeans'):
        
        x0 = data['now_cost'].loc[(data['kMeans-cat'] == 'bronze')]
        x1 = data['now_cost'].loc[(data['kMeans-cat'] == 'silver')]
        x2 = data['now_cost'].loc[(data['kMeans-cat'] == 'gold')]
        x3 = data['now_cost'].loc[(data['kMeans-cat'] == 'platin')]
        
        y0 = data['strength'].loc[(data['kMeans-cat'] == 'bronze')]
        y1 = data['strength'].loc[(data['kMeans-cat'] == 'silver')]
        y2 = data['strength'].loc[(data['kMeans-cat'] == 'gold')]
        y3 = data['strength'].loc[(data['kMeans-cat'] == 'platin')]
        
        d0 = data['description'].loc[(data['kMeans-cat'] == 'bronze')]
        d1 = data['description'].loc[(data['kMeans-cat'] == 'silver')]
        d2 = data['description'].loc[(data['kMeans-cat'] == 'gold')]
        d3 = data['description'].loc[(data['kMeans-cat'] == 'platin')]

    else:
        x0 = data['now_cost'].loc[(data['pcaKMeans-cat'] == 'bronze')]
        x1 = data['now_cost'].loc[(data['pcaKMeans-cat'] == 'silver')]
        x2 = data['now_cost'].loc[(data['pcaKMeans-cat'] == 'gold')]
        x3 = data['now_cost'].loc[(data['pcaKMeans-cat'] == 'platin')]
        
        y0 = data['strength'].loc[(data['pcaKMeans-cat'] == 'bronze')]
        y1 = data['strength'].loc[(data['pcaKMeans-cat'] == 'silver')]
        y2 = data['strength'].loc[(data['pcaKMeans-cat'] == 'gold')]
        y3 = data['strength'].loc[(data['pcaKMeans-cat'] == 'platin')]
        
        d0 = data['description'].loc[(data['pcaKMeans-cat'] == 'bronze')]
        d1 = data['description'].loc[(data['pcaKMeans-cat'] == 'silver')]
        d2 = data['description'].loc[(data['pcaKMeans-cat'] == 'gold')]
        d3 = data['description'].loc[(data['pcaKMeans-cat'] == 'platin')]
     
        
    fig = go.Figure()

    # Add traces
    fig.add_trace(go.Scatter(x=x0, y=y0,
                        mode='markers',
                        marker_color='burlywood',
                        name='bronze',
                        text=d0))
    fig.add_trace(go.Scatter(x=x1, y=y1,
                    mode='markers',
                    marker_color='darkgrey',
                    name='silver',
                    text=d1))
    
    fig.add_trace(go.Scatter(x=x2, y=y2,
                mode='markers',
                marker_color='darkgoldenrod',
                name='gold',
                text=d2))

    fig.add_trace(go.Scatter(x=x3, y=y3,
                mode='markers',
                marker_color='grey',
                name='platin',
                text=d3))
    
    fig.update_layout(
    xaxis=dict(autorange=True, title_text='Cost', title_font={"size": 14}, tickfont={"size":10}),
    yaxis=dict(autorange=True, title_text='Strength', title_font={"size": 14}, tickfont={"size":10}),
    height=230,
    width=630,
    margin=dict(l=0, r=0, b=0,t=0),
    plot_bgcolor='rgb(255,255,255)',
    )
    
    
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="left",
        x=-0.04
    ))
    
    
    return fig



@st.cache(allow_output_mutation=True)
def averageScatter(data, model):   
    
    
    if (model == 'zScore'):
        
        Bronze = data.loc[(data['str-cat'] == 'bronze')]
        BronzeCount = Bronze['strength'].count()
        Bronzev1 = Bronze.loc[(data['strength'] > 0)]
        BronzeAvg = round(Bronzev1['strength'].mean(),2)
        BronzeCost = round(Bronzev1['now_cost'].mean(),2)

        Silver = data.loc[(data['str-cat'] == 'silver')]
        SilverCount = Silver['strength'].count()
        SilverAvg = round(Silver['strength'].mean(),2)
        SilverCost = round(Silver['now_cost'].mean(),2)
        
        Gold = data.loc[(data['str-cat'] == 'gold')]
        GoldCount = Gold['strength'].count()
        GoldAvg = round(Gold['strength'].mean(),2)
        GoldCost = round(Gold['now_cost'].mean(),2)

        Platin = data.loc[(data['str-cat'] == 'platin')]
        PlatinCount = Platin['strength'].count()
        PlatinAvg = round(Platin['strength'].mean(),2)
        PlatinCost = round(Platin['now_cost'].mean(),2)


    elif (model == 'kMeans'):
        
        Bronze = data.loc[(data['kMeans-cat'] == 'bronze')]
        BronzeCount = Bronze['strength'].count()
        Bronzev1 = Bronze.loc[(data['strength'] > 0)]
        BronzeAvg = round(Bronzev1['strength'].mean(),2)
        BronzeCost = round(Bronzev1['now_cost'].mean(),2)

        Silver = data.loc[(data['kMeans-cat'] == 'silver')]
        SilverCount = Silver['strength'].count()
        SilverAvg = round(Silver['strength'].mean(),2)
        SilverCost = round(Silver['now_cost'].mean(),2)
        
        Gold = data.loc[(data['kMeans-cat'] == 'gold')]
        GoldCount = Gold['strength'].count()
        GoldAvg = round(Gold['strength'].mean(),2)
        GoldCost = round(Gold['now_cost'].mean(),2)

        Platin = data.loc[(data['kMeans-cat'] == 'platin')]
        PlatinCount = Platin['strength'].count()
        PlatinAvg = round(Platin['strength'].mean(),2)
        PlatinCost = round(Platin['now_cost'].mean(),2)

    else:
        
        Bronze = data.loc[(data['pcaKMeans-cat'] == 'bronze')]
        BronzeCount = Bronze['strength'].count()
        Bronzev1 = Bronze.loc[(data['strength'] > 0)]
        BronzeAvg = round(Bronzev1['strength'].mean(),2)
        BronzeCost = round(Bronzev1['now_cost'].mean(),2)

        Silver = data.loc[(data['pcaKMeans-cat'] == 'silver')]
        SilverCount = Silver['strength'].count()
        SilverAvg = round(Silver['strength'].mean(),2)
        SilverCost = round(Silver['now_cost'].mean(),2)
        
        Gold = data.loc[(data['pcaKMeans-cat'] == 'gold')]
        GoldCount = Gold['strength'].count()
        GoldAvg = round(Gold['strength'].mean(),2)
        GoldCost = round(Gold['now_cost'].mean(),2)

        Platin = data.loc[(data['pcaKMeans-cat'] == 'platin')]
        PlatinCount = Platin['strength'].count()
        PlatinAvg = round(Platin['strength'].mean(),2)
        PlatinCost = round(Platin['now_cost'].mean(),2)
     
        
    fig = go.Figure()

    # Add traces
    fig.add_trace(go.Scatter(x=[BronzeCost], y=[BronzeAvg],
                        mode='markers',
                        marker_color='burlywood',
                        marker_size=[BronzeCount],
                        name='bronze',
                        text=[BronzeCount]
                        ))
    fig.add_trace(go.Scatter(x=[SilverCost], y=[SilverAvg],
                    mode='markers',
                    marker_color='darkgrey',
                    marker_size=[SilverCount],
                    name='silver',
                    text=[SilverCount]
                    ))
    
    fig.add_trace(go.Scatter(x=[GoldCost], y=[GoldAvg],
                mode='markers',
                marker_color='darkgoldenrod',
                marker_size=[GoldCount],
                name='gold',
                text=[GoldCount]
                ))

    fig.add_trace(go.Scatter(x=[PlatinCost], y=[PlatinAvg],
                mode='markers',
                marker_color='grey',
                marker_size=[PlatinCount],
                name='platin',
                text=[PlatinCount]
                ))
    
    fig.update_layout(
    xaxis=dict(autorange=True, title_text='Cost', title_font={"size": 14}, tickfont={"size":10}),
    yaxis=dict(autorange=True, title_text='Strength', title_font={"size": 14}, tickfont={"size":10}),
    height=550,
    width=630,
    margin=dict(l=0, r=0, b=0,t=0),
    plot_bgcolor='rgb(255,255,255)',
    )
    
    
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.1,
        xanchor="left",
        x=-0.04
    ))
    
    
    return fig


@st.cache(allow_output_mutation=True)
def teamScores(data, teams):   
    
    scoresList = []
    count = len(teams)

    for i in teams:
        teamlineup = lineup(data, i)
        teamscore = round(teamStrength(data, i, teamlineup),2)
        scoresList.append(teamscore)
        
    fig = go.Figure()

    # Add traces
    
    for i in range(0, count):
        fig.add_trace(go.Scatter(x=[teams[i]], y=[scoresList[i]],
                            mode='markers',
                            marker_color=px.colors.qualitative.Light24[i],
                            marker_size=[20],
                            name=teams[i],
                            ))

    fig.update_layout(
    xaxis=dict(autorange=True, title_text='Teams', title_font={"size": 14}, tickfont={"size":10}),
    yaxis=dict(autorange=True, title_text='Strength', title_font={"size": 14}, tickfont={"size":10}),
    height=550,
    width=630,
    margin=dict(l=0, r=0, b=0,t=0),
    plot_bgcolor='rgb(255,255,255)',
    )
    
   
    fig.update_layout(legend=dict(
        title="Teams",
    ))
    
    
    return fig


@st.cache(allow_output_mutation=True)
def teamScoresList(data, teams):   
    
    scoresList = []
    count = len(teams)

    for i in teams:
        teamlineup = lineup(data, i)
        teamscore = round(teamStrength(data, i, teamlineup),2)
        scoresList.append(teamscore)
        
    return scoresList



@st.cache(allow_output_mutation=True)
def targetTeamScatter(data, targetTeam):   
    
    data = data.loc[(data['team'] == targetTeam)]
    
            
    x0 = data['now_cost'].loc[(data['str-cat'] == 'bronze')]
    x1 = data['now_cost'].loc[(data['str-cat'] == 'silver')]
    x2 = data['now_cost'].loc[(data['str-cat'] == 'gold')]
    x3 = data['now_cost'].loc[(data['str-cat'] == 'platin')]
    
    y0 = data['strength'].loc[(data['str-cat'] == 'bronze')]
    y1 = data['strength'].loc[(data['str-cat'] == 'silver')]
    y2 = data['strength'].loc[(data['str-cat'] == 'gold')]
    y3 = data['strength'].loc[(data['str-cat'] == 'platin')]
    
    d0 = data['description'].loc[(data['str-cat'] == 'bronze')]
    d1 = data['description'].loc[(data['str-cat'] == 'silver')]
    d2 = data['description'].loc[(data['str-cat'] == 'gold')]
    d3 = data['description'].loc[(data['str-cat'] == 'platin')]
    
    countBronze = len(x0)
    countSilver = len(x1)
    countGold = len(x2)
    countPlatin = len(x3)
        
        
    fig = go.Figure()

    # Add traces
    if(countBronze > 0):
        fig.add_trace(go.Scatter(x=x0, y=y0,
                            mode='markers',
                            marker_color='burlywood',
                            name='bronze',
                            text=d0))
    
    if(countSilver > 0):
        fig.add_trace(go.Scatter(x=x1, y=y1,
                        mode='markers',
                        marker_color='darkgrey',
                        name='silver',
                        text=d1))
    if(countGold > 0):
        fig.add_trace(go.Scatter(x=x2, y=y2,
                    mode='markers',
                    marker_color='darkgoldenrod',
                    name='gold',
                    text=d2))
    if(countPlatin > 0):
        fig.add_trace(go.Scatter(x=x3, y=y3,
                    mode='markers',
                    marker_color='grey',
                    name='platin',
                    text=d3))
    
    fig.update_layout(
    xaxis=dict(autorange=True, title_text='Cost', title_font={"size": 14}, tickfont={"size":10}),
    yaxis=dict(autorange=True, title_text='Strength', title_font={"size": 14}, tickfont={"size":10}),
    height=230,
    width=630,
    margin=dict(l=0, r=0, b=0,t=0),
    plot_bgcolor='rgb(255,255,255)',
    )
    
    
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="left",
        x=-0.04
    ))
    
    
    return fig


@st.cache(allow_output_mutation=True)
def HeadToHeadScatter(data, home, away):   
     
    x0 = data['now_cost'].loc[(data['team'] == home)]
    x1 = data['now_cost'].loc[(data['team'] == away)]

    
    y0 = data['strength'].loc[(data['team'] == home)]
    y1 = data['strength'].loc[(data['team'] == away)]

    
    d0 = data['description'].loc[(data['team'] == home)]
    d1 = data['description'].loc[(data['team'] == away)]

        
        
    fig = go.Figure()

    # Add traces
    fig.add_trace(go.Scatter(x=x0, y=y0,
                        mode='markers',
                        marker_color=px.colors.qualitative.Light24[0],
                        name=home,
                        text=d0))
    
    fig.add_trace(go.Scatter(x=x1, y=y1,
                    mode='markers',
                    marker_color=px.colors.qualitative.Light24[13],
                    name=away,
                    text=d1))

    
    fig.update_layout(
    xaxis=dict(autorange=True, title_text='Cost', title_font={"size": 14}, tickfont={"size":10}),
    yaxis=dict(autorange=True, title_text='Strength', title_font={"size": 14}, tickfont={"size":10}),
    height=230,
    width=630,
    margin=dict(l=0, r=0, b=0,t=0),
    plot_bgcolor='rgb(255,255,255)',
    )
    
    
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="left",
        x=-0.04
    ))
    
    
    return fig


######  Show table with target team statistics and Graph   ##########################################################################################
st.markdown("<h3 style='text-align: left; color: purple; padding-left: 0px; font-size: 40px'><b>Team Analysis<b></h3>", unsafe_allow_html=True)

colx, coly, colz = st.columns([1, 1, 1])

tTeam = colx.selectbox('Team', teams, index=13)
lastGames = coly.number_input('Game History', min_value=2, step=1, value=6)
graph = colz.selectbox('Graphic', graph_options, index=5)
    
targTeam = tTeam
games=lastGames
graph_value = graph
    
homeTeam = merged_stats[(merged_stats['HomeTeam']==tTeam) | (merged_stats['AwayTeam']==tTeam)]

    
tarTeam = tables(homeTeam, games, tTeam)

colq, colw = st.columns([1, 1])

val = stats(homeTeam, targTeam, games, graph_value,0)
colq.plotly_chart(val[0], use_container_width=True)
colw.plotly_chart(val[1], use_container_width=True)

tarTeam



teamScatter = targetTeamScatter(elements, targTeam)

filter = filterElements(elements, tTeam)
playerStats = playerTables(filter)

playerNames = filterNames(elements, tTeam)

display = st.checkbox("Show "+targTeam+" Player Stats")

if display:
    st.markdown("<h3 style='text-align: left; color: #008080; padding-left: 0px; font-size: 20px'><b>"+targTeam+" Players Scatter Plot<b></h3>", unsafe_allow_html=True)
    st.write(teamScatter)
    st.markdown(" ")
    st.markdown("<h4 style='text-align: left; color: #872657; padding-left: 0px; font-size: 20px'><b>Players Analysis<b></h4>", unsafe_allow_html=True)
    st.write(playerStats)
    name = st.selectbox('Detailed Player Statistics', playerNames, index=0)
    playerGames = filterPlayer(history, name)
    player = playerStatistics(playerGames, games)
    st.write(player)


######  Show table with team comparison statistics and Graphs with Head to Head Section   ############################################################
st.markdown(" ")
st.markdown(" ")
st.markdown("<h3 style='text-align: left; color: purple; padding-left: 0px; font-size: 40px'><b>Team Comparison<b></h3>", unsafe_allow_html=True)

colx, coly = st.columns([1, 1])
    
home = colx.selectbox('Home Team', teams, index=13)
away= coly.selectbox('Away Team', teams, index=11)

homelogo = 'football_logo/'+home+'.png'
awaylogo = 'football_logo/'+away+'.png'

homeImage = Image.open(homelogo)
awayImage = Image.open(awaylogo)

teama = home
teamb = away

homeTeam12 = seasons[(seasons['HomeTeam']==home) | (seasons['AwayTeam']==home)]
awayTeam12 = seasons[(seasons['HomeTeam']==away) | (seasons['AwayTeam']==away)]   

homeTeam_merged = merged_stats[(merged_stats['HomeTeam']==home) | (merged_stats['AwayTeam']==home)]
awayTeam_merged = merged_stats[(merged_stats['HomeTeam']==away) | (merged_stats['AwayTeam']==away)]

    
head2head_merged = merged_stats[((merged_stats['HomeTeam']==home) & (merged_stats['AwayTeam']==away)) | ((merged_stats['HomeTeam']==away) & (merged_stats['AwayTeam']==home))]
    
target1 = team_merge[(team_merge['targetTeam']==home)]
team1 = pd.merge(homeTeam12, target1, how='inner', left_on=['gameDate','Season'], right_on=['gameDate','Season'])

target2 = team_merge[(team_merge['targetTeam']==away)]
team2 = pd.merge(awayTeam12 , target2, how='inner', left_on=['gameDate','Season'], right_on=['gameDate','Season'])

bothteams = pd.merge(team1 , team2, how='inner', left_on=['gameDate','Season'], right_on=['gameDate','Season'])
    
bothteams = bothteams[-games:]


cols, colt = st.columns([1,1])


val1 = stats(homeTeam_merged, teama, games, graph_value, 1)
val2 = stats(awayTeam_merged, teamb, games, graph_value, 2)

cols.plotly_chart(val1[0], use_container_width=True)
colt.plotly_chart(val2[0], use_container_width=True)


colu, colv = st.columns([1,1])
cols.plotly_chart(val1[1], use_container_width=True)
colt.plotly_chart(val2[1], use_container_width=True)

st.markdown("<h4 style='text-align: left; color: purple; padding-left: 0px; font-size: 40px'><b>Head-to-Head<b></h4>", unsafe_allow_html=True)
test = tables(head2head_merged,games,teama) 

coli, colo = st.columns([1,1])
test2 = statshead2head(head2head_merged, teama, teamb, games, graph_value)
coli.plotly_chart(test2[0], use_container_width=True)
colo.plotly_chart(test2[1], use_container_width=True)

test


headToheadScatter = HeadToHeadScatter(elements, home, away)

displayHeadToHead = st.checkbox('Show '+home+" versus "+away+" Players Distribution")

if displayHeadToHead:
    st.markdown("<h3 style='text-align: left; color: #008080; padding-left: 0px; font-size: 20px'><b>"+home+" versus "+away+" Players Scatter Plot<b></h3>", unsafe_allow_html=True)
    st.write(headToheadScatter)
    
   
homeFPL = teamFpl(elements, home)
awayFPL = teamFpl(elements, away)

home_names = homeFPL['web_name'].values
away_names = awayFPL['web_name'].values


homeline0 = lineup(elements, home)
awayline0 = lineup(elements, away)


Image.open('football_logo/football_logo.jpg')


soccerImage = Image.open('football_logo/preview3.png')
st.sidebar.image(soccerImage, width=200)


st.sidebar.markdown("<h3 style='text-align: left; color: #872657; padding-left: 0px; font-size: 30px'><b>Team Lineups<b></h3>", unsafe_allow_html=True)
st.sidebar.markdown(' ')
st.sidebar.markdown("<h3 style='text-align: left; color: #008080; padding-left: 0px; font-size: 20px'><b>"+home+" - Home Team<b></h3>", unsafe_allow_html=True)
st.sidebar.image(homeImage, width=200)
homeline = st.sidebar.multiselect(home+' Starting XI', home_names, default=homeline0)
homeCount = len(homeline)
homescore = round(teamStrength(elements, home, homeline),2)


st.sidebar.markdown("<h3 style='text-align: left; color: purple; padding-left: 0px; font-size: 20px'><b>Team Strength - "+str(homescore)+" | Players - "+str(homeCount)+"<b></h3>", unsafe_allow_html=True)


homeline = teamTables(homeFPL)

displayhome = st.sidebar.checkbox("Show "+home+" Players")

if displayhome:
    st.sidebar.plotly_chart(homeline)


st.sidebar.markdown(" ")
st.sidebar.markdown(" ")
st.sidebar.markdown("<h3 style='text-align: left; color: #008080; padding-left: 0px; font-size: 20px'><b>"+away+" - Away Team<b></h3>", unsafe_allow_html=True)
st.sidebar.image(awayImage, width=200)
awayline = st.sidebar.multiselect(away+' Starting XI', away_names, default=awayline0)
awayCount = len(awayline)
awayscore = round(teamStrength(elements, away, awayline),2)


st.sidebar.markdown("<h3 style='text-align: left; color: purple; padding-left: 0px; font-size: 20px'><b>Team Strength - "+str(awayscore)+" | Players - "+str(awayCount)+"<b></h3>", unsafe_allow_html=True)

awayline = teamTables(awayFPL)

displayaway = st.sidebar.checkbox("Show "+away+" Players")

if displayaway:
    st.sidebar.plotly_chart(awayline)
  
    
    
categories = ['platin', 'gold', 'silver', 'bronze']

models = ['zScore', 'kMeans', 'pcaKMeans']


st.markdown(" ")
st.markdown(" ")


st.markdown("<h3 style='text-align: left; color: purple; padding-left: 0px; font-size: 40px'><b>Team Scores<b></h3>", unsafe_allow_html=True)

allTeamScores = teamScores(elements, teams)

st.markdown("<h3 style='text-align: left; color: #008080; padding-left: 0px; font-size: 20px'><b>All Team Scores<b></h3>", unsafe_allow_html=True)
st.write(allTeamScores)

dreamteam = Image.open('football_logo/DreamTeam.png')

displayDreamTeam = st.checkbox('Show Dream Team')

if displayDreamTeam:
    st.markdown("<h3 style='text-align: left; color: #008080; padding-left: 0px; font-size: 20px'><b>GW22 Dream Team<b></h3>", unsafe_allow_html=True)
    st.image(dreamteam, width=475)
    

st.markdown(" ")
st.markdown(" ")
st.markdown("<h3 style='text-align: left; color: purple; padding-left: 0px; font-size: 40px'><b>Player Rankings<b></h3>", unsafe_allow_html=True)
modcol, catcol = st.columns([1,1])

model = modcol.selectbox('Model', models, index=0)

cati = catcol.selectbox('Category', categories, index=0)

if (cati == 'platin'):
    colors = 'grey'
    catName = 'Platinum'
elif (cati == 'gold'):
    colors = 'darkgoldenrod'
    catName = 'Gold'
elif (cati == 'silver'):
    colors = 'darkgrey'
    catName = 'Silver'
else:
    colors='burlywood'
    catName = 'Bronze'

playerCategory = playerRank(elements, cati, model)
playerRanking = playerRankTables(playerCategory)
playerscatter = playerScatter(playerCategory)

st.markdown(" ")
st.markdown(" ")

st.markdown("<h3 style='text-align: left; color: #008080; padding-left: 0px; font-size: 20px'><b>"+catName+" Players Scatter Plot<b></h3>", unsafe_allow_html=True)
st.write(playerscatter)

st.markdown(" ")
st.markdown(" ")

playerscatterAll = playerScatterAll(elements, model)
    
    
displayPlayers = st.checkbox('Show Players in Class')

if displayPlayers:

    st.markdown("<h3 style='text-align: left; color: #872657; padding-left: 0px; font-size: 20px'><b>"+catName+" Players Details<b></h3>", unsafe_allow_html=True)
    st.write(playerRanking)

displayAllPlayers = st.checkbox('Show All Players Scatter Plot')  
avgCategory = averageScatter(elements, model)  
    
if displayAllPlayers:
    st.markdown("<h3 style='text-align: left; color: #008080; padding-left: 0px; font-size: 20px'><b> All Players Scatter Plot<b></h3>", unsafe_allow_html=True)
    st.write(playerscatterAll)
    st.markdown(" ")
    st.markdown("<h3 style='text-align: left; color: #008080; padding-left: 0px; font-size: 20px'><b>Average Category Scores<b></h3>", unsafe_allow_html=True)
    st.write(avgCategory)
    

st.markdown(" ")      
st.markdown(" ")
st.markdown(" ")
premier, match = st.columns([1,6])

image3 = Image.open('football_logo/preview1.png')
premier.image(image3, use_column_width=True)

match.markdown("<h4 style='text-align: left; color: #551A8B; padding-left: 0px; font-size: 50px'><b>Simulate Match<b></h4>", unsafe_allow_html=True)


colq, colp = st.columns([1,1])


colq.image(homeImage, width=200)

colq.markdown("<h3 style='text-align: left; color: #008080; padding-left: 0px; font-size: 20px'><b>"+home+": Team Strength - "+str(homescore)+"<b></h3>", unsafe_allow_html=True)

colp.image(awayImage, width=200)

colp.markdown("<h3 style='text-align: left; color: #008080; padding-left: 0px; font-size: 20px'><b>"+away+": Team Strength - "+str(awayscore)+"<b></h3>", unsafe_allow_html=True)

xgHome0= colq.number_input(home+' (Home Adjustment)', min_value=-5.0, max_value=5.0, step=0.1, value=0.0)
xgAway0= colp.number_input(away+' (Away Adjustment)', min_value=-5.0, max_value=5.0, step=0.1, value=0.0)

xgHome = homescore + xgHome0
xgAway = awayscore + xgAway0

proby = matchProb(xgHome, xgAway)

proHome = '{:.2%}'.format(round(proby[0],4))
proDraw = '{:.2%}'.format(round(proby[1],4))
proAway = '{:.2%}'.format(round(proby[2],4))

oddHome = round(1/proby[0],2)
oddDraw = round(1/proby[1],2)
oddAway = round(1/proby[2],2)  

st.markdown(" ")
st.markdown(" ")

forecast, odds = st.columns([1,6])

image10 = Image.open('football_logo/football_logo.jpg')
forecast.image(image10, use_column_width=True)
odds.markdown("<h3 style='text-align: left; color: #551A8B; padding-left: 0px; font-size: 30px'><b>Match Probability (Fair Odds)<b></h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,1,1])

col1.markdown("<h3 style='text-align: left; color: #872657; padding-left: 0px; font-size: 20px'><b>HomeWin - "+str(proHome)+" ("+str(oddHome)+")<b></h3>", unsafe_allow_html=True)
col2.markdown("<h3 style='text-align: left; color: #872657; padding-left: 0px; font-size: 20px'><b>Draw - "+str(proDraw)+" ("+str(oddDraw)+")<b></h3>", unsafe_allow_html=True)
col3.markdown("<h3 style='text-align: left; color: #872657; padding-left: 0px; font-size: 20px'><b>AwayWin - "+str(proAway)+" ("+str(oddAway)+")<b></h3>", unsafe_allow_html=True)



############################################################################################################################
########Load Contract########################################################################################################

@st.cache(allow_output_mutation=True)
def load_contract():

    # Load the contract ABI
    with open(Path('./contracts/compiled/bettingSystem_abi.json')) as f:
        contract_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=contract_abi
    )

    return contract


# Load the contract
contract = load_contract()

betAccount = generate_account()
accounts = w3.eth.accounts[1:2]

st.title("Betting Account")

ClientAddress = st.selectbox("Select Account", options=accounts)
st.markdown("---")

################################################################################
# Register New Betting Account
################################################################################

if((contract.functions.totalSupply().call() == 0)):

    st.markdown("## Client Take-On")

    owner_name = st.text_input("Enter the name of account holder")
    account_name = st.text_input("Account Name")

    st.markdown(" ")
    st.markdown(" ")

    if st.button("Register Account"):
        
        initial_appraisal_value = 0       
        
        init_id = contract.functions.registerBettingAccount(
            ClientAddress,
            owner_name,
            account_name,
            int(initial_appraisal_value)
        )

        tx_hash = init_id.transact({'from': ClientAddress, 'gas': 1000000})

        receipt = w3.eth.waitForTransactionReceipt(tx_hash)   
        
        st.balloons()
        
        L = [str(initial_appraisal_value)]
        file1 = open('balance.txt', 'w')
        file1.writelines(L)
        file1.close()

if((contract.functions.totalSupply().call() == 1)):
    
    st.markdown("## Add Deposit")

    file1 = open('balance.txt', 'r')
    value = file1.readlines()
    val = int(float(value[0]))

    token_id=0
    appraisal_value = st.number_input('Deposit Amount', min_value=0, max_value=100, step=1, value=0)
    new_appraisal_value = appraisal_value + val
    if st.button("Deposit"):

        tx_hash = contract.functions.newAppraisal(
            token_id,
            int(new_appraisal_value),
        ).transact({"from": w3.eth.accounts[0]})
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        
        st.balloons()
        
        L = [str(new_appraisal_value)]
        file1 = open('balance.txt', 'w')
        file1.writelines(L)
        file1.close()

file1 = open('balance.txt', 'r')
value = file1.readlines()
val = int(float(value[0]))

st.write('Opening Account Balance: '+ str(val))

####
st.markdown("---")

########################################################################################################
if((contract.functions.totalSupply().call() == 1)):

    st.markdown("## Place Bet")


    colpick, colAmount = st.columns([1,1])

    outcome = [home+' Win', 'Draw', away+' Win']


    pick = colpick.selectbox('Pick', outcome, index=1)
    amount = colAmount.number_input('Bet Amount', min_value=0.0, max_value=100.0, step=1.0, value=0.0)

    Advantage = [0.05, 0.1, 0.15, 0.2, 0.25]
    Adjustment = [-0.02, -0.04, -0.06, -0.08, -0.1]

    homeAdvantage = random.choice(Advantage)
    awayAdjustment = random.choice(Adjustment)

    matchProbability = matchProb((homescore + homeAdvantage), (awayscore + awayAdjustment))

    proHomeInt = int(round(matchProbability[0],4)*100)
    proDrawInt = int(round(matchProbability[1],4)*100)
    proAwayInt = int(round(matchProbability[2],4)*100)

    result = random.choices(outcome, weights=(proHomeInt, proDrawInt, proAwayInt), k=1)

    if st.button("Place Bet"):
        
        ## Using readlines()
        file1 = open('balance.txt', 'r')
        value = file1.readlines()
        val = int(float(value[0]))

        st.write('Result: '+result[0])
        
        st.markdown(" ")
        if(result[0] == pick):

            if(pick == (home+' Win')):
                amount = round((amount*oddHome),2)
            elif(pick == (away+' Win')):
                amount = round((amount*oddAway),2)
            else:
                amount = round((amount*oddDraw),2)
            
            st.markdown('You Win!!!')   
            st.markdown(amount)  
            
        else:
            st.markdown('You Lose!!!')
            amount = -1*amount
            st.markdown(amount) 
            
            
        token_id=0
        new_appraisal_value = val + amount
            
        tx_hash = contract.functions.newAppraisal(
            token_id,
            int(new_appraisal_value),
        ).transact({"from": w3.eth.accounts[0]})
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        
        L = [str(new_appraisal_value)]
        file1 = open('balance.txt', 'w')
        file1.writelines(L)
        file1.close()  
        
        st.write('Updated Account Balance: '+str(new_appraisal_value))
        

#####################################################################################################
#####crypto wallet (Withdrawal)######################################################################
st.markdown(" ")
st.markdown(" ")

if((contract.functions.totalSupply().call() == 1)):
    
    st.markdown("## Withdrawal")


    withdrawal = st.number_input('Withdrawal Amount', min_value=0.0, max_value=100.0, step=1.0, value=0.0)

    if st.button("Withdraw Amount"):
    
        file1 = open('balance.txt', 'r')
        value = file1.readlines()
        val = int(float(value[0]))

        if(withdrawal > val):
            st.write ('Not enough funds to withdraw')
        else:
            new_appraisal_value = val - withdrawal
            
            token_id=0    
            tx_hash = contract.functions.newAppraisal(
                token_id,
                int(new_appraisal_value),
            ).transact({"from": w3.eth.accounts[0]})
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            
            st.balloons()
            
            L = [str(new_appraisal_value)]
            file1 = open('balance.txt', 'w')
            file1.writelines(L)
            file1.close()

            transaction_hash = send_transaction(w3, betAccount, accounts[0], withdrawal)

            st.write(transaction_hash)

            st.balloons()
        
## Using readlines()
file1 = open('balance.txt', 'r')
value = file1.readlines()
val = int(float(value[0]))

st.write('Closing Account Balance: '+ str(val))

st.markdown("---")

################################################################################
# Account Report
################################################################################
if((contract.functions.totalSupply().call() == 1)):
    st.markdown("## Get Account history")
    
    historylog = st.checkbox("Get Account Reports")
    
    Account_id = 0
    if historylog:
        appraisal_filter = contract.events.Appraisal.createFilter(
            fromBlock=0,
            argument_filters={"tokenId": Account_id}
        )
        appraisals = appraisal_filter.get_all_entries()
        if appraisals:    
            for appraisal in appraisals:
                report_dictionary = dict(appraisal)
                st.markdown("### Account Event Log")
                st.write(report_dictionary)
                st.markdown("### Account Details")
                st.write(report_dictionary["args"])
        else:
            st.write("No Bets Placed")

st.markdown("---")
#######################################################################################
#######################################################################################

