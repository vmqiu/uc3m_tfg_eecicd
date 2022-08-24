FROM python:3.10.5-slim
WORKDIR /welcome_comp
ENV FLASK_APP=hello   
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY src/welcome_comp .

CMD [ "flask", "run", "--host=0.0.0.0" ]

