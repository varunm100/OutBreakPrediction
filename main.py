#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as soup
import urllib.request, sys,json,re
import numpy as np
from datetime import datetime
import datetime as dt
import math

#IMPORTANT CONST
#-------------------------------#
typeDiseaseString = 'Foodborne'
GetDataStart = ''
GetDataEnd = ''
#-------------------------------#

#SOME BACK-END VARS
#-------------------------------#
global MainTypeD
global MainFormattedArr
global TrueArr
global FalseArr
global ClassificationPercentages
global DateDelta
MainTypeD = []
MainFormattedArr = []
TrueArr = [0,0,0,0,0]
FalseArr = [0,0,0,0,0]
ClassificationPercentages = []
DateDelta = 0
TodayDate = dt.date.today()
RequestURL = 'http://www.healthmap.org/getAlerts.php?category%5B%5D=1&category%5B%5D=2&category%5B%5D=29&locations%5B%5D=142&species%5B%5D=132&sdate=01%2F01%2F1900&edate=' + str(TodayDate.month) + '%2F' + str(TodayDate.day) + '%2F' +  str(TodayDate.year) + '&heatscore=1&partner=promed'
ScaleFactor = 1.0
#-------------------------------#

def WriteFileHeaders():
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
    	if str(typeDiseaseString) in str(element['label']).replace(',','_'):
    		MainTypeD.append(str(DateString) + ' ' + str(element['lat']) + ' ' + str(element['lon']))
    	NumberAlerts = len(element['alertids'])
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

def FormatDataMain():
	StringDate = str(MainTypeD[0]).split(' ')
	StringDate = str(StringDate[0]).strip()
	StringDate = StringDate.replace('-','/')
	date_format = "%Y/%m/%d"
	StartDate = datetime.strptime(str(StringDate), date_format)
	StartDate = dt.date(StartDate.year,StartDate.month,StartDate.day)
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
	NewUpdatedArr = []
	for iElement in FinalFreqArr:
		numFeatures = str(iElement).split(' ')
		if (len(numFeatures) <= 1):
			ElementIndex = FinalFreqArr.index(iElement)
			ElementIndex+=1
			SearchSubArr = FinalFreqArr[0:ElementIndex]
			SearchSubArr = SearchSubArr[::-1]
			StartNumF = str(SearchSubArr[0]).split(' ')
			for SubSubArr in SearchSubArr:
				numF = str(SubSubArr).split(' ')
				if (len(numF) > 3):
					numStart = str(StartNumF[0]).split(' ')
					DateAppendingStart = str(numStart[0]).strip()
					DateAppendingStart = DateAppendingStart.replace('-','/')
					date_format = "%Y/%m/%d"
					CounterDate002 = datetime.strptime(str(DateAppendingStart), date_format)
					CounterDate002 = dt.date(CounterDate002.year, CounterDate002.month, CounterDate002.day)

					DateAppendingEnd = str(numF[0]).strip()
					DateAppendingEnd = DateAppendingEnd.replace('-','/')
					date_format = "%Y/%m/%d"
					CounterDate003 = datetime.strptime(str(DateAppendingEnd), date_format)
					CounterDate003 = dt.date(CounterDate003.year, CounterDate003.month, CounterDate003.day)

					DeltaDaysTotal = CounterDate002 - CounterDate003
					DeltaDaysTotal = DeltaDaysTotal.days 
					NewUpdatedArr.append(str(SearchSubArr[0]) + " " + str(abs(DeltaDaysTotal)))
					break
		else:
			NewUpdatedArr.append(str(iElement))
	return NewUpdatedArr

def GenerateGraphStructure():
	global MainFormattedArr
	# Days off can have | 0-3 | 4-8 | 9-14| 15-25 | >25
	# -----------------------------------------------------
	#Index of those day |  0  |  1	|  2  |   3   |  4
	global TrueArr
	global FalseArr
	TrueArr = [0,0,0,0,0]
	FalseArr = [0,0,0,0,0]
	for ItemMain in MainFormattedArr:
		StringParsedArr = str(ItemMain).split(' ')
		StringParsedArrFalse = str(ItemMain).split(' ')
		if len(StringParsedArr) > 3:
			DeltaDaysMain = int(StringParsedArr[3])
			if 0 <= DeltaDaysMain <= 3:
				TrueArr[0] = TrueArr[0] + 1
			elif 4 <= DeltaDaysMain <= 8:
				TrueArr[1] = TrueArr[1] + 1
			elif 9 <= DeltaDaysMain <= 14:
				TrueArr[2] = TrueArr[2] + 1
			elif 15 <= DeltaDaysMain <= 25:
				TrueArr[3] = TrueArr[3] + 1
			elif DeltaDaysMain >= 25:
				TrueArr[4] = TrueArr[4] + 1
		else:
			DeltaDaysMainFalse = int(StringParsedArrFalse[1])
			if 0 <= DeltaDaysMainFalse <= 3:
				FalseArr[0] = FalseArr[0] + 1
			elif 4 <= DeltaDaysMainFalse <= 8:
				FalseArr[1] = FalseArr[1] + 1
			elif 9 <= DeltaDaysMainFalse <= 14:
				FalseArr[2] = FalseArr[2] + 1
			elif 15 <= DeltaDaysMainFalse <= 25:
				FalseArr[3] = FalseArr[3] + 1
			elif DeltaDaysMainFalse >= 25:
				FalseArr[4] = FalseArr[4] + 1

