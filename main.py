from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/create/{function}")
def read_item(function: str, id: Union[str, None] = None):
    if function == "user":
      return {"function": function, "user_id": id}
    if function == "loan":
      return {"function": function, "user_id": id}
    return {"function":"invalid operation", "user_id": "N/A"}

