import sqlite3 as sql
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
matplotlib.interactive(True)


def get_conn():
    sqlite_file = 'lahman2014.sqlite'
    conn = sql.connect(sqlite_file)
    return conn

def problem_1():
    problem1_query = 'SELECT * FROM (SELECT * FROM (SELECT yearID as yearID, teamID as teamID, sum(salary) as payroll FROM Salaries GROUP BY yearID, teamID) AS TeamPayroll NATURAL JOIN (SELECT teamID as teamID, yearID as yearID, (W * 1.0/G ) * 100 AS win_percentage FROM Teams GROUP BY teamID, yearID) AS Teams_wins) AS TeamPayRollWinPercentage NATURAL JOIN Teams' 
    data = pd.read_sql(problem1_query, get_conn())
    return data

def problem_2():
    data = problem_1() 
    data = data.loc[(data.yearID >= 1990) & (data.yearID <= 2014)]
    fig, ax = plt.subplots()
    for teamid in data['teamID'].unique():
        data1 = data.loc[data['teamID'] == teamid]
        data1.plot(x='yearID', y='payroll', ax=ax, label=teamid)
    plt.title('Payroll Distribution')
    plt.xlabel('Year')
    plt.ylabel('Payroll')
    plt.show()
    return None

def problem_3():
    data = problem_1() 
    data = data.loc[(data.yearID >= 1990) & (data.yearID <= 2014)]
    data1 = data.groupby('yearID', sort=False)['payroll'].mean().reset_index(name ='mean')
    data1[['yearID','mean']].plot(title='Mean', kind='bar', x='yearID', y='mean')
    print(data1)
    plt.show()
    data2 = data.groupby('yearID', sort=False)['payroll'].median().reset_index(name ='median')
    data2[['yearID','median']].plot(title='Median', kind='bar', x='yearID', y='median')
    print(data2)
    plt.show()
    return None

def problem_4():
    data = problem_1() 
    data = data.loc[(data.yearID >= 1990) & (data.yearID <= 2014)]
    data = data[['yearID', 'teamID' , 'payroll', 'win_percentage']]
    bins = [1989, 1994, 1999, 2004, 2009, 2014]
    labels = [1, 2, 3, 4, 5]
    data['bin'] = pd.cut(data['yearID'], bins, labels=labels)
    data1 = data.groupby(['bin', 'teamID'], sort=False)['payroll'].mean().reset_index(name ='mean_payroll')
    data2 = data.groupby(['bin', 'teamID'], sort=False)['win_percentage'].mean().reset_index(name ='mean_win_percentage')
    data2 = data2.drop(columns= ['bin','teamID'])
    data = pd.concat([data1, data2], ignore_index=False, axis=1)
    bins = data['bin'].unique()
    colors = ['r', 'g', 'b', 'c', 'm']
    for idx, binid in enumerate(bins):
        data1 = data.loc[data['bin'] == binid]
        data1['color'] = np.where(data1['teamID'] == 'OAK', 'y', colors[idx])
        sns.lmplot(x='mean_payroll', y='mean_win_percentage', data=data1, scatter_kws={'facecolor': data1['color']}, line_kws={'color': 'k'}, 
        fit_reg=True, hue='bin', legend_out = True)
        ax = plt.gca()
        ax.set_title('Mean Payroll Win Percentage Distribution')
        ax.set_xlabel('Mean Payroll')
        ax.set_ylabel('Mean Win Percentage')
    return data

def problem_5():
   data = problem_1() 
   data = data.loc[(data.yearID >= 1990) & (data.yearID <= 2014)]
   data1 = data.groupby('yearID', sort=False)['payroll'].mean().reset_index(name ='mean_payroll')
   data2 = data.groupby('yearID', sort=False)['payroll'].std().reset_index(name ='std_payroll')
   data2 = data2.drop(columns= 'yearID')
   data3 = pd.concat([data1, data2], ignore_index=False, axis=1)
   data = pd.merge(data, data3, on='yearID', how='inner')
   data['diff'] = data['payroll'] - data['mean_payroll'] 
   data['standardized_payroll'] =   data['diff'] / data['std_payroll']
   return data[['yearID','teamID','payroll','win_percentage','mean_payroll', 'std_payroll', 'standardized_payroll','lgID','franchID','W','G','Rank']]


def problem_6():
    data = problem_5() 
    data = data[['yearID', 'teamID' , 'standardized_payroll', 'win_percentage']]
    bins = [1989, 1994, 1999, 2004, 2009, 2014]
    labels = [1, 2, 3, 4, 5]
    data['bin'] = pd.cut(data['yearID'], bins, labels=labels)
    data1 = data.groupby(['bin', 'teamID'], sort=False)['standardized_payroll'].mean().reset_index(name ='mean_standardized_payroll')
    data2 = data.groupby(['bin', 'teamID'], sort=False)['win_percentage'].mean().reset_index(name ='mean_win_percentage')
    data2 = data2.drop(columns= ['bin','teamID'])
    data = pd.concat([data1, data2], ignore_index=False, axis=1)
    bins = data['bin'].unique()
    colors = ['r', 'g', 'b', 'c', 'm']
    for idx, binid in enumerate(bins):
        data1 = data.loc[data['bin'] == binid]
        data1['color'] = np.where(data1['teamID'] == 'OAK', 'y', colors[idx])
        sns.lmplot(x='mean_standardized_payroll', y='mean_win_percentage', data=data1, scatter_kws={'facecolor': data1['color']}, line_kws={'color': 'k'}, 
        fit_reg=True, hue='bin', legend_out = True)
        ax = plt.gca()
        ax.set_title('Mean Standardized Payroll Win Percentage Distribution')
        ax.set_xlabel('Mean Standardized Payroll')
        ax.set_ylabel('Mean Win Percentage')
    return data

def problem_7():
     data = problem_5() 
     data = data[['yearID', 'teamID' , 'standardized_payroll', 'win_percentage']]
     bins = [1989, 1994, 1999, 2004, 2009, 2014]
     labels = [1, 2, 3, 4, 5]
     data['bin'] = pd.cut(data['yearID'], bins, labels=labels)
     data['color'] = data.apply(lambda row: label_color(row),axis=1) 
     sns.lmplot(x='standardized_payroll', y='win_percentage', data=data, scatter_kws={'facecolor': data['color']}, line_kws={'color': 'k'}, 
     fit_reg=True)
     ax = plt.gca()
     ax.set_title('Standardized Payroll Win Percentage Distribution')
     ax.set_xlabel('Standardized Payroll')
     ax.set_ylabel('Win Percentage Distribution')
     ax.legend(labels)
     return data

def problem_8():
    data = problem_5()
    data = data[['yearID', 'teamID' , 'standardized_payroll', 'win_percentage']]
    data['expecte_win_pct'] = 50 + 2.5 * data['standardized_payroll']
    data['efficiency'] = data['win_percentage'] - data['expecte_win_pct']
    teams =['OAK', 'BOS', 'NYA', 'ATL', 'TBA']
    fig, ax = plt.subplots()
    for teamid in teams:
        data1 = data.loc[data['teamID'] == teamid]
        data1.plot(x='yearID', y='efficiency', ax=ax, label=teamid)
    plt.title('Spending Efficiency')
    plt.xlabel('Year')
    plt.ylabel('Efficiency')
    plt.show()
    return data

def label_color (row):
   if row['bin'] == 1 :
      return 'r'
   if row['bin'] == 2:
      return 'g'
   if row['bin'] == 3 :
      return 'b'
   if row['bin'] == 4:
      return 'c'
   return 'm'
