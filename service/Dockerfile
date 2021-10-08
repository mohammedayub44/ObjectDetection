FROM python:3.6.9

# RUN apt-get update && \
#         apt-get install -y software-properties-common && \
#         add-apt-repository ppa:deadsnakes/ppa && \
#         apt-get update -y  && \
#         apt-get install -y build-essential python3.6 python3.6-dev python3-pip && \
#         apt-get install -y git  && \
#         # update pip
#         python3.6 -m pip install pip --upgrade && \
#         python3.6 -m pip install wheel && \
RUN mkdir -p /usr/src/app && \
    mkdir -p /usr/src/app/images/heatmaps && \
    mkdir -p /usr/src/app/images/snapshots && \
    mkdir -p /usr/src/app/serving_models && \
    mkdir -p /usr/src/app/data

WORKDIR /usr/src/app

COPY requirements.txt swagger.yaml /usr/src/app/

RUN pip install -r requirements.txt && \
    chmod -R +x /usr/src/app 

COPY ./service/* /usr/src/app/service/
COPY ./serving_models/classify_model.pkl /usr/src/app/serving_models/classify_model.pkl
COPY ./data/occupantLoadFactor.csv /usr/src/app/data/occupantLoadFactor.csv

WORKDIR /usr/src/app/service/

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]