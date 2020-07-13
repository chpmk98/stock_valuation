# This python script is for evaluating cool stocks that I am interested in
# It uses Python 3

# import libraries
import csv
import time
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from pandas_datareader import data
from datetime import date, datetime
from matplotlib import pyplot as plt

# modify this dictionary to describe your current portfolio
# using stock symbols and number of stocks held
pBoi = {"INO" :1,
		"SPY" :1,
		"SPYG":2,
		"VOO" :1,
		"SPXL":2,
		"UPRO":2}

# modify this list to include all the stocks you want to consider
# and compare by using their stock symbols
spicyBois = ["MTB", "SOXL", "IJR", "SCZ", "IWD", "VOE"]

# read in the provided data from the Kenneth R. French Data Library and format the date for merging with other data
# this data currently goes from July 1963 to May 2020
# for subsequent dates, please download updated Fama/French 5 Factors (2x3) [Daily] and Momentum Factor (Mom) [Daily]
# data from https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html and update the xlsx accordingly
dateparse = lambda x: datetime.strptime(str(x), '%Y%m%d')
dfMFF = pd.read_excel('FamaFrench.xlsx', sheet_name='Daily', skiprows=3, usecols=[0,1,2,3,4,5],\
                     parse_dates=['Date'], date_parser=dateparse, index_col='Date' )
dfMFF['Date'] = pd.to_datetime(dfMFF.index).to_period('D')
dfMFF.set_index('Date',inplace=True)

# calculate market returns as well as 5 year and 10 year dates
dfMFF['Mkt'] = dfMFF['Mkt-RF'] + dfMFF['RF']
lastDate = dfMFF.iloc[-1].name.strftime('%m/%d/%Y')
fiveYearDate = dfMFF.iloc[-252*5].name.strftime('%m/%d/%Y')
tenYearDate = dfMFF.iloc[-252*10].name.strftime('%m/%d/%Y')
print("five-year analysis from {} to {}\nten-year analysis from {} to {}".format(fiveYearDate, lastDate, tenYearDate, lastDate))
print("starting analysis. this may take a minute or two...")

# calculate the daily returns of the current portfolio over the past 10 years
portfolioBoi = dict()
for stockSymbol, stockAmount in pBoi.items():
	portfolioBoi[stockSymbol] = (data.DataReader(stockSymbol, 'yahoo', start=tenYearDate, end=lastDate)['Adj Close'])*stockAmount
portfolioDF = pd.DataFrame(portfolioBoi)
portfolioDF['Portfolio'] = (portfolioDF.sum(axis=1).pct_change())*100
portfolioDF = portfolioDF.dropna()
portfolioDF['Date'] = pd.to_datetime(portfolioDF.index).to_period('D')
portfolioDF.set_index('Date',inplace=True)
dfMFF = dfMFF.merge(portfolioDF['Portfolio'], left_index=True, right_index=True)

# build dataframes for five year returns and 10 year returns of the target stocks
# note: five year returns cover the last five years, while 10 year returns cover the five years before that.
fiveYearBois = dict()
tenYearBois = dict()

for stockSymbol in spicyBois:
    fiveYearBois[stockSymbol] = (data.DataReader(stockSymbol, 'yahoo', start=fiveYearDate, end=lastDate)['Adj Close'].pct_change())*100
    tenYearBois[stockSymbol] = (data.DataReader(stockSymbol, 'yahoo', start=tenYearDate, end=fiveYearDate)['Adj Close'].pct_change())*100

# merge the five year and 10 year stock data with the Kenneth R. French data
fiveYearDF = pd.DataFrame(fiveYearBois)
fiveYearDF = fiveYearDF.dropna()
fiveYearDF['Date'] = pd.to_datetime(fiveYearDF.index).to_period('D')
fiveYearDF.set_index('Date',inplace=True)
fiveYearDF = dfMFF.merge(fiveYearDF, left_index=True, right_index=True)

tenYearDF = pd.DataFrame(tenYearBois)
tenYearDF = tenYearDF.dropna()
tenYearDF['Date'] = pd.to_datetime(tenYearDF.index).to_period('D')
tenYearDF.set_index('Date',inplace=True)
tenYearDF = dfMFF.merge(tenYearDF, left_index=True, right_index=True)