def BayesTheory():
	# Days off can have | 0-3 | 4-8 | 9-14| 15-25 | >25
	# -----------------------------------------------------
	#Index of those day |  0  |  1	|  2  |   3   |  4

	#Bayes Theory = P(True|0-1) = P(True)*P(0-1|True)/P(0-1)
	global MainFormattedArr
	global TrueArr
	global FalseArr
	global ClassificationPercentages
	classArrType = [0,1,2,3,4]
#------------------------- PUTTING EVERYTHING TOGETHER -------------------------# 
	TrueSum = int(sum(TrueArr))
	FalseSum = int(sum(FalseArr))
	TotalSum = TrueSum + FalseSum
	for SingleType in range(len(classArrType)):
		Yx = TrueArr[SingleType]
		Ay = TrueSum
		A = TotalSum
		Nx = FalseArr[SingleType]
		Numerator = (Yx/Ay)*(Ay/A)
		Denominator = (Nx+Yx)/A
		Final = Numerator/Denominator
		ClassificationPercentages.append(Final)

def Prediction(DaysAhead):
	global ClassificationPercentages
	global MainFormattedArr
	global DateDelta
	Today = dt.date.today() + dt.timedelta(days=DaysAhead)
	counter = 0
	FlagBoolPrediction = False
	DateDelta = 0
	while True:
		CounterDate004 = Today - dt.timedelta(days=counter)
		CounterDate004 = dt.date(CounterDate004.year, CounterDate004.month, CounterDate004.day)
		for CheckingDate in MainFormattedArr:
			ParsedDate = str(CheckingDate).split(' ')
			size = len(ParsedDate)
			ParsedDate = ParsedDate[0].strip()
			ParsedDate = ParsedDate.replace('-','/')
			date_format = "%Y/%m/%d"
			ParsedDate = datetime.strptime(str(ParsedDate), date_format)
			ParsedDate = dt.date(ParsedDate.year, ParsedDate.month, ParsedDate.day)
			if str(ParsedDate) == str(CounterDate004):
				if size > 3:
					FlagBoolPrediction = True
					break
		if FlagBoolPrediction == True:
			DateDelta = counter
			break
		
		counter+=1

	if DateDelta == 0:
		return (1/ScaleFactor)
	elif 1 <= DateDelta <= 3:
		return ClassificationPercentages[0]
	elif 4 <= DateDelta <= 8:
		return ClassificationPercentages[1]
	elif 9 <= DateDelta <= 14:
		return ClassificationPercentages[2]
	elif 15 <= DateDelta <= 25:
		return ClassificationPercentages[3]
	elif DateDelta >= 25:
		return ClassificationPercentages[4]

	return 0

def PrintZebiLogo():
	with open('Logo.txt') as f:
		FileLines = f.readlines()
	for SingleLine in FileLines:
		print("\033[34m" + SingleLine + "\033[0m", end='', flush=True)
	print('\n\n\n')

#-------------------------------#
PrintZebiLogo()
WriteFileHeaders()
PredictionDaysAheadUserInput = input("How far ahead would you like to predict?: ")
MainTypeD = GetData(RequestURL)
MainFormattedArr = FormatDataMain()
GenerateGraphStructure()
BayesTheory()
FinalPredictionVal = Prediction(int(PredictionDaysAheadUserInput))
FinalPredictionVal = ScaleFactor*FinalPredictionVal
print('\n')
print("------------------------------------------------------------------------------------------------------------------------------" + "\n")
print("There is a " + str(round(float(FinalPredictionVal*100), 3)) + "% chance of their being a " + str(typeDiseaseString) + " outbreak in " + str(PredictionDaysAheadUserInput) + " days of time." + "\n")
print("The most recent " + str(typeDiseaseString) + " outbreak happened " + str(DateDelta) + " days before the date you entered." + "\n")
print("------------------------------------------------------------------------------------------------------------------------------")
#-------------------------------#