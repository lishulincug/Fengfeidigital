from .datasource import WindSource
from bokeh.models import ColumnDataSource
from .graph3d import Surface3d
import datetime
import pandas as pd


def translate_data(df):
    result = []
    for i in range(len(df)):
        date = df.iloc[i]['date']
        y = df.iloc[i]['x']
        z = df.iloc[i]['y']
        color = df.iloc[i]['avg_strength']
        start = datetime.datetime(year=2011, month=1, day=1).strftime("%Y-%m-%d")
        delta = pd.to_datetime(date) - pd.to_datetime(start)

        result.append([delta.days, y, z, color])
    return pd.DataFrame(result, columns=['x', 'y', 'z', 'color'])


def wind_doc(doc):
    global start
    start = 2011
    ws = WindSource.from_excel('app/data/wind.xlsx')
    data = translate_data(ws.get_data_by_year(start))
    source = ColumnDataSource(data)
    surface = Surface3d(x="x", y="y", z="z", color='color', data_source=source, width=600, height=600)
    doc.title = '无锡市历史风向状况图'
    doc.add_root(surface)

    def update():
        global start
        start += 1
        if start == 2019:
            start = 2011
        data = translate_data(ws.get_data_by_year(start))
        source.data = ColumnDataSource(data).data

    doc.add_periodic_callback(update, 5000)