# we will report things in a table with columns in the order of Mkt, Portfolio, and Interesting Stocks
csvLabels = ['Mkt', 'Portfolio'] + spicyBois

# we store calculated values in dictionaries
fiveYearCalculatedValues = dict()
tenYearCalculatedValues = dict()

# establish days per year
T = 252

# calulate arithmetic average return
result = []
for stockSymbol in csvLabels:
	result.append(fiveYearDF[stockSymbol].mean()*T)
fiveYearCalculatedValues['Arithmetic Average Return'] = result

result = []
for stockSymbol in csvLabels:
	result.append(tenYearDF[stockSymbol].mean()*T)
tenYearCalculatedValues['Arithmetic Average Return'] = result

# calculate volatility
result = []
for stockSymbol in csvLabels:
	result.append(fiveYearDF[stockSymbol].std()*np.sqrt(T))
fiveYearCalculatedValues['Volatility'] = result

result = []
for stockSymbol in csvLabels:
	result.append(tenYearDF[stockSymbol].std()*np.sqrt(T))
tenYearCalculatedValues['Volatility'] = result

# calculate geometric average return
result = []
for stockSymbol in csvLabels:
	result.append((stats.gmean(fiveYearDF[stockSymbol]/100 + 1)**T - 1)*100)
fiveYearCalculatedValues['Geometric Average Return'] = result

result = []
for stockSymbol in csvLabels:
	result.append((stats.gmean(tenYearDF[stockSymbol]/100 + 1)**T - 1)*100)
tenYearCalculatedValues['Geometric Average Return'] = result

# calculate Sharpe Ratio
result = []
rfMean = fiveYearDF['RF'].mean()*T
for i in range(len(csvLabels)):
	result.append((fiveYearCalculatedValues['Arithmetic Average Return'][i] - rfMean)/fiveYearCalculatedValues['Volatility'][i])
fiveYearCalculatedValues['Sharpe Ratio'] = result

result = []
rfMean = tenYearDF['RF'].mean()*T
for i in range(len(csvLabels)):
	result.append((tenYearCalculatedValues['Arithmetic Average Return'][i] - rfMean)/tenYearCalculatedValues['Volatility'][i])
tenYearCalculatedValues['Sharpe Ratio'] = result

# calculate M2 measure
result = []
MktSD = fiveYearCalculatedValues['Volatility'][0]
MktSR = fiveYearCalculatedValues['Sharpe Ratio'][0]
for i in range(len(csvLabels)):
	result.append((fiveYearCalculatedValues['Sharpe Ratio'][i] - MktSR)*MktSD)
fiveYearCalculatedValues['M2'] = result

result = []
MktSD = tenYearCalculatedValues['Volatility'][0]
MktSR = tenYearCalculatedValues['Sharpe Ratio'][0]
for i in range(len(csvLabels)):
	result.append((tenYearCalculatedValues['Sharpe Ratio'][i] - MktSR)*MktSD)
tenYearCalculatedValues['M2'] = result

# calculate market beta
result = []
for stockSymbol in csvLabels:
	result.append(sm.OLS(fiveYearDF[stockSymbol], sm.add_constant(fiveYearDF['Mkt'])).fit().params['Mkt'])
fiveYearCalculatedValues['Beta (Mkt)'] = result

result = []
for stockSymbol in csvLabels:
	result.append(sm.OLS(tenYearDF[stockSymbol], sm.add_constant(tenYearDF['Mkt'])).fit().params['Mkt'])
tenYearCalculatedValues['Beta (Mkt)'] = result

# calculate Jenson's Alpha relative to the market
result = []
rfMean = fiveYearDF['RF'].mean()*T
MktMean = fiveYearCalculatedValues['Arithmetic Average Return'][0]
for i in range(len(csvLabels)):
	result.append(fiveYearCalculatedValues['Arithmetic Average Return'][i] - (rfMean + fiveYearCalculatedValues['Beta (Mkt)'][i]*(MktMean - rfMean)))
fiveYearCalculatedValues["Jenson's Alpha (Mkt)"] = result

