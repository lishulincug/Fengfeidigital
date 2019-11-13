#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pandas as pd
import yaml
from datetime import datetime
import time


class DataSource(object):

    def __init__(self, df):
        self.df = df

    @classmethod
    def from_excel(cls, file_name):
        df = pd.read_excel(file_name)
        return cls(df)

    def get_data_by_year(self, year):
        tmp = self.df
        tmp['date'] = pd.to_datetime(tmp['date'])
        return tmp[tmp['date'].dt.year == year]

    @property
    def data(self):
        return self.df


class WindSource(DataSource):
    pass


class WeatherSource(DataSource):

    @property
    def colors_map(self):
        with open('app/data/colors.yml', 'rb') as f:
            map_colors = yaml.load(f)
        return map_colors

    def boxs_for_year(self, year):
        return (
            time.mktime(datetime(year, 1, 1, 0, 0, 0).timetuple()) * 1000,
            time.mktime(datetime(year, 4, 1, 0, 0, 0).timetuple()) * 1000,
            time.mktime(datetime(year, 7, 1, 0, 0, 0).timetuple()) * 1000,
            time.mktime(datetime(year, 10, 1, 0, 0, 0).timetuple()) * 1000,
            time.mktime(datetime(year, 12, 31, 0, 0, 0).timetuple()) * 1000
        )

    def labels_for_year(self, year):
        return (
            time.mktime(datetime(year, 2, 15, 0, 0).timetuple()) * 1000,
            time.mktime(datetime(year, 5, 15, 0, 0, 0).timetuple()) * 1000,
            time.mktime(datetime(year, 8, 15, 0, 0, 0).timetuple()) * 1000,
            time.mktime(datetime(year, 11, 15, 0, 0, 0).timetuple()) * 1000,
        )

    def season_count(self, df):
        good_weather = bad_weather = 0
        series = df['weather']

        for i in range(len(series)):
            if '雨' in series.iloc[i] or \
                    '雪' in series.iloc[i] or \
                    '雾' in series.iloc[i] or \
                    '霾' in series.iloc[i]:
                bad_weather += 1
            else:
                good_weather += 1

        high = df['high'].max()
        low = df['low'].min()

        return [high, low, good_weather, bad_weather]

    def stat_by_year(self, year):
        data = self.get_data_by_year(year)
        spring = data[data['date'].dt.month < 4]
        summer = data[(data['date'].dt.month > 3) & (data['date'].dt.month < 7)]
        autumn = data[(data['date'].dt.month > 6) & (data['date'].dt.month < 10)]
        winter = data[data['date'].dt.month > 9]

        result = [[f'{year}-春'] + self.season_count(spring),
                  [f'{year}-夏'] + self.season_count(summer),
                  [f'{year}-秋'] + self.season_count(autumn),
                  [f'{year}-冬'] + self.season_count(winter)]

        title = ['season', 'high', 'low', 'good', 'bad']

        return pd.DataFrame(result, columns=title)
