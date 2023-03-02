import os
import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.web import StaticFileHandler
from controller.detect import DetectHandler
from controller.page import PageHandler

current_path = os.path.dirname(__file__)
settings = dict(
    debug=True,
    static_path=os.path.join(
        current_path, "dist/ocr") 
)

def make_app():
    return tornado.web.Application([
        (r"/api/detect/*", DetectHandler),
        (r"/", PageHandler),
        (r"/(.*)", StaticFileHandler,
         {"path": os.path.join(current_path, "dist/ocr"), "default_filename": "index.html"}),
    ], **settings)


if __name__ == "__main__":

    port = 80
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    # server.listen(port)
    server.bind(port)
    server.start(1)
    print(f'server is running: {port}')

    # tornado.ioloop.IOLoop.current().start()
    tornado.ioloop.IOLoop.instance().start()
