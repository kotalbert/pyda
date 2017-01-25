# -*- coding: utf-8 -*-
"""
Assignment 3.
Using pandas library for data manipulation
"""

# Question 1
# Read data into data frames

import pandas as pd
from datetime import datetime


def energy_read():
    """
    Read energy data set (exel).
    Skip header and footer.
    Recognize missing values
    Apply names to data columns.
    """
    energy = pd.read_excel('../data/ei.xls',
                           skiprows=18,
                           skipfooter=38,
                           na_values="...",
                           header=None,
                           names=['Country', 'Energy Supply',
                                  'Energy Supply per Capita', '% Renewable'],
                           usecols=range(2, 6))
    return energy


def energy_clean(e):
    """
    Convert values in energy data file, as required.
    """
    # Convert peta to giga
    e['Energy Supply'] = e['Energy Supply']*1e6

    # rename countries
    e['Country'] = (e['Country'].str
                    .replace('China, Hong Kong Special Administrative Region',
                             'Hong Kong'))
    e['Country'] = (e['Country'].str
                    .replace('China, Macao Special Administrative Region',
                             'Macao'))
    e['Country'] = (e['Country'].str
                    .replace('United Kingdom of Great Britain and Northern '
                             'Ireland', 'United Kingdom'))
    e['Country'] = (e['Country'].str
                    .replace('United States of America', 'United States'))
    e['Country'] = e['Country'].str.replace('Republic of Korea', 'South Korea')

    # remove numbers and parenthesis
    e['Country'] = e['Country'].str.replace('[0-9]', '')
    e['Country'] = e['Country'].str.replace('\s+\(.+', '')
    e = e.set_index('Country')

    return(e)


def wb_read():
    """
    Read world bank data set.
    Skip the header.
    """
    wb = pd.read_csv('..\data\world_bank.csv', skiprows=4)
    return(wb)


def wb_clean(wb):
    """
    Clean the world bank data.
    Rename countries to match energy data set.
    """
    wb['Country Name'] = (wb['Country Name'].str
                          .replace('Korea, Rep.', 'South Korea'))
    wb['Country Name'] = (wb['Country Name'].str
                          .replace('Iran, Islamic Rep.', 'Iran'))
    wb['Country Name'] = (wb['Country Name'].str
                          .replace('Hong Kong SAR, China', 'Hong Kong'))
    wb = wb.set_index('Country Name')
    return(wb)


def sm_read():
    """
    Read the scimago data.
    """
    sm = pd.read_excel('..\data\scimagojr-3.xlsx')
    sm = sm.set_index('Country')
    return(sm)


def data_merge(en, gdp, sm):
    """
    Merge the data by country name.
    Use only the last 10 years (2006-2015) of GDP data and only the top 15
    countries by Scimagojr 'Rank' (Rank 1 through 15).
    """

    # limiting scimagojr data
    sm = sm[sm['Rank'] <= 15]

    # limiting the output
    df = pd.merge(en, gdp, how='inner', right_index=True, left_index=True)
    df = pd.merge(df, sm, how='inner', right_index=True, left_index=True)

    # merging the frames
    cols = ['Rank', 'Documents', 'Citable documents', 'Citations',
            'Self-citations', 'Citations per document', 'H index',
            'Energy Supply', 'Energy Supply per Capita', '% Renewable',
            '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013',
            '2014', '2015']
    df = df[cols]

    return (df)


def answer_one():
    # Read the data sets
    GDP = wb_read()
    GDP = wb_clean(GDP)
    ScimEn = sm_read()
    energy = energy_read()
    energy = energy_clean(energy)

    df = data_merge(energy, GDP, ScimEn)
    return df


# Question 2
def answer_two():
    # Read the data sets
    GDP = wb_read()
    GDP = wb_clean(GDP)
    ScimEn = sm_read()
    energy = energy_read()
    energy = energy_clean(energy)

    return(GDP.shape[0] + ScimEn.shape[0] + energy.shape[0] - 15)


# Question 3
def answer_three():
    """What is the average GDP over the last 10 years for each country?
    (exclude missing values from this calculation.)"""
    Top15 = answer_one()
    yrs = ['2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013',
           '2014', '2015']
    gdp = Top15[yrs]
    gms = (gdp
           .mean(axis=1)
           .sort_values(ascending=False)
           )
    return(gms)


# Question 4
def answer_four():
    """ By how much had the GDP changed over the 10 year span for the country
    with the 6th largest average GDP? """
    top15 = answer_one()
    gm = answer_three()

    # find which country has 6th position, extract gdp values
    cn = gm.index[5]
    gdp = top15.loc[cn, ['2006', '2015']]

    # find gdp values
    dif = gdp['2015'] - gdp['2006']
    return(dif)


