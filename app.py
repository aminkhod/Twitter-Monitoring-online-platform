# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 08:53:02 2022

@author: Hossein
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
##
"""Parameters"""
floor_sentiment = 1
ceiling_sentiment = 4
existingClasses = ['Class1','Class2','Class3','Class4','Class5','Avg']
increment = (ceiling_sentiment-floor_sentiment)/100
Table6 = {'Class1':74,'Class2':18,'Class3':None
             ,'Class4':9,'Class5':1,'Avg':28}
ColHeader = 'Sentiment'
"""Input Data"""
df = pd.read_csv('ddata1.csv')
df.set_index('sampleDate',inplace=True)
df.index = pd.to_datetime(df.index)
df0 = df.copy()
##
"""FUNCTIONS"""
# #1#
def makeDeltaSentimentColumns(df)-> df:
    """claclutes difference in Sentiment Value for every pair of sequential rows and generates\
        the correponding diff columns in dataframe"""
    txt = 'dif_'+ColHeader
    df[txt] = df[ColHeader].diff()
    return df
##
#2#
def singleRangeDeltaSentiment(df0,callingStartDate:str,callingEndDate:str,ColHeader:str='Sentiment')-> float:
    """caluclates difference in Sentiment Values\
        for a selective pair of (startDate and endDate)"""
    startSentiment = df0.at[callingStartDate,ColHeader]
    endSentiment = df0.at[callingEndDate,ColHeader]
    deltaSentiment = endSentiment - startSentiment
    return deltaSentiment
###
#3#
def deltaX_columns(df)-> df:
    """calculates deltaX from deltaSentiment\
        and adds the calculated columns to df"""
    df = makeDeltaSentimentColumns(df)
    DiffColumn = 'dif_'+ColHeader
    txt = 'deltaX'
    df[txt] = df.apply(lambda row: row[DiffColumn] * (0.01/increment), axis=1)
    return df
##
#4#
def singleRangeDeltaX(df0,callingStartDate:str,callingEndDate:str)-> float:
    """caluclates INCERMENT PERCENT Change (deltaX) in Sentiment Values\
        for a selective pair of (startDate and endDate)"""
    deltaSentiment = singleRangeDeltaSentiment(df0,callingStartDate,callingEndDate)
    deltaX = deltaSentiment * (0.01/increment)
    return deltaX
###
#5#
def deltaWTP_columns(df,Table6:dict)-> df:
    """calculates deltaWTP from deltax\
        and adds the calculated columns to df: a column per Class"""
    df = deltaX_columns(df)
    coeff = Table6
    for i in existingClasses:
        for k,v in coeff.items():
            if i == k:
                if(isinstance(v,(float,int))):
                    multiplier = v
                    txt = i+'_deltaWTP'
                    df[txt] = df.apply(lambda row: row.deltaX * multiplier, axis=1)
    return df
##
#6#
def singleRange_deltaWTP(df0,callingStartDate:str,callingEndDate:str,callingClass:str,
                          Table6:dict)-> float:
    """caluclates Delta in WillingnessToPay\
        for a selective (startDate and endDate)"""
    deltaX = singleRangeDeltaX(df0,callingStartDate,callingEndDate)
    coeff = Table6
    for k,v in coeff.items():
        if k == callingClass:
            if(isinstance(v,(float,int))):
                multiplier = v
        deltaWTP = deltaX * multiplier
    return deltaWTP
###
#7#
def get_cleaned_df(df,Table6:dict)-> df:
    """adding WTP Columns to df, dropping extra columns"""
    result_df = deltaWTP_columns(df,Table6)
    result_df.drop(['Sentiment', 'dif_Sentiment','deltaX'], axis=1, inplace=True)
    result_df.columns = result_df.columns.str.replace('_deltaWTP', '')
    return result_df
###
#8#
def df_byUserInput(start_Date:str, end_Date:str, callingClasses:list)-> df:
    """to prepare a TimeSeries for plotting: truncates df based on a Start Date and End Date\
        and tailor df by keeping only those columns of Classes called by User"""
    result_df = get_cleaned_df(df,Table6)
    ts = result_df.truncate(before = start_Date, after = end_Date)
    ts = ts[callingClasses]
    return ts
