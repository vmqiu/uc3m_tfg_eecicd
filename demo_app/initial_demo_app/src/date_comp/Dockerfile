FROM python:3.10.5-slim
WORKDIR /date_comp
ENV FLASK_APP=date   
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY src/date_comp .

CMD [ "flask", "run", "--host=0.0.0.0" ]

