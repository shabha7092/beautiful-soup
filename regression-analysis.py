import pandas as pd 
import matplotlib 
import matplotlib.pyplot as plt
matplotlib.interactive(True)


def scatter_plot(filePath):
    if filePath is None:
        return None
    data = pd.read_csv("gap.tsv", sep='\t')
    data.plot(x='year', y='lifeExp', kind='scatter',  title='Life expectancy over time')
    return data

def check_distribution(data):
    if data is None:
        return None
    data = data.copy()
    data = pd.concat([data.groupby('year' , sort=True)['lifeExp'].mean().reset_index(name ='mean_lifeExp'), 
    data.groupby('year' , sort=True)['lifeExp'].median().reset_index(name ='median_lifeExp').drop('year', axis =1)],ignore_index=False, axis=1)
    data['is_symmetric'] = data['mean_lifeExp'] == data['median_lifeExp']
    data['is_right_skewed'] = data['mean_lifeExp'] > data['median_lifeExp']
    data['is_left_skewed'] = data['mean_lifeExp'] < data['median_lifeExp']
    return data
