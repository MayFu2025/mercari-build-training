import os
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import json

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
    # Save image to directory
    image_bytes = image.file.read()
    image_name = f"{hashlib.sha256(image_bytes).hexdigest()}.jpg"
    save_image(image_bytes, image_name)

    # Save item to json
    item = {"name": name, "category": category, "image_name": image_name}
    save_json(new_item=item)

    logger.info(f"Receive item: {name}, {category}, {image_name}")
    return {"message": f"item received: {item}"}


# GET endpoint for /items
@app.get("/items")
def get_items_list(filename='items.json'):
    with open(filename, 'r') as file:
        file_data = json.load(file)
    return {"message": file_data}


@app.get("/items/{item_id}")



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