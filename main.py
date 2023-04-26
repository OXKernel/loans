from typing import Union

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Python Loan app"}

@app.get("/create/user")
def read_item(first_name: Union[str, None] = None, last_name: Union[str, None] = None, user_id: Union[str, None] = None):
    return {"first_name": first_name, "last_name": last_name, "user_id": user_id}

@app.get("/create/loan")
def read_item(principal: Union[str, None] = None, loan_term_months: Union[str, None] = None, user_id: Union[str, None] = None):
    return {"principal": principal, "duration": loan_term_months, "user_id": user_id}

@app.get("/fetch/loan_sched")
def read_item(user_id: Union[str, None] = None):
   return {"user_id": user_id}

@app.get("/fetch/loan_summary")
def read_item(user_id: Union[str, None] = None):
   return {"user_id": user_id}

@app.get("/fetch/all_loans")
def read_item(user_id: Union[str, None] = None):
   return {"user_id": user_id}

@app.get("/share/{loan_id}")
def read_item(loan_id: str, user_id: Union[str, None] = None):
    return {"loan_id": loan_id, "user_id": user_id}
