#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure, curdoc
from bokeh.models import BoxAnnotation, LabelSet
from bokeh.models.formatters import DatetimeTickFormatter, PrintfTickFormatter
from bokeh.layouts import column, row
from bokeh import layouts
from bokeh.models.widgets import Button, DataTable, TableColumn
from .datasource import WeatherSource
from math import pi


def make_labels_dataset(dp, year):
    labels = dp.labels_for_year(year)

    labels = {
        "x": [labels[0], labels[1], labels[2], labels[3]],
        "y": [40, 40, 40, 40],
        "text": ["春", "夏", "秋", "冬"]
    }

    return ColumnDataSource(labels)


def make_dataset(dp, year):
    df = dp.get_data_by_year(year)
    return ColumnDataSource(df)


def make_weather_plot(dp):
    colors_map = dp.colors_map
    weathers = list(colors_map.keys())
    colors = list(colors_map.values())
    source = ColumnDataSource(data=dict(weather=weathers, counts=[1 for i in range(len(weathers))], color=colors))
    p = figure(x_range=weathers, y_range=(0, 1), plot_height=250, title="天气颜色对照图",
               toolbar_location=None, tools="")
    p.vbar(x='weather', top='counts', width=0.9, color='color', source=source)
    p.xaxis.major_label_orientation = pi / 4
    p.yaxis.visible = False
    return p


def make_plot(year, c1, c2, boxs):
    p1 = figure(x_axis_type='datetime', plot_width=1000, plot_height=400, title=f"无锡天气状况图: {year}", y_range=(-10, 45),
                toolbar_location=None, tools="")
    p1.xaxis.formatter = DatetimeTickFormatter(days=["%Y-%m"])
    p1.xaxis.axis_label = '时间'
    p1.xaxis.major_label_orientation = pi / 4
    p1.xgrid.visible = False
    p1.yaxis.formatter = PrintfTickFormatter(format="%d℃")
    p1.yaxis.axis_label = '气温'

    labels = LabelSet(x='x', y='y', text='text', source=c1)
    p1.vbar(x='date', width=0, top='high', bottom='low', color='color', source=c2)

    p1.add_layout(labels)

    box1 = BoxAnnotation(left=boxs[0], right=boxs[1], fill_alpha=0.1, fill_color="lightcyan")
    box2 = BoxAnnotation(left=boxs[1], right=boxs[2], fill_alpha=0.1, fill_color="papayawhip")
    box3 = BoxAnnotation(left=boxs[2], right=boxs[3], fill_alpha=0.1, fill_color="lightpink")
    box4 = BoxAnnotation(left=boxs[3], right=boxs[4], fill_alpha=0.1, fill_color="mintcream")

    p1.add_layout(box1)
    p1.add_layout(box2)
    p1.add_layout(box3)
    p1.add_layout(box4)

    return p1


def make_stat_table(source):
    columns = [
        TableColumn(field='season', title="季节"),
        TableColumn(field='high', title="最高温度"),
        TableColumn(field="low", title="最低温度"),
        TableColumn(field="good", title="适合出行"),
        TableColumn(field="bad", title="不适合出行"),
    ]

    stat_table = DataTable(source=source, columns=columns, width=400, height=200)
    return stat_table


def make_combo():
    dp = WeatherSource.from_excel("app/data/weather.xlsx")
    c1 = make_labels_dataset(dp, 2011)
    c2 = make_dataset(dp, 2011)
    boxs = dp.boxs_for_year(2011)

    slider = Slider(start=2011, end=2018, value=2011, step=1, title="year")
    button = Button(label="► Play", button_type='danger', width=50)

    p1 = make_weather_plot(dp)
    p2 = make_plot(2011, c1, c2, boxs)

    table_source = ColumnDataSource(dp.stat_by_year(2011))
    stat_table = make_stat_table(table_source)

    c = column(p2, column(row(p1, column(row(slider, button), stat_table))))

    def slider_callback(attr, old, new):
        year = slider.value
        n_c1 = make_labels_dataset(dp, year)
        n_c2 = make_dataset(dp, year)
        boxs = dp.boxs_for_year(year)
        c.children[0] = make_plot(year, n_c1, n_c2, boxs)
        table_source.data = table_source.from_df(dp.stat_by_year(year))

    slider.on_change('value', slider_callback)

    def animate_update():
        year = slider.value + 1
        if year > 2018:
            year = 2011
        slider.value = year

    callback_id = None

    def animate():
        global callback_id
        if button.label == '► Play':
            button.label = '❚❚ Pause'
            callback_id = curdoc().add_periodic_callback(animate_update, 2000)
        else:
            button.label = '► Play'
            curdoc().remove_periodic_callback(callback_id)

    button.on_click(animate)
    return c


def weather_doc(doc):
    _layout = layouts.layout(make_combo())
    doc.title = "无锡市历史天气状况图"
    doc.add_root(_layout)