result = []
rfMean = tenYearDF['RF'].mean()*T
MktMean = tenYearCalculatedValues['Arithmetic Average Return'][0]
for i in range(len(csvLabels)):
	result.append(tenYearCalculatedValues['Arithmetic Average Return'][i] - (rfMean + tenYearCalculatedValues['Beta (Mkt)'][i]*(MktMean - rfMean)))
tenYearCalculatedValues["Jenson's Alpha (Mkt)"] = result

# calculate tracking error relative to the market
result = []
MktMean = fiveYearCalculatedValues['Arithmetic Average Return'][0]
for i, stockSymbol in enumerate(csvLabels):
	result.append((fiveYearDF[stockSymbol] - (fiveYearCalculatedValues['Arithmetic Average Return'][i] - fiveYearCalculatedValues['Beta (Mkt)'][i]*MktMean) - fiveYearCalculatedValues['Beta (Mkt)'][i]*fiveYearDF['Mkt']).std()*np.sqrt(T))
fiveYearCalculatedValues['Tracking Error (Mkt)'] = result

result = []
MktMean = tenYearCalculatedValues['Arithmetic Average Return'][0]
for i, stockSymbol in enumerate(csvLabels):
	result.append((tenYearDF[stockSymbol] - (tenYearCalculatedValues['Arithmetic Average Return'][i] - tenYearCalculatedValues['Beta (Mkt)'][i]*MktMean) - tenYearCalculatedValues['Beta (Mkt)'][i]*tenYearDF['Mkt']).std()*np.sqrt(T))
tenYearCalculatedValues['Tracking Error (Mkt)'] = result

# calculate Appraisal Ratio relative to the market
result = []
for i in range(len(csvLabels)):
	result.append(fiveYearCalculatedValues["Jenson's Alpha (Mkt)"][i]/fiveYearCalculatedValues['Tracking Error (Mkt)'][i])
fiveYearCalculatedValues['Appraisal Ratio (Mkt)'] = result

result = []
for i in range(len(csvLabels)):
	result.append(tenYearCalculatedValues["Jenson's Alpha (Mkt)"][i]/fiveYearCalculatedValues['Tracking Error (Mkt)'][i])
tenYearCalculatedValues['Appraisal Ratio (Mkt)'] = result

# calculate portfolio beta
result = []
for stockSymbol in csvLabels:
	result.append(sm.OLS(fiveYearDF[stockSymbol], sm.add_constant(fiveYearDF['Portfolio'])).fit().params['Portfolio'])
fiveYearCalculatedValues['Beta (Portfolio)'] = result

result = []
for stockSymbol in csvLabels:
	result.append(sm.OLS(tenYearDF[stockSymbol], sm.add_constant(tenYearDF['Portfolio'])).fit().params['Portfolio'])
tenYearCalculatedValues['Beta (Portfolio)'] = result

# calculate Jenson's Alpha relative to the portfolio
result = []
rfMean = fiveYearDF['RF'].mean()*T
MktMean = fiveYearCalculatedValues['Arithmetic Average Return'][1]
for i in range(len(csvLabels)):
	result.append(fiveYearCalculatedValues['Arithmetic Average Return'][i] - (rfMean + fiveYearCalculatedValues['Beta (Portfolio)'][i]*(MktMean - rfMean)))
fiveYearCalculatedValues["Jenson's Alpha (Portfolio)"] = result

result = []
rfMean = tenYearDF['RF'].mean()*T
MktMean = tenYearCalculatedValues['Arithmetic Average Return'][1]
for i in range(len(csvLabels)):
	result.append(tenYearCalculatedValues['Arithmetic Average Return'][i] - (rfMean + tenYearCalculatedValues['Beta (Portfolio)'][i]*(MktMean - rfMean)))
tenYearCalculatedValues["Jenson's Alpha (Portfolio)"] = result

# calculate tracking error relative to the portfolio
result = []
MktMean = fiveYearCalculatedValues['Arithmetic Average Return'][1]
for i, stockSymbol in enumerate(csvLabels):
	result.append((fiveYearDF[stockSymbol] - (fiveYearCalculatedValues['Arithmetic Average Return'][i] - fiveYearCalculatedValues['Beta (Portfolio)'][i]*MktMean) - fiveYearCalculatedValues['Beta (Portfolio)'][i]*fiveYearDF['Portfolio']).std()*np.sqrt(T))
