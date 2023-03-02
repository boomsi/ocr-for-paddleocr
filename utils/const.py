from enum import Enum

filter_text_re = '\?|·|●|&'  # 特殊符号过滤

MIN_DETECT_CONFIDENCE = 0.8  # 数据可信度最低值
Y_ERROR = 15  # y 轴误差，在误差范围内，视为一行
X_ERROR = 10  # x 轴误差，在误差范围内，视为一列
MIN_ROWS = 3  # 最小行数
MIN_COLUMNS = 2  # 最小列数


class Detail(Enum):
    BEGIN_ROWS_UNENOUGHT = '（初始数据）行数少于3'
    NOT_REGULAR_TABLE = '非（规则）表格'
    FINAL_ROWS_UNENOUGHT = '（最终数据）行数少于3'
    COLUMNS_UNENOUGHT = '列数少于2'