###
#9#
def plot_timeSeris(start_Date:str, end_Date:str, callingClasses:list)-> plt:
    """plots a time series by modifying df according called Dates and Classes by User"""
    ts = df_byUserInput(start_Date, end_Date, callingClasses)
    plt.figure(figsize = (15,8))
    sns.set_style("whitegrid")
    ax = sns.lineplot(data = ts, marker= 'o', markersize=14, palette="pastel")
    ax.set_title("WTP by Sentiment", fontsize = 20)
    ax.set_xlabel("Date", fontsize = 20)
    ax.set_ylabel("$ WTP", fontsize = 20)
    ax.legend (loc="best")
    plt.xticks(rotation=45)
###
# plot_timeSeris(start_Date = '1/29/2019', end_Date = '2/19/2019', callingClasses = ['Class1', 'Class4'])
test_singleRange_deltaWTP = singleRange_deltaWTP(df0,'1/15/2019','2/12/2019','Class1',Table6)
###

"""PART 2: create a Dashboard"""
###
result_df = get_cleaned_df(df,Table6)
###
import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input

"""Input Data"""
data = pd.read_csv("ddata1.csv")
data.set_index('sampleDate',inplace=True)
data.index = pd.to_datetime(data.index)
data = get_cleaned_df(data,Table6)
data = data.iloc[1: , :]
data.reset_index(inplace=True)
data.sort_values("sampleDate", inplace=True)
###ver 3 ###
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
###
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "WTP by Sentiment"
###
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children=" 🔌🚗🔌 ", className="header-emoji"),
                html.H1(
                    children="WTP Sentiment Dashboard", className="header-title"
                ),
                html.P(
                    children="presents changes in WTP"
                    " with respect to changes in Sentiment"
                    " gathered from Social Media",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Classes", className="menu-title"),
                        dcc.Dropdown(
                            id="Class-filter",
                            options=[
                                {"label": Col, "value": Col}
                                for Col in (data.columns) if Col != 'sampleDate'
                            ], 
                            value="Avg",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                ###
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                            ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.sampleDate.min().date(),
                            max_date_allowed=data.sampleDate.max().date(),
                            start_date=data.sampleDate.min().date(),
                            end_date=data.sampleDate.max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="Class-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="fixed-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)
###
@app.callback(
    [Output("Class-chart", "figure"), Output("fixed-chart", "figure")],
    [
        Input("Class-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
####   
def update_charts(Col, start_date, end_date):
    if Col != 'sampleDate':
        mask = (
            (data.sampleDate >= start_date)
            & (data.sampleDate <= end_date)
        )
        filtered_data = data.loc[:, Col]
        filtered_data = data.loc[mask, :]
##        
        price_chart_figure = {
            "data": [
                {
                    "x": filtered_data.sampleDate,
                    "y": filtered_data[Col],
                    "type": "lines",
                    "hovertemplate": "$%{y:.2f}<extra></extra>",
                },
            ],
            "layout": {
                "title": {
                    "text": "WTP in Class",
                    "x": 0.05,
                    "xanchor": "left",
                },
                "xaxis": {"fixedrange": True},
                "yaxis": {"tickprefix": "$", "fixedrange": True},
                "colorway": ["#17B897"],
            },
        }
    
        fixed_chart_figure = {
            "data": [
                {
                    "x": data.sampleDate,
                    "y": filtered_data['Avg'],
                    "name":'Average',
                    "type": "lines",
                },     
                ##
                {
                    "x": data.sampleDate,
                    "y": filtered_data['Class1'],
                    "name":'Class 1',
                    "type": "lines",
                },
                ##
                {
                    "x": data.sampleDate,
                    "y": filtered_data['Class2'],
                    "name":'Class 2',
                    "type": "lines",
                },
                ##
                {
                    "x": data.sampleDate,
                    "y": filtered_data['Class4'],
                    "name":'Class 4',
                    "type": "lines",
                },
                ##
                {
                    "x": data.sampleDate,
                    "y": filtered_data['Class5'],
                    "name":'Class 5',
                    "type": "lines",
                },
                ##
      
            ],
            "layout": {
                "title": {"text": "Average of Classes", "x": 0.05, "xanchor": "left"},
                "xaxis": {"fixedrange": True},
                "yaxis": {"tickprefix": "$","fixedrange": True},
                # "colorway": ["#E12D39"],
                
            },
        }
    return price_chart_figure,  fixed_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)
##
#####
