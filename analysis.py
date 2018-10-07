from assignment import get_Space_weather_data
from assignment import get_top50_space_weather_data
from assignment import get_formatted_nasa_data
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.interactive(True)

def get_replication(URL=None, columns=['rank', 'x_class', 'start_datetime', 'max_datetime', 'end_datetime', 'region']):
    if URL is None:
        return None
    data = get_formatted_nasa_data(URL)
    data = data.dropna(subset=['importance'])
    data = data[data.importance != 'FILA']
    data['key1'] = data['importance'].str[0]
    data['key2'] = data['importance'].str[1:].astype(float)
    data = data.sort_values(['key1', 'key2'], ascending=[False, False])
    data['region'] = data['flare_region'].str[1:]
    data['x_class'] = data['key1'].astype(str) + data['key2'].astype(str)
    data['max_datetime'] = data['cme_datetime']
    data = data.dropna(subset=['x_class', 'start_datetime', 'max_datetime', 'end_datetime', 'region'])
    data = data.reset_index(drop=True)
    data['rank'] = data.index + 1
    data = data[columns]
    return data.head(50)
    

def get_integration(URL1=None, URL2=None):
    if URL1 is None or URL2 is None:
        return None
    data = get_Space_weather_data(URL1)
    data1 = get_top50_space_weather_data(data)
    data1['key1'] = data1['x_class'].str[0]
    data1['key2'] = data1['x_class'].str[1:].astype(float)
    data = get_formatted_nasa_data(URL2)
    data2 = data.copy()
    data2 = data2.dropna(subset=['importance'])
    data2 = data2[data2.importance != 'FILA']
    data2['region'] = data2['flare_region'].str[1:]
    data2 = data2[data2['region'].str.contains('[^A-Za-z?]', na=False)] 
    data2['region'] = data2['region'].astype(int)
    data2['key1'] = data2['importance'].str[0]
    data2['key2'] = data2['importance'].str[1:].astype(float)
    data2['x_class'] = data2['key1'].astype(str) + data2['key2'].astype(str)
    data2['max_datetime'] = data2['cme_datetime']
    data2 = data2[['x_class', 'start_datetime', 'max_datetime', 'end_datetime', 'region', 'key1', 'key2']]
    data2 = data2.dropna()
    data2 = data2.reset_index(drop=True)
    merged_data = pd.merge_asof(data1.sort_values('start_datetime', ascending='False'), data2.sort_values('start_datetime', ascending='False'), on='start_datetime', by=['key1', 'key2','region'], direction = 'nearest').dropna()
    merged_data = pd.merge(merged_data, data, how='left', left_on=['max_datetime_y', 'end_datetime_y'], right_on=['cme_datetime', 'end_datetime'])
    merged_data = merged_data.rename(columns={'start_datetime_y' : 'start_datetime'})
    columns = list(data.columns)
    columns.insert(0, 'rank')
    merged_data= merged_data[columns]
    merged_data = merged_data[columns].sort_values(by=['rank'])
    return merged_data
    

def get_time_series(URL=None):
    if URL is None:
        return None
    data = get_formatted_nasa_data(URL)
    top_data = analysis1(URL)
    top_data.index = top_data['start_datetime']
    markers = top_data.index.values
    data = data[['start_datetime','start_frequency']]
    data.index = data['start_datetime']
    del data['start_datetime']
    data = data[data['start_frequency'].str.contains('[^A-Za-z?]', na=False)]
    data=data.astype(int)
    data.plot(marker='o', color='r', markevery=markers)
    plt.show()
    return None

def main(url_1, url_2):
    print('Executing Step 1')
    data = get_replication(url_2)
    print(data.head(50))
    print('Executing Step 2')
    data = get_integration(url_1, url_2)
    print(data.head(100))
    print('Executing Step 3')
    get_time_series(url_2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url_1', default='https://www.spaceweatherlive.com/en/solar-activity/top-50-solar-flares')
    parser.add_argument('--url_2', default='https://cdaw.gsfc.nasa.gov/CME_list/radio/waves_type2.html')
    args = parser.parse_args()
    main(args.url_1, args.url_2)
