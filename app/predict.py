from tornado.web import RequestHandler
from tornado.options import options
import datetime
import requests
import re
from math import sqrt
from functools import reduce


class PredictHandler(RequestHandler):

    def get(self, *args, **kwargs):

        try:

            r = requests.get("http://wthrcdn.etouch.cn/weather_mini?citykey=101190201", timeout=5)
            high = r.json()['data']['yesterday']['high']
            low = r.json()['data']['yesterday']['low']
            wind_dire = r.json()['data']['yesterday']['fx']
            wind_strength = r.json()['data']['yesterday']['fl']
            yesterday = datetime.datetime.now() + datetime.timedelta(days=-1)

            high = int(re.search(r'\d+', high)[0])
            low = int(re.search(r'\d+', low)[0])
            x = y = 0
            for ch in wind_dire:
                if '东' == ch:
                    x += 1
                elif '南' == ch:
                    y -= 1
                elif '西' == ch:
                    x -= 1
                elif '北' == ch:
                    y += 1

            _strength = re.findall(r'\d', wind_strength)
            avg_streng = reduce(lambda a, b: a + b, map(lambda x: int(x), _strength)) / len(_strength)
            data = [high, low, yesterday.year, yesterday.month, yesterday.day, sqrt(pow(x, 2) + pow(y, 2)), avg_streng]
            result = options.model.predict([data])
            return self.write(
                {
                    'status': 200,
                    'data': int(list(result)[0]),
                    'msg': ""
                })

        except Exception as e:
            return self.write({'status': 500,
                               'data': "",
                               'msg': str(e)})
