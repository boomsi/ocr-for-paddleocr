import json
import time

import tornado.web

# from detect.main import detect, filter_by_table
from detect.main_class import Detect


class DetectHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        img = self.get_argument("img", None, True)
        obj = Detect.default(img)
        print(obj.final_data)
        self.finish(json.dumps(obj.final_data))

    @tornado.gen.coroutine
    def post(self):
        start_time = time.time()
        img = self.request.files.get('file', None)

        # obj = Detect(img[0].body)
        obj = Detect.default(img[0].body)

        self.finish(json.dumps(
            {'code': 200,
             'msg': '成功',
             'data': {
                 'img_detected': '',
                 'raw_out': obj.final_data,
                 'source_data': obj.source_data,
                 'speed_time': round(time.time() - start_time, 2)
                }
             }
        ))
