FROM python:3.8

WORKDIR /usr/local/src

COPY . ./

RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && \
    apt-get update && apt-get install libgl1 -y
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

CMD ["python", "main.py"]

