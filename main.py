from bokeh.server.server import Server
from tornado.web import RequestHandler
import tornado.ioloop
from tornado.options import define
from app.wind import wind_doc
from app.weather import weather_doc
from app.predict import PredictHandler
from app.lr_model import LRModel
from app.index import IndexHandler

if __name__ == '__main__':
    bokeh_app = {
        '/weather': weather_doc,
        '/wind': wind_doc
    }

    server = Server(bokeh_app, check_unused_sessions_milliseconds=500,
                    unused_session_lifetime_milliseconds=500,
                    allow_websocket_origin=["*"])
    server.start()

    setting = {
        'static_path': 'static',
        'template_path': 'templates'
    }

    # 缓存model
    lr = LRModel()
    define('model', lr.model)

    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/predict', PredictHandler)
    ], **setting)

    app.listen(8899)
    print("server start")
    tornado.ioloop.IOLoop.current().start()
