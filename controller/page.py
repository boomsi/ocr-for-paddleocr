import os

import tornado.web

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class PageHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        self.render(os.path.join(
            BASE_PATH, 'dist/ocr/index.html'))
