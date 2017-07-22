#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as soup
import urllib.request, sys,json,re
import tensorflow as tf
import numpy as np
from datetime import datetime
import datetime as dt
import math

RequestURL = 'http://www.healthmap.org/getAlerts.php?category%5B%5D=1&category%5B%5D=2&category%5B%5D=29&locations%5B%5D=142&species%5B%5D=132&sdate=01%2F21%2F2017&edate=07%2F22%2F2017&heatscore=1&partner=promed'

global MainTypeD
MainTypeD = []
global MainFormattedArr
MainFormattedArr = []
#Weather constants -
Data = open('Data.csv', 'w')
Data.write('# of Alerts, Date, Type, Location, Lat, Lon' + '\n')
Data.close()

def FormatData(InputDate):
	InputDate = InputDate.replace('Jan','1')
	InputDate = InputDate.replace('Feb','2')
	InputDate = InputDate.replace('Mar','3')
	InputDate = InputDate.replace('Apr','4')
	InputDate = InputDate.replace('May','5')
	InputDate = InputDate.replace('Jun','6')
	InputDate = InputDate.replace('Jul','7')
	InputDate = InputDate.replace('Aug','8')
	InputDate = InputDate.replace('Sep','9')
	InputDate = InputDate.replace('Oct','10')
	InputDate = InputDate.replace('Nov','11')
	InputDate = InputDate.replace('Dec','12')
	InputDate = InputDate.strip()
	return str(InputDate)


def GetData(inputURL):
    global MainTypeD
    raw_data = urllib.request.urlopen(inputURL).read().decode()
    data = json.loads(raw_data)
    Data = open('Data.csv', 'a')
    for element in data['markers']:
    	Date = str(element['html'])
    	Date = soup(Date, 'html.parser')
    	Date = Date.span.text
    	Date = Date.replace(' - ', '').strip()
    	Date = Date.replace(' ','/')
    	Date = FormatData(str(Date))
    	date_format = "%d/%m/%Y"
    	Date = datetime.strptime(str(Date), date_format)
    	DateString = str(Date).replace(' 00:00:00','')
    	if "Foodborne" in str(element['label']).replace(',','_'):
    		MainTypeD.append(str(DateString) + ' ' + str(element['lat']) + ' ' + str(element['lon']))
    	NumberAlerts = len(element['alertids'])
    	# Finds the day and year - str(re.findall(r'\d+', str(Date)))
    	concateString = str(NumberAlerts) + ', ' + str(Date).replace(',','_') + ', ' + str(element['label']).replace(',','_') + ', ' + str(element['place_name']).replace(',','_') + ', ' + str(element['lat']).replace(',','_') + ', ' + str(element['lon']).replace(',','_') + '\n'
    	Data = open('Data.csv', 'a')
    	Data.write(str(concateString))
    	Data.close()

    MainTypeD = MainTypeD[::-1]
    ArrRange = len(MainTypeD)
    CounterDiType = []
    for i in range(ArrRange):
    	Delta = 0
    	if i != 0:
	    	StringDate = str(MainTypeD[i]).split(' ')
	    	StringDate = str(StringDate[0]).strip()
	    	StringDate = StringDate.replace('-','/')
	    	date_format = "%Y/%m/%d"
	    	DateA = datetime.strptime(str(StringDate), date_format)
	    	StringDate = str(MainTypeD[i-1]).split(' ')
	    	StringDate = str(StringDate[0]).strip()
	    	StringDate = StringDate.replace('-','/')
	    	date_format = "%Y/%m/%d"
	    	DateB = datetime.strptime(str(StringDate), date_format)
	    	Delta = DateB - DateA
	    	Delta = Delta.days
	    	Delta = abs(Delta)
	    	CounterDiType.append(str(MainTypeD[i]) + ' ' + str(Delta))

    print("Found " + str(len(CounterDiType)) + " chunks usable data!")
    print ("Got Most Recent Data [--------------100%-------------]")
    return CounterDiType

def BayesTheory():
	# Days off can have | 0-3 | 4-8 | 9-14| 15-20  | >20 |
	# -----------------------------------------------------
	#Index of those day |  0  |  1	|  2  |   3	   |  4  |

	#Bayes Theory = P(True|0-1) = P(True)*P(0-1|True)/P(0-1)
	global MainFormattedArr
	TrueArr = []
	#includes count of 0-3, 4-8, 9-14, 15-20, and >20 in the True classifier
	FalseArr = []
	#includes count of 0-3, 4-8, 9-14, 15-20, and >20 in the False classifier


def FormatDataMain():
	#Get Start Date
	StringDate = str(MainTypeD[0]).split(' ')
	StringDate = str(StringDate[0]).strip()
	StringDate = StringDate.replace('-','/')
	date_format = "%Y/%m/%d"
	StartDate = datetime.strptime(str(StringDate), date_format)
	StartDate = dt.date(StartDate.year,StartDate.month,StartDate.day)
	#Get End Date
	EndDate = dt.date.today()
	FinalFreqArr = []
	deltaDays = EndDate - StartDate
	for a in range(deltaDays.days):
		FlagBool = True
		for Type in MainTypeD:
			StringDate = str(Type).split(' ')
			StringDate = str(StringDate[0]).strip()
			StringDate = StringDate.replace('-','/')
			date_format = "%Y/%m/%d"
			CounterDate001 = datetime.strptime(str(StringDate), date_format)
			CounterDate001 = CounterDate001.replace(hour=0, minute=0, second=0, microsecond=0)
			CounterDate001 = dt.date(CounterDate001.year, CounterDate001.month, CounterDate001.day)
			if str(CounterDate001) == str(StartDate + dt.timedelta(days=a)):
				FinalFreqArr.append(str(Type))
				FlagBool = False
		if FlagBool == True:
			FinalFreqArr.append(str(StartDate + dt.timedelta(days=a)))

	FinalFreqArr = list(set(FinalFreqArr))
	for iElement in FinalFreqArr:
		numFeatures = str(iElement).split(' ')
		if (len(numFeatures) <= 1):
			#Do Some stuff here: get the closest number of days away from a previous day
			ElementIndex = FinalFreqArr.index(iElement)
			SearchSubArr = FinalFreqArr[:ElementIndex]
			SearchSubArr = SearchSubArr[::-1]
			for SubSubArr in SearchSubArr:
				numF = str(SubSubArr).split(' ')
				if (len(numF) > 1):
					break
	
	print("Formatted " + str(len(FinalFreqArr)) + " points!")
	return FinalFreqArr

MainTypeD = GetData(RequestURL)
MainFormattedArr = FormatDataMain()
BayesTheory()