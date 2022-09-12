# chc-app

Social Media Analytical Dashboard

## Technologies Used

1. VueJS 3
2. Firebase
3. Flask
4. FastAPI
5. Python
6. Javascript

## Getting Started

Open up two VSCs and cd into respective directories to run.

### Create your environment file

1. cd into /frontend
2. Retrieve your credentials from firebase
3. Create .env file in frontend and input your following credentials

```bash
FIREBASE_API_KEY="VUE_APP_XXX"
AUTH_DOMAIN="VUE_APP_XXX"
DATABASE_URL="VUE_APP_XXX"
PROJECT_ID="VUE_APP_XXX"
STORAGE_BUCKET="VUE_APP_XXX"
MESSAGING_SENDER_ID="VUE_APP_XXX"
APP_ID="VUE_APP_XXX"
MEASUREMENT_ID="VUE_APP_XXX"
```

## to-dos

integrate firestore into frontend

## Research

Switching flask to fastapi

https://medium.com/@calebkaiser/why-we-switched-from-flask-to-fastapi-for-production-machine-learning-765aab9b3679

tldr :

1. flask has no native async support
2. FastAPI outperforms Flask by 300&

framework and machine learning with fastapi

https://medium.com/@8B_EC/tutorial-serving-machine-learning-models-with-fastapi-in-python-c1a27319c459
