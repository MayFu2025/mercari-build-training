import os
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import json
from library import DatabaseWorker

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [os.environ.get("FRONT_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

db = DatabaseWorker('mercari.sqlite3')


# GET endpoint
@app.get("/")
def root():
    return {"message": "Hello, world!"}


# function to save given item into json file
def save_json(new_item, filename='items.json'):
    if os.path.exists(filename):
        with open(filename, 'r+') as file:
            file_data = json.load(file)
            file_data["items"].append(new_item)
            file.seek(0)
            json.dump(file_data, file, indent=4)
    else:
        with open(filename, 'w') as file:
            json.dump({"items": [new_item]}, file, indent=4)


# function to save given image into images file
def save_image(image_bytes, image_name):
    path = os.path.join("images", image_name)
    with open(path, "wb") as image:
        image.write(image_bytes)


# POST endpoint for /items
@app.post("/items")
def add_item(name: str = Form(), category: str = Form(), image: UploadFile = File()):
    # (3-4) Save image to directory
    image_bytes = image.file.read()
    image_name = f"{hashlib.sha256(image_bytes).hexdigest()}.jpg"
    save_image(image_bytes, image_name)

    # (3-2) Save item to json
    # item = {"name": name, "category": category, "image_name": image_name}
    # save_json(new_item=item)
    #
    # logger.info(f"Received item: {name}, {category}, {image_name}")
    # return {"message": f"item received: {item}"}

    # (4-1) Save item to db
    query = f"INSERT into items(name, category, image_name) values('{name}', '{category}', '{image_name}')"
    db.run_query(query)
    add_category(category)
    return {"message": f"item received: {name}"}



# (3-3) GET endpoint for /items
@app.get("/items")
def get_items_list(filename='items.json'):
    # with open(filename, 'r') as file:
    #     file_data = json.load(file)
    # return {"message": file_data}

    # (4-1) New GET endpoint for /items
    query = f'''SELECT * from items'''
    items = db.search(query, multiple=True)
    return {"message": items}


# (3-5) GET endpoint for /items/{item_id}
@app.get("/items/{item_id}")
def get_item_id(item_id: int):
    with open('items.json', 'r') as file:
        file_data = json.load(file)
        items_list = file_data["items"]
    if 0 <= item_id <= len(items_list):
        return {"message": items_list[item_id]}
    else:
        raise HTTPException(status_code=404, detail="Index out of range")


# (3-6) Displaying Debug Log
@app.get("/image/{image_name}")
async def get_image(image_name):
    # Create image path
    image = images / image_name

    if not image_name.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)


# (4-1) Move json to db (Run once)
# query = '''create table if not exists items(
#     id integer primary key,
#     name text,
#     category text,
#     image_name text)'''
# db.run_query(query)
#
# with open('items.json', 'r') as file:
#     item_list = json.load(file)["items"]
#     for item in item_list:
#         query = f"INSERT into items(name, category, image_name) values('{item['name']}', '{item['category']}', '{item['image_name']}')"
#         db.run_query(query)


# (4-2) GET endpoint for /search
@app.get("/search")
def get_search_results(keyword:str):
    query = f"SELECT * from items where name LIKE '%{keyword}%'"
    results = db.search(query, multiple=True)
    return {"items": results}


# (4-3) Categories table
# Run once
# query = "create table if not exists categories(id integer primary key, name text unique)"
# db.run_query(query)
#
# query = "select distinct category from items"
# categories = db.search(query, multiple=True)
# print(categories)
# for category in categories:
#     query = f"INSERT OR IGNORE into categories(name) values('{category[0]}')"
#     db.run_query(query)

def add_category(category):
    query = f"INSERT OR IGNORE {category} into categories"
    db.run_query(query)




# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=9000)