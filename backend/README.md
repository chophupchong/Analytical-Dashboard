## Getting Started

## Compile Jsons in backend root folder

1. serviceAccountKey.json
2. youtubeAccessTokens.json
3. instagramAccessTokens.json
4. facebookAccessTokens.json

## Run

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

1. Access Tokens to be retrieved from the frontend to call the functions
Storing credentials in json file

## References

Refered to these

https://www.freecodecamp.org/news/how-to-get-started-with-firebase-using-python/
https://firebase.google.com/docs/database/admin/start#python

Git Secrets
https://cloud.google.com/blog/products/identity-security/help-keep-your-google-cloud-service-account-keys-safe