# Question 5
def answer_five():
    """ What is the mean `Energy Supply per Capita`? """
    mepc = answer_one()['Energy Supply per Capita'].mean()
    return(mepc)


# Question 6
def answer_six():
    """ What country has the maximum % Renewable and what is the percentage?"""
    re = answer_one()['% Renewable']
    return(re.argmax(), re.max())


# Question 7
def answer_seven():
    """ Create a new column that is the ratio of Self-Citations to Total
    Citations. What is the maximum value for this new column, and what country
    has the highest ratio? """
    top15 = answer_one()
    ratio = top15['Self-citations']/top15['Citations']
    return (ratio.argmax(), ratio.max())


# Question 8
def answer_eight():
    """ Create a column that estimates the population using Energy Supply and
    Energy Supply per capita. What is the third most populous country according
    to this estimate? """
    top15 = answer_one()
    popest = top15['Energy Supply']/top15['Energy Supply per Capita']
    popest.sort_values(ascending=False, inplace=True)
    return(popest.index[2])


# Question 9
def answer_nine():
    """ Create a column that estimates the number of citable documents per
    person. What is the correlation between the number of citable documents per
    capita and the energy supply per capita?
    Use the .corr() method, (Pearson's correlation). """

    Top15 = answer_one()
    Top15['PopEst'] = Top15['Energy Supply'] / Top15['Energy Supply per Capita']
    Top15['Citable docs per Capita'] = (
        Top15['Citable documents'] / Top15['PopEst'])
    cr = (Top15[['Citable docs per Capita', 'Energy Supply per Capita']]
          .corr().iloc[0][1])
    return (cr)


# Question 10
def answer_ten():
    """ Create a new column with a 1 if the country's % Renewable value is at
    or above the median for all countries in the top 15, and a 0 if the
    country's % Renewable value is below the median."""
    top15 = answer_one()
    med = top15['% Renewable'].median()
    top15['HighRenew'] = 0
    top15.loc[top15['% Renewable'] >= med, 'HighRenew'] = 1
    return(top15['HighRenew'])


# Question 11
def answer_eleven():
    """Use the following dictionary to group the Countries by Continent, then
    create a dateframe that displays the sample size (the number of countries in
    each continent bin), and the sum, mean, and std deviation for the estimated
    population of each country. """
    ContinentDict = {'China': 'Asia',
                     'United States': 'North America',
                     'Japan': 'Asia',
                     'United Kingdom': 'Europe',
                     'Russian Federation': 'Europe',
                     'Canada': 'North America',
                     'Germany': 'Europe',
                     'India': 'Asia',
                     'France': 'Europe',
                     'South Korea': 'Asia',
                     'Italy': 'Europe',
                     'Spain': 'Europe',
                     'Iran': 'Asia',
                     'Australia': 'Australia',
                     'Brazil': 'South America'}
    top15 = answer_one()
    top15['Population est.'] = (top15['Energy Supply'] /
                                top15['Energy Supply per Capita'])
    # reset index
    top15.reset_index(level=0, inplace=True)
    top15['Continent'] = top15['index'].apply(ContinentDict.get)
    top15.set_index('Continent', inplace=True)
    stats = ['size', 'sum', 'mean', 'std']
    agr = top15['Population est.'].groupby(level=0).agg(stats)
    return agr


# Question 12
def answer_twelve():
    """ Cut % Renewable into 5 bins. Group Top15 by the Continent, as well as
    these new % Renewable bins. How many countries are in each of these groups?
    """
    ContinentDict = {'China': 'Asia',
                     'United States': 'North America',
                     'Japan': 'Asia',
                     'United Kingdom': 'Europe',
                     'Russian Federation': 'Europe',
                     'Canada': 'North America',
                     'Germany': 'Europe',
                     'India': 'Asia',
                     'France': 'Europe',
                     'South Korea': 'Asia',
                     'Italy': 'Europe',
                     'Spain': 'Europe',
                     'Iran': 'Asia',
                     'Australia': 'Australia',
                     'Brazil': 'South America'}
    top15 = answer_one()
    top15.reset_index(level=0, inplace=True)
    top15['Continent'] = top15['index'].apply(ContinentDict.get)
    top15['% Renewable bins'] = pd.cut(top15['% Renewable'], 5)
    top15 = top15.groupby(['Continent', '% Renewable bins']).size()
    return (top15)


# Question 13
def fmt(s):
    """ Helper for formating values with separator """
    return '{:,}'.format(s)


def answer_thirteen():
    """ Convert the Population Estimate series to a string with thousands
    separator (using commas). Do not round the results. """
    top15 = answer_one()
    popest = top15['Energy Supply'] / top15['Energy Supply per Capita']
    popest = popest.apply(fmt)

    return (popest)


print('Last run:', datetime.now())
