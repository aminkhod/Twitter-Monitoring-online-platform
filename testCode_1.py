# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 08:53:02 2022

@author: Hossein
"""

#besmellah
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
##
"""Parameters"""
floor_sentiment = 1
ceiling_sentiment = 4
increment = (ceiling_sentiment-floor_sentiment)/100
phi_price = {'Class1':(-0.97,0.15),'Class2':(-11.41,1.27),'Class3':(-3.17,0.59)
             ,'Class4':(-8.4,0.92),'Class5':(-7.62,1.16)}
beta_SocialMedia = {'Class1':(1.65,0.54),'Class2':(6.23,0.54),'Class3':(2,0.71)
             ,'Class4':(4.17,0.49),'Class5':(1.33,1.47)}
"""Input Data"""
df = pd.read_csv('ddata0.csv')
print(df.head())
df.set_index('sampleDate',inplace=True)
df.index = pd.to_datetime(df.index)
##
"""FUNCTIONS"""
#1#
def existingClasses(df)-> list:
    """returns Classes in Input Data"""
    df_colList = list(df.columns)
    ClassList = []
    for i in df_colList:
        m = re.match("(C\w+)",i)
        if m:
            ClassList.append(i)
    return ClassList
##
dataClasses = existingClasses(df)
#2#
def makeDeltaSentimentColumns(df)-> df:
    """claclutes difference in Sentiment Value for every pair of sequential rows and generates\
        the correponding diff columns in dataframe"""
    for Clas in existingClasses(df):
        txt = Clas+'_dif'
        df[txt] = df[Clas].diff()
    return df
##
test_makeDeltaSentimentColumns = makeDeltaSentimentColumns(df)
#3#
def singleRangeDeltaSentiment(df,callingStartDate:str,callingEndDate:str,callingClass:str)-> float:
    """caluclates difference in Sentiment Values\
        for a selective pair of (startDate and endDate)"""
    startSentiment = df.at[callingStartDate,callingClass]
    endSentiment = df.at[callingEndDate,callingClass]
    deltaSentiment = endSentiment - startSentiment
    return deltaSentiment
###
test_singleRangeDeltaSentiment = singleRangeDeltaSentiment(df,'1/15/2019','2/12/2019','Class1')
#4#
def listOfDiffColumns(df)-> list:
    """returns titles of columns of DeltaSentiment for all Classes"""
    df_colList = list(df.columns)
    ClassDifList = []
    for i in df_colList:
        if (i.endswith('dif')):
           ClassDifList.append(i) 
    return ClassDifList
##
test_listOfDiffColumns = listOfDiffColumns(df)
#5#
def deltaX_columns(df)-> df:
    """calculates deltaX from deltaSentiment\
        and adds the calculated columns to df"""
    for i in listOfDiffColumns(df):
        txt = i+'_deltaX'
        df[txt] = df.apply(lambda row: row[i] * (0.01/increment), axis=1)
    return df
##
test_deltaX_columns = deltaX_columns(df)
#6#
def singleRangeDeltaX(df,callingStartDate:str,callingEndDate:str,callingClass:str)-> float:
    """caluclates INCERMENT PERCENT Change (deltaX) in Sentiment Values\
        for a selective pair of (startDate and endDate)"""
    deltaSentiment = singleRangeDeltaSentiment(df,callingStartDate,callingEndDate,callingClass)
    deltaX = deltaSentiment * (0.01/increment)
    return deltaX
###
test_singleRangeDeltaX = singleRangeDeltaX(df,'1/15/2019','2/12/2019','Class1')
#7#
def beta_BY_phi(phi_price:dict, beta_SocialMedia:dict)-> dict:
    """calculates devision of (beta_SocialMedia/phi_price) per Class\
         considering Mean/Mean ; that is stdv excluded"""
    phiPrice_betaSocial = {}
    for k1,v1 in phi_price.items():
        for k2,v2 in beta_SocialMedia.items():
            if k1 == k2:
                phiPrice_betaSocial[k1] = v2[0] / v1[0]
    return phiPrice_betaSocial
###            
test_beta_BY_phi = beta_BY_phi(phi_price, beta_SocialMedia)
#8#
def listOfDeltaXcolumns(df)-> list:
    """returns titles of columns of deltaX for all Classes"""
    df_colList = list(df.columns)
    ClassDeltaXlist = []
    for i in df_colList:
        if (i.endswith('deltaX')):
           ClassDeltaXlist.append(i) 
    return ClassDeltaXlist
##
test_listOfDeltaXcolumns = listOfDeltaXcolumns(df)
#9#
def deltaWTP_columns(df,phi_price:dict,beta_SocialMedia:dict)-> df:
    """calculates deltaWTP from deltax\
        and adds the calculated columns to df"""
    coeff = beta_BY_phi(phi_price,beta_SocialMedia)
    for i in listOfDeltaXcolumns(df):
        for k,v in coeff.items():
            classStr = (i.split("_"))[0]
            if classStr == k:
                multiplier = v
            txt = i+'_deltaWTP'
            df[txt] = df.apply(lambda row: row[i] * multiplier, axis=1)
    return df
##
test_deltaWTP_columns = deltaWTP_columns(df,phi_price,beta_SocialMedia)
#10#
def singleRange_deltaWTP(df,callingStartDate:str,callingEndDate:str,callingClass:str,
                         phi_price:dict = phi_price,beta_SocialMedia:dict = beta_SocialMedia)-> float:
    """caluclates Delta in WillingnessToPay\
        for a selective (startDate and endDate)"""
    deltaX = singleRangeDeltaX(df,callingStartDate,callingEndDate,callingClass)
    coeff = beta_BY_phi(phi_price,beta_SocialMedia)
    for k,v in coeff.items():
        if k == callingClass:
            multiplier = v
    deltaWTP = deltaX * multiplier
    return deltaWTP
###
test_singleRange_deltaWTP = singleRange_deltaWTP(df,'1/15/2019','2/12/2019','Class1')
###
