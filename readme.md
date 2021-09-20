# MatchMaking

An application to balance team players for a match.

# Steps to run:

1) Start a postgresql server

2) Create a .env file with the following content

```.env
DATABASE_URL="postgres://postgres:<password>@<databaseurl>:5432/mydatabase"
```

3) Run:
```powershell
python create.py
python import.py
flask run
```

Cloud Run instance:

Commands to build
```powershell
# Build and push to remote repository
gcloud builds submit --tag gcr.io/nms-small-apps/matchmaking --project nms-small-apps
    # ALTERNATIVELY YOU CAN:
        ## step1) building
        # docker build . -t gcr.io/proj/matchmaking
        ## step2) Upload to google cloud repository
        # docker push gcr.io/proj/matchmaking
# Deploy to Cloud Run
gcloud config set run/region us-central1
gcloud run deploy --image gcr.io/nms-small-apps/matchmaking --platform managed --port=5000
```