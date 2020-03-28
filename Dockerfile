FROM python:3

RUN pip3 install --no-cache-dir opencv-python
RUN pip3 install --no-cache-dir matplotlib
RUN pip3 install --no-cache-dir pillow

RUN mkdir /src
WORKDIR /src
ADD . /src

CMD [ "python", "-u", "/src/main.py" ]
