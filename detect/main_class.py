
import re
from paddleocr import PaddleOCR
from functools import cmp_to_key
from utils.const import Detail, MIN_ROWS, MIN_COLUMNS, MIN_DETECT_CONFIDENCE, X_ERROR, Y_ERROR, filter_text_re

ocr = PaddleOCR(use_angle_cls=False, use_gpu=True, lang="ch")


class Detect():
    source_data = []
    final_data = []
    img = None
    position = ''

    # @property
    # def final_data(cls):
    #     return cls.final_data

    # @final_data.setter
    # def final_data(cls, val):
    #     print(111, len(val))

    @classmethod
    def default(cls, img):
        print('>>> Start')
        cls.img = img
        cls._init_data()

        cls.row_group_and_column_sort()

        cls.drop_rows_useless_item()

        cls.cut_rows_area()

        cls._collect_data()

        return cls

    @classmethod
    def _init_data(cls):
        lists = ocr.ocr(cls.img, cls=False)[0]
        final = []

        for item in lists:
            msg = list(item[1])

            if msg[1] < MIN_DETECT_CONFIDENCE:
                continue

            text = re.sub(filter_text_re, ' ', msg[0], 0, 0)
            lt, rt, _, lb = item[0]
            item[0].append([(rt[0] - lt[0]) / 2 + lt[0],
                            (lb[1] - lt[1]) / 2 + lt[1]])

            item_dict = {'polygon': item[0],
                         'text': text, 'confidence': msg[1]}
            final.append(item_dict)
        cls.source_data = final
        cls.final_data = final
        return final

    @classmethod
    def row_group_and_column_sort(cls):
        '''行分组 每行每项按照 x轴 排序（存在多行文本因高度不同位置会错开）'''
        y = 0
        row_group = []
        for row in cls.final_data:
            _, row_y = row['polygon'][-1]
            if (len(row_group) > 0) and (row_y - y <= Y_ERROR):
                row_group[-1].append(row)
            else:
                row_group.append([row])
            y = row_y

        list(map(lambda x: x.sort(key=cmp_to_key(
            lambda y, z: y['polygon'][0][0] - z['polygon'][0][0])), row_group))

        if len(row_group) < MIN_ROWS:
            cls.final_data = [Detail.BEGIN_ROWS_UNENOUGHT.value]
        else:
            cls.final_data = row_group
        return row_group

    @classmethod
    def drop_rows_useless_item(cls):
        '''根据众数 移除每行左侧无效数据项
        '''
        mode_num = cls.get_table_align(cls.final_data)

        if mode_num == None:
            cls.final_data = [Detail.NOT_REGULAR_TABLE.value]
        else:
            new_row_group = []
            useless_row_group = []  # 舍弃数据
            for item in cls.final_data:
                k = list((j for j, x in enumerate(item)
                          if abs((x['polygon'][0][0] if cls.position == 'left' else x['polygon'][-1][0]) - mode_num) < X_ERROR))
                if len(k) > 0:
                    new_row_group.append(item[k[0]:])
                else:
                    useless_row_group.append(item)
            cls.final_data = new_row_group
        return new_row_group

    @classmethod
    def cut_rows_area(cls):
        '''确定 表格的上下区间 截取有效区域
        '''
        frag = True
        x_area = [-1, -1]
        final = []
        for i, item in enumerate(cls.final_data):
            if len(item) < MIN_COLUMNS:
                if frag:
                    x_area[0] = i
                else:
                    x_area[1] = i
                    # break;
            else:
                frag = False
        else:
            if x_area[1] + 1 < len(cls.final_data):
                x_area[1] = -1

        if sum(x_area) > -2:
            if (len(cls.final_data) - x_area[0] < MIN_ROWS
                        or (x_area[1] > 0 and x_area[1] < MIN_ROWS)
                        or (x_area[0] >= 0 and x_area[1] >= 0 and x_area[1] - x_area[0] - 1 < MIN_ROWS)
                    ):
                final = [Detail.FINAL_ROWS_UNENOUGHT.value]
            else:
                final = cls.final_data[x_area[0] + 1: x_area[1]] if (x_area[0] >= 0 and x_area[1]) >= 0 else (
                    cls.final_data[x_area[0]+1:] if x_area[0] >= 0 else cls.final_data[:x_area[1]])
            cls.final_data = final
        return final

    @classmethod
    def _collect_data(cls):
        final = list(
            map(lambda i: list(map(lambda j: j['text'], i)), cls.final_data))
        cls.final_data = final
        return final

    @classmethod
    def get_table_align(cls, row_group):
        '''判断是左对齐还是居中对齐，返回响应对齐方式的众数
        '''
        lt_x_list = list(map(lambda x: x[0]['polygon'][0][0], row_group))
        c_x_list = list(map(lambda x: x[0]['polygon'][-1][0], row_group))
        lt_x_mode_num = cls.get_mode(lt_x_list, X_ERROR)  # x轴lt众数
        c_x_mode_num = cls.get_mode(c_x_list, X_ERROR)  # x轴c众数
        if cls.noneToInt(lt_x_mode_num[1]) > cls.noneToInt(c_x_mode_num[1]):
            mode_num = lt_x_mode_num[0]
            cls.position = 'left'
        else:
            mode_num = c_x_mode_num[0]
            cls.position = 'center'
        return mode_num

    @classmethod
    def get_mode(cls, lists, standrad):
        '''获取列表中的众数(在误差范围内)
        @return 
            (众数, 出现次数)
        '''

        try:
            final_couple = {lists[0]: 1}
            for i in lists[1:]:
                keys = final_couple.keys()
                old = list((j for j in keys if abs(j - i) <= standrad))

                if len(old) == 1:
                    final_couple[old[0]] += 1
                else:
                    final_couple[i] = 1

            max_couple = [0, 0]
            for key in final_couple:
                if final_couple[key] > max_couple[1]:
                    max_couple[1] = final_couple[key]
                    max_couple[0] = key
            return max_couple if max_couple[1] >= MIN_ROWS else [None, None]
        except:
            return [None, None]

    @classmethod
    def noneToInt(cls, value):
        return 0 if value == None else value