fiveYearCalculatedValues['Tracking Error (Portfolio)'] = result

result = []
MktMean = tenYearCalculatedValues['Arithmetic Average Return'][1]
for i, stockSymbol in enumerate(csvLabels):
	result.append((tenYearDF[stockSymbol] - (tenYearCalculatedValues['Arithmetic Average Return'][i] - tenYearCalculatedValues['Beta (Portfolio)'][i]*MktMean) - tenYearCalculatedValues['Beta (Portfolio)'][i]*tenYearDF['Portfolio']).std()*np.sqrt(T))
tenYearCalculatedValues['Tracking Error (Portfolio)'] = result

# calculate Appraisal Ratio relative to the portfolio
result = []
for i in range(len(csvLabels)):
	result.append(fiveYearCalculatedValues["Jenson's Alpha (Portfolio)"][i]/fiveYearCalculatedValues['Tracking Error (Portfolio)'][i])
fiveYearCalculatedValues['Appraisal Ratio (Portfolio)'] = result

result = []
for i in range(len(csvLabels)):
	result.append(tenYearCalculatedValues["Jenson's Alpha (Portfolio)"][i]/tenYearCalculatedValues['Tracking Error (Portfolio)'][i])
tenYearCalculatedValues['Appraisal Ratio (Portfolio)'] = result

# runs the Fama French four-factor model
ffFactors = ['Mkt-RF', 'SMB', 'HML', 'MOM']
X = sm.add_constant(fiveYearDF[ffFactors])
ffFactors = ['const'] + ffFactors
result = []
for factorName in ffFactors:
	fiveYearCalculatedValues['Fama-French ' + factorName + ' (coef)'] = []
	fiveYearCalculatedValues['Fama-French ' + factorName + ' (t)'] = []
for stockSymbol in csvLabels:
	Y = (fiveYearDF[stockSymbol] - fiveYearDF['RF'])
	ffBoi = sm.OLS(Y, X).fit()
	for factorName in ffFactors:
		fiveYearCalculatedValues['Fama-French ' + factorName + ' (coef)'].append(ffBoi.params[factorName])
		fiveYearCalculatedValues['Fama-French ' + factorName + ' (t)'].append(ffBoi.tvalues[factorName])
	result.append(ffBoi.rsquared)
fiveYearCalculatedValues['Fama-French R2'] = result

ffFactors = ['Mkt-RF', 'SMB', 'HML', 'MOM']
X = sm.add_constant(tenYearDF[ffFactors])
ffFactors = ['const'] + ffFactors
result = []
for factorName in ffFactors:
	tenYearCalculatedValues['Fama-French ' + factorName + ' (coef)'] = []
	tenYearCalculatedValues['Fama-French ' + factorName + ' (t)'] = []
for stockSymbol in csvLabels:
	Y = (tenYearDF[stockSymbol] - tenYearDF['RF'])
	ffBoi = sm.OLS(Y, X).fit()
	for factorName in ffFactors:
		tenYearCalculatedValues['Fama-French ' + factorName + ' (coef)'].append(ffBoi.params[factorName])
		tenYearCalculatedValues['Fama-French ' + factorName + ' (t)'].append(ffBoi.tvalues[factorName])
	result.append(ffBoi.rsquared)
tenYearCalculatedValues['Fama-French R2'] = result





timeSig = time.time()
# after all our calculations, we store the data in a txt file
with open('{}__fiveYearAnalysis.csv'.format(timeSig), 'w', newline='') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow([date.today()] + csvLabels)
    for key in fiveYearCalculatedValues:
        wr.writerow([key] + fiveYearCalculatedValues[key])

with open('{}__tenYearAnalysis.csv'.format(timeSig), 'w', newline='') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow([date.today()] + csvLabels)
    for key in tenYearCalculatedValues:
        wr.writerow([key] + tenYearCalculatedValues[key])

print("all done!")




