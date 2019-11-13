import pandas as pd
import yaml
import re
from math import sqrt
from functools import reduce
import numpy as np


class Vector(object):
    def __init__(self):
        self._x = 0
        self._y = 0

    def cal_direction(self, direction):
        if direction == '东':
            self.x += 1

        elif direction == '南':
            self.y -= 1

        elif direction == '西':
            self.x -= 1

        elif direction == '北':
            self.y += 1

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, value):
        self._x = value

    @y.setter
    def y(self, value):
        self._y = value

    def reset(self):
        self.x = 0
        self.y = 0


class WeatherSolution(object):

    def __init__(self):
        """ inFile(format: '.xlsx')
        """

        self.df = pd.read_excel('无锡市历史天气预报数据.xlsx',
                                sheet_name=[8])[8]

    def weather_parse(self):

        result = []
        degree_rule = re.compile(r'(^[\-|0-9][0-9]*)℃')

        for i in range(len(self.df)):
            date = self.df.iloc[i]['日期'].strftime("%Y-%m-%d")
            weather = self.df.iloc[i]['天气状况']
            temp = self.df.iloc[i]['气温']

            if '小雨-中雨' in weather:
                weather = weather.replace('小雨-中雨', '小到中雨')

            weathers = weather.split('/')

            r1 = self.hex2rgb(self.colors_map[weathers[0].strip()])
            r2 = self.hex2rgb(self.colors_map[weathers[1].strip()])
            mix = self.color_mix(r1, r2, 50)

            degrees = temp.split('/')

            high = degrees[0].strip()
            low = degrees[1].strip()

            _high = degree_rule.search(high)
            _low = degree_rule.search(low)

            if _high and _low:
                high_value = int(_high[1])
                low_value = int(_low[1])

            result.append((date, high_value, low_value, weather, mix))

        return pd.DataFrame(result, columns=['date', 'high', 'low', 'weather', 'color'])

    def hex2rgb(self, hexString):
        _hex = '0x' + hexString[1:]
        hexcolor = int(_hex, 16)

        rgb = [(hexcolor >> 16) & 0xff,
               (hexcolor >> 8) & 0xff,
               hexcolor & 0xff
               ]
        return rgb

    def rgb2hex(self, rgbcolor):
        r, g, b = rgbcolor
        _hex = hex((r << 16) + (g << 8) + b)
        return '#' + _hex[2:]

    def color_mix(self, R1, R2, alpha):
        """ R1 (r, g, b)
            R2 (r, g , b)
            alpha 0~100
        """
        r1, g1, b1 = R1
        r2, g2, b2 = R2
        mix = (
            int((r1 * (100 - alpha) + r2 * alpha) / 100),
            int((g1 * (100 - alpha) + g2 * alpha) / 100),
            int((b1 * (100 - alpha) + b2 * alpha) / 100)
        )
        return self.rgb2hex(mix)

    @property
    def colors_map(self):
        with open('colors.yml', 'rb') as f:
            map_colors = yaml.load(f)
        return map_colors


class WindSolution(object):

    def __init__(self):
        self.df = pd.read_excel('无锡市历史天气预报数据.xlsx',
                                sheet_name=[8])[8]

    def wind_parse(self):
        result = []
        original = Vector()
        flag = 2011

        for i in range(len(self.df)):

            date = self.df.iloc[i]['日期'].strftime("%Y-%m-%d")

            if flag < pd.to_datetime(date).year:
                flag = pd.to_datetime(date).year
                original.reset()

            wind = self.df.iloc[i]['风力风向']

            axis = self.get_direction(wind, original)
            avg_strength = self.get_avg_wind_strength(wind)

            result.append([date, axis.x, axis.y, avg_strength])

        title = ['date', 'x', 'y', 'avg_strength']
        return pd.DataFrame(result, columns=title)

    def get_direction(self, string, vector):
        part1, part2 = string.split('/')

        direction_list = ['东', '南', '西', '北']
        for ch in part1:
            if ch in direction_list:
                vector.cal_direction(ch)

        for ch in part2:
            if ch in direction_list:
                vector.cal_direction(ch)

        return vector

    def get_avg_wind_strength(self, string):
        rule = r'\d'
        num_list = re.findall(rule, string)

        nums = list(map(lambda x: int(x), num_list))
        return sum(nums) / len(nums)


class MlSolution(object):
    def __init__(self):
        self.df = pd.read_excel('无锡市历史天气预报数据.xlsx',
                                sheet_name=[8])[8]

    def parse(self):
        df = self.df
        df.columns = ['date', 'weather', 'temp', 'wind']
        df.weather = df.weather.apply(lambda x: 0 if '雨' in x
                                                     or '雾' in x
                                                     or '霾' in x
                                                     or '雪' in x else 1)
        df['high'] = pd.Series(map(lambda x: re.search(r'\d+', x.split('/')[0])[0], df['temp'].values))
        df['low'] = pd.Series(map(lambda x: re.search(r'\d+', x.split('/')[1])[0], df['temp'].values))

        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        stength_list = []
        dire_list = []
        for i in range(len(df)):
            tmp = df.iloc[i]['wind']
            x = y = 0

            for ch in tmp:
                if ch == '东':
                    x += 1
                elif ch == '南':
                    y -= 1
                elif ch == '西':
                    x -= 1
                elif ch == '北':
                    y += 1

            dire_list.append(sqrt(pow(x, 2) + pow(y, 2)))
            try:
                tmp_list = re.findall(r'(\d)-(\d).*(\d)-(\d)', tmp)[0]
            except:
                tmp_list = [0]
            stength_list.append(reduce(lambda a, b: a + b, map(lambda x: int(x), tmp_list)) / len(tmp_list))

        df['wind_dire'] = pd.Series(dire_list)
        df['wind_strength'] = pd.Series(stength_list)
        df.drop(['date', 'temp', 'wind'], axis=1, inplace=True)
        df['high'] = df['high'].astype(int)
        df['low'] = df['low'].astype(int)

        good_index = df[df['weather'] == 1].index
        good_random = np.random.choice(good_index,
                                       800,
                                       replace=False)
        bad_index = df[df['weather'] == 0].index
        bad_random = np.random.choice(bad_index,
                                      800,
                                      replace=False)
        return pd.concat([df.loc[good_random], df.loc[bad_random]])


def generate_weather():
    s = WeatherSolution()
    df = s.weather_parse()

    writer = pd.ExcelWriter("weather.xlsx")
    df.to_excel(writer, index=False)
    writer.save()


def generate_wind():
    s = WindSolution()
    df = s.wind_parse()
    writer = pd.ExcelWriter("wind.xlsx")
    df.to_excel(writer, index=False)
    writer.save()


def generate_ml():
    s = MlSolution()
    df = s.parse()
    writer = pd.ExcelWriter("ml.xlsx")
    df.to_excel(writer, index=False)
    writer.save()


if __name__ == '__main__':
    generate_weather()
    generate_wind()
    generate_ml()
