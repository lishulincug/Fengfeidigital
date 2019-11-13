from bokeh.core.properties import Instance, String
from bokeh.models import ColumnDataSource, LayoutDOM

JS_CODE = """
import * as p from "core/properties"
import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"

OPTIONS =
  width:  '600px'
  height: '600px'
  style: 'dot-color'
  showPerspective: true
  showGrid: true
  keepAspectRatio: true
  verticalRatio: 1.0
  legendLabel: '风力等级'
  cameraPosition:
    horizontal: -0.35
    vertical: 0.22
    distance: 1.8
  dotSizeRatio: 0.01
  xValueLabel: (value)->
    return vis.moment("2011-01-01").add(value, 'days').format("YYYY-MM-DD")
  xLabel: '时间'
  yLabel: '东 / 西'
  zLabel: '北 / 南'
  valueMax: 5
  valueMin: 3


export class Surface3dView extends LayoutDOMView

  initialize: (options) ->
    super(options)

    url = "http://visjs.org/dist/vis.js"

    script = document.createElement('script')
    script.src = url
    script.async = false
    script.onreadystatechange = script.onload = () => @_init()
    document.querySelector("head").appendChild(script)

  _init: () ->
    @_graph = new vis.Graph3d(@el, @get_data(), OPTIONS)

    @connect(@model.data_source.change, () =>
        @_graph.setData(@get_data())
    )

  get_data: () ->
    data = new vis.DataSet()
    source = @model.data_source
    for i in [0...source.get_length()]
      data.add({
        x:     source.get_column(@model.x)[i]
        y:     source.get_column(@model.y)[i]
        z:     source.get_column(@model.z)[i]
        style: source.get_column(@model.color)[i]
      })
    return data

export class Surface3d extends LayoutDOM

  default_view: Surface3dView

  type: "Surface3d"

  @define {
    x:           [ p.String           ]
    y:           [ p.String           ]
    z:           [ p.String           ]
    color:       [ p.String           ]
    data_source: [ p.Instance         ]
  }
"""


class Surface3d(LayoutDOM):
    __implementation__ = JS_CODE

    data_source = Instance(ColumnDataSource)

    x = String
    y = String
    z = String
    color = String
