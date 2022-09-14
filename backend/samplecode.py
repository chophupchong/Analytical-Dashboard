def sample(app):
    from fastapi import FastAPI, Depends
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import db
    import json

    cred = credentials.Certificate("./serviceAccountKey.json")

    #Currently Firebase Realtime Database is linked to the bzacapstonechc firebase acc's proj
    default_app = firebase_admin.initialize_app(cred, {
        'databaseURL': "https://chcdashboard-default-rtdb.asia-southeast1.firebasedatabase.app"
    })

    ### The following code is a sample of how to interact with the firebase realtime database using python
    #The following code is a sample of how to read a file from .json and writing it to firebase realtime database

    #commented out
    # ref = db.reference("/")
    # with open("mock.json", "r") as f:
    #     file_contents = json.load(f)

    # ref.set(file_contents)

    #sample code for firebase push function
    #ref = db.reference("/")

    #commented out
    # ref = db.reference("/")
    # ref.set({
    # 	"Books":
    # 	{
    # 		"Best_Sellers": -1
    # 	}
    # })

    #commented out
    # ref = db.reference("/Books/Best_Sellers")
    # import json
    # with open("mock.json", "r") as f:
    # 	file_contents = json.load(f)

    # for key, value in file_contents.items():
    # 	ref.push().set(value)

    #The following code is a sample of reading from the db and updating the db

    #commented out
    # ref = db.reference("/Books/Best_Sellers/")
    # best_sellers = ref.get()
    # print("best_sellers")
    # print(best_sellers)
    # for key, value in best_sellers.items():
    # 	if(value["Author"] == "J.R.R. Tolkien"):
    # 		value["Price"] = 90
    # 		ref.child(key).update({"Price":80})

    #the following json rule was added to firebase realtime database security rules to allow to use the order_by_child method
        # "Books": {
        #   "Best_Sellers": {
        #       ".indexOn": ["Price"]
        #   }
    #reading from db with a query that orders by price

    #commented out
    # ref = db.reference("/Books/Best_Sellers/")
    # print("ordered by price")
    # print(ref.order_by_child("Price").get())

    ### The following code is a sample of how to interact with the firebase realtime database using python AND fastapi
    #app = FastAPI()

    @app.get("/")
    async def root():
        ref = db.reference("/Books/Best_Sellers/")
        #return {"message": "Hello World"}
        return ref.get() #this is all the data in Books/Best_Sellers

    ### using post
    #from typing import Optional
    from pydantic import BaseModel

    class Authorpriceinfo(BaseModel):
        name: str
        #description: Optional[str] = None
        price: int
        #tax: Optional[float] = None

    #example put request that will update the firebase db
    #u can verify the changes by using the get "/" request
    #just as a note, put is for UPDATE, post is for CREATE
    @app.post("/author_price/{author_name}")
    async def author_price(author_name: str, price: int):
        ref = db.reference("/Books/Best_Sellers/")
        best_sellers = ref.get()
        for key, value in best_sellers.items():
            if (value["Author"] == author_name):
                ref.child(key).update({"Price":price})
        return author_name + "'s book(s) set to $" +str(price)

    # class Authorpriceinfo(BaseModel):
    #     name: str
    #     #description: Optional[str] = None
    #     price: int
    #     #tax: Optional[float] = None
        
    #commented out code but this is the same put example except using post which is not the correct convention
    # @app.post("/author_price/")
    # async def author_price(authorpriceinfo: Authorpriceinfo):
    #     ref = db.reference("/Books/Best_Sellers/")
    #     best_sellers = ref.get()
    #     for key, value in best_sellers.items():
    #         if (value["Author"] == authorpriceinfo.name):
    #             ref.child(key).update({"Price":authorpriceinfo.price})
    #     return authorpriceinfo