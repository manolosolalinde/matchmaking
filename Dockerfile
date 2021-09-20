FROM python:3

ENV APP_HOME /usr/src/app
WORKDIR $APP_HOME

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY .env ./

COPY . .

#Tip: Leave everything that can change for last

# This runs a flask application in localhost:5000
CMD [ "python", "./application.py" ]


## Test Locally
# docker build . -t gcr.io/nms-small-apps/matchmaking
# docker run -it --rm --name matchmaking -p 5000:5000  gcr.io/nms-small-apps/matchmaking
