# run with bash deploy.sh
gcloud builds submit --tag gcr.io/nms-small-apps/matchmaking --project nms-small-apps
    # ALTERNATIVELY YOU CAN:
        ## step1) building
        # docker build . -t gcr.io/nms-small-apps/matchmaking
        ## step2) Upload to google cloud repository
        # docker push gcr.io/nms-small-apps/matchmaking
# Deploy to Cloud Run
gcloud config set run/region us-central1
gcloud run deploy matchmaking --image gcr.io/nms-small-apps/matchmaking --platform managed --port=5000 --project nms-small-apps --allow-unauthenticated