## Getting Started

## Create your .env file again

Retrieve your service account key from Firebase console

1. Settings
2. Service accounts
3. Under Firebase Admin SDK, generate new private key

**NOTE**

## Do not expose your serviceAccountKey.json

I have created a service account key json sample.
After generating your private key, it should be a json file.
Paste and rename the json file to "serviceAccountKey.json"

run

```bash

pip install -r requirements.txt

uvicorn main:app --reload

alternate commands:
pip install --user -r requirements.txt
python -m uvicorn main:app --reload
```

## See API documentation

http://localhost:8000/docs

## to-dos

deployment on deta?
https://fastapi.tiangolo.com/uk/deployment/deta/

## References

Refered to these

https://www.freecodecamp.org/news/how-to-get-started-with-firebase-using-python/
https://firebase.google.com/docs/database/admin/start#python

Git Secrets
https://cloud.google.com/blog/products/identity-security/help-keep-your-google-cloud-service-account-keys-safe
