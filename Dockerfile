FROM frolvlad/alpine-python-machinelearning

EXPOSE 8899 5006

WORKDIR /app

ADD . /app

RUN echo "https://mirror.tuna.tsinghua.edu.cn/alpine/v3.8/main/" > /etc/apk/repositories

RUN apk add --no-cache nodejs

RUN pip install -r requirements.txt -i https://pypi.douban.com/simple/

CMD ["python", "main.py"]