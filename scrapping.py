from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import requests
import argparse



def get_Space_weather_data(URL=None, columns=['rank','x_class','date','region','start_time','max_time','end_time','movie']):
    if URL is None:
        return None
    page = requests.get(URL)
    soup = bs(page.text, 'lxml')
    soup.prettify()
    solar_flare = soup.find('table', {'class':'table table-striped table-responsive-md'})
    df = pd.read_html(str(solar_flare))[0]
    df.columns = columns
    return df


def get_top50_space_weather_data(df=None):
    if(df is None):
        return None
    df = df.copy()
    df = df.drop(df.columns[df.columns.size-1], axis=1)
    df['start_time'] = df['date'] + ' ' + df['start_time']
    df['max_time'] = df['date'] + ' ' + df['max_time']
    df['end_time'] = df['date'] + ' ' + df['end_time']
    columns = df.columns[df.columns.str.contains('time')]
    df[columns] = df[columns].applymap(lambda x: pd.to_datetime(x))
    df.columns = df.columns.str.replace('time','datetime')
    df['region'].replace('-', np.NaN)
    df = df[['rank', 'x_class', 'start_datetime', 'max_datetime','end_datetime','region']]
    return df

def get_nasa_data(URL=None, columns=['start_date', 'start_time', 'end_date', 'end_time', 'start_frequency', 
                             'end_frequency', 'flare_location', 'flare_region', 'flare_classification', 
                             'cme_date', 'cme_time', 'cme_angle', 'cme_width', 'cme_speed']):
    if URL is None:
        return None
    data = []
    page = requests.get(URL)
    soup = bs(page.text, 'lxml')
    rows = soup.find('pre').text.split('\n')
    rows = rows[12:len(rows)-3]
    for row in rows:
        values = row.split(' ')
        values = [x for x in values if x]
        values = values[0:14]
        data.append(values)
    return pd.DataFrame(data=data, columns=columns)

def get_formatted_nasa_data(URL=None, columns=['start_datetime', 'end_datetime', 'start_frequency', 'end_frequency', 
                             'flare_location',  'flare_region', 'importance', 'cme_datetime',
                             'cpa', 'width', 'speed',  'plot']):
    if URL is None:
        return None
    data = []
    page = requests.get(URL)
    soup = bs(page.text, 'lxml')
    rows = soup.find('pre').text.split('\n')
    rows = rows[12:len(rows)-3]
    indexes = [0,1,2,3,9,10]
    for row in rows:
        row_list = []
        values = row.split(' ')
        values = [x for x in values if x]
        year = values[0].split(' ')[0].split('/')[0]
        start_time = pd.to_datetime(values[0].replace('/' , '-') + ' ' + values[1] + ':00')
        end_time = year + '-' + values[2].replace('/' , '-') + ' ' + values[3] + ':00'
        if '-' not in values[9]:
            cme_time = year + '-' + values[9].replace('/' , '-') + ' ' + values[10] + ':00'
        else:
            cme_time = 'na'
        row_list.append(start_time)
        row_list.append(end_time)
        row_list.append(cme_time)
        for index in sorted(indexes, reverse=True):
            del values[index]
        for val in values:
            if '-' in val:
                row_list.append('na')
            else:
                row_list.append(val)
        row_list = row_list[0:12]
        row_list.insert(7, row_list.pop(2))
        data.append(row_list)
    data = pd.DataFrame(data=data, columns=columns)
    data = data.replace('na', np.NaN)
    data['is_halo'] = data.apply(is_halo, axis=1)
    data = data.replace('Halo', np.NaN)
    data['width_lower_bound'] = data.apply(is_lower, axis=1)
    data['width'] = data.width.replace({'>':' '}, regex=True)
    return data

def is_halo(row):
    if row['cpa'] == 'Halo':
        return True
    return False

def is_lower(row):
    if '>' in str(row['width']):
        return True
    return False

def main(url_1, url_2):
    print('Executing Step 1')
    data = get_Space_weather_data(url_1)
    print(data.head(50))
    print('Executing Step 2')
    data = get_top50_space_weather_data(data)
    print(data.head(100))
    print('Executing Step 3')
    data = get_nasa_data(url_2)
    print(data.head(100))
    print('Executing Step 4')
    data = get_formatted_nasa_data(url_2)
    print(data.head(100))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url_1', default='https://www.spaceweatherlive.com/en/solar-activity/top-50-solar-flares')
    parser.add_argument('--url_2', default='https://cdaw.gsfc.nasa.gov/CME_list/radio/waves_type2.html')
    args = parser.parse_args()
    main(args.url_1, args.url_2)



            










    

    

