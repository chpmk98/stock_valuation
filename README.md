# stock_valuation
This Python 3 script automatically pulls historic stock prices from Yahoo! Finance and evaluates the performance of various stocks against the market and an existing portfolio to help make more informed decisions in stock selection. Written by Alvin Tan in March 2020 and modified for GitHub in July 2020.

To conduct the analysis, download the repository and run stockBoi.py. The program uses the following libraries: csv, time, numpy, pandas, scipy, statsmodels, pandas_datareader, datetime, matplotlib, and xlrd. The program generates two output CSV files: fiveYearAnalysis.csv and tenYearAnalysis.csv. The two file names are prefixed by the machine time at time of output generation to allow for multiple runs without overriding previous output. Sample output files are included in this repository, and an explaination of the contents of the output files is included below.

To personalize the analysis, open stockBoi.py in a text editor and modify the pBoi dictionary to describe your current portfolio and the spicyBois list to contain the stocks that you want to consider. Then save and run stockBoi.py. You can also update the FamaFrench.xlsx file to contain updated data for Fama French analysis by downloading the Fama/French 5 Factors (2x3) [Daily] and Momentum Factor (Mom) [Daily] files from https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html and update the xlsx accordingly. At the time of writing, this data goes from July 1963 to May 2020.

**Disclaimer:** Historical performance does not necessarily predict future performance. There may be current events that would cause a certain asset to perform better than this analysis would predict, or something may happen that causes a promising asset to perform very poorly. As such, this analysis should be supplemented by additional research, and investments should be made only after careful consideration. I am not responsible if y'all lose money.

I use Robinhood as my broker. They provide commission-free transactions and have a reasonably straightforward interface. If you use my referral link to sign up, you start off with one free (randomly selected) stock: https://join.robinhood.com/alvint255.

## Explaination of Output
The fiveYearAnalysis and tenYearAnalysis files contain the same analysis across either a five-year time period or a ten-year time period. The five-year analysis gives more recent performance of the stocks while the ten-year analysis provides more data to work with.

In the analyses, we consider the performance of the Market, your current Portfolio, and the other stocks that you are interested in (generally referred to as "assets" in the subsequent text). For each of these, we calculate the following:

*Arithmetic Average Return* is the expected yearly percent return. Higher values are better.

*Volatility* is the yearly standard devation of the return and can be thought of as risk. Lower values are better.

*Geometric Average Return* is the average return when considering compounding effects. This value is generally lower than the Arithmetic Average Return and is not used in subsequent calculations.

*Sharpe Ratio* compares the asset's return with risk-free return and divides the difference by the asset's volatility. It is a way to quantify the risk v.s. return of stand-alone assets. Higher values are better.

*M2* (also known as the M-squared value or the Modigliani risk-adjusted performance) describes the difference in return between an asset and the overall market after adjusting the volatility of the asset to be equal to that of the market (by borrowing or loaning at the risk-free rate). Essentially this asks, "Given the same risk, how much more return can we expect to get from the asset compared to the market?". Higher values are better.

*The following four values (Beta, Jenson's Alpha, Tracking Error, and Appraisal Ratio) are calculated relative to some benchmark. In our analyses, we use both the market and your portfolio as benchmarks and report the results for both.*

*Beta* describes the relation between an asset's return and the return of the benchmark by running the regression
![equation](https://latex.codecogs.com/png.latex?r_a%20%3D%20%5Calpha%20&plus;%20%5Cbeta%20r_%7Bbmk%7D%20&plus;%20%5Cepsilon).
Essentially this asks, "How much does the asset move compared to a movement in the benchmark." For instance, given a beta value of 3, a 4% increase in the benchmark would correspond to a 12% increase in the asset value. Higher values indicate greater return in "good" times and greater losses in "bad" times. Lower values indicate insurance against "bad" times and generally mediocre performance in "good" times. Depending on current events and your own preferences, you can decide whether you want low beta or high beta stock.

*Jenson's Alpha* is the alpha value from the regression above and describes additional return an asset gains above that corresponding to benchmark variation. You can think of it as adjusting the expected returns for systematic risks (as described by the benchmark). It's also the maximum percent you should be willing to pay a fund manager for managing a particular portfolio (relative to the market). Higher values are better.

*Tracking Error* is the standard deviation of the error term in the regression above and describes how well the asset price can be described by the benchmark. This is not necessarily good or bad, but just shows how accurately the beta and Jenson's alpha values describe stock performance. Lower values indicate more correlation with the benchmark and greater accuracy of beta and alpha values in describing stock behavior, while higher values indicate more deviation from the benchmark and less predictive power of the beta and alpha values.

*Appraisal Ratio* takes Jenson's alpha and divides it by the tracking error. This adjusts the expected returns for idiosyncratic risks. Higher values are better.

*The following five values (const, Mkt-RF, SMB, HML, and MOM) come from the Fama-French four-factor model by running the regression 
![equation](https://latex.codecogs.com/png.latex?%5Csmall%20r_a%20%3D%20%5Calpha%20&plus;%20%5Cbeta_%7BMkt-RF%7D%20%28r_%7BMkt%7D%20-%20r_%7BRF%7D%29%20&plus;%20%5Cbeta_%7BSMB%7D%20SMB%20&plus;%20%5Cbeta_%7BHML%7D%20HML%20&plus;%20%5Cbeta_%7BMOM%7D%20MOM%20&plus;%20%5Cepsilon)
. We report both the coefficient value and the t-value, which is the coefficient value divided by its standard deviation. We consider a coefficient to be statistically significant if the magnitude of its t-value is greater than 1.96.*

*Fama-French const* adjusts the expected return for systematic risks as described by the other values in the regression. Higher values are better.

*Fama-French Mkt-RF* describes the relation between the asset and the overall market (or more specifically, the return of the market less the risk-free rate. This value is similar to the Beta (Mkt) value.

*Fama-French SMB* stands for Small-Minus-Big and describes the tendancy for small firms to have higher returns than large firms due to decreased security and larger transaction costs in small firm stocks. Positive values indicate the asset behaves like a small firm while negative values indicate the asset behaves like a large firm.

*Fama-French HML* stands for High-Minus-Low and describes how firms with high book-to-market ratios (i.e. value firms) tend to have higher returns than firms with low book-to-market ratios (i.e. growth firms). This is because value firms tend to be more risky than growth firms. Positive values indicate the asset behaves like a value firm while negative values indicate the asset behaves like a growth firm.

*Fama-French MOM* stands for MOMentum and describes how firms that have been doing well recently (i.e. over the past 6-months) continue to do well while firms that have been doing poorly continue to do poorly. This behavior is complemented by the reversal effect, where firms that have been doing well historically (i.e. five years ago) tend to do poorly now while firms that have been doing poorly tend to do well now. Positive values indicate that the asset follows this momentum effect while negative values indicate more fickle behavior.

*Fama-French R2* describes the proportion of the variation in the asset's price that can be described by the four factors in the Fama-French model. Values closer to 1 indicate better predictive power of the coefficients above while values closer to 1 indicate poor predictive power. Assets with smaller R2 values have a lot of idiosyncratic risk and/or are affected by systematic risks not included in the model.
