FROM python:3

ENV APP_HOME /usr/src/app
WORKDIR $APP_HOME

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#Tip: Leave everything that can change for last

# This runs a flask application in localhost:5000
CMD [ "python", "./application.py" ]