import logging
import sys
import sqlite3
from typing import Union
from fastapi import FastAPI

# Init logging
# setup loggers
logging.config.fileConfig('log.conf', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)

class SQLInit:
  conn = sqlite3.connect('loans.db')

  conn.execute('''CREATE TABLE IF NOT EXISTS USERS
           (ID INTEGER PRIMARY KEY NOT NULL,
            FIRST_NAME TEXT        NOT NULL,
            LAST_NAME  TEXT        NOT NULL
           );''')

  conn.execute('''CREATE TABLE IF NOT EXISTS LOANS
            (LOAN_ID         INTEGER PRIMARY KEY AUTOINCREMENT,
             ID              INTEGER    NOT NULL,
             PRINCIPAL       FLOAT      NOT NULL,
             TERM_IN_MONTHS  INTEGER    NOT NULL,
             INTEREST        FLOAT      NOT NULL,
             DESCRIPTION     TEXT       UNIQUE NOT NULL
             );''')

  conn.execute('''CREATE TABLE IF NOT EXISTS SHARED_LOANS
            (LOAN_ID    INTEGER NOT NULL,
             ID         INTEGER NOT NULL,
             SHARED_ID  INTEGER NOT NULL,
             FOREIGN KEY(LOAN_ID)   REFERENCES LOANS(LOAN_ID),
             FOREIGN KEY(ID)        REFERENCES USERS(ID),
             FOREIGN KEY(SHARED_ID) REFERENCES USERS(ID)
             );''')

  conn.commit()
  conn.close()

class LoanIQ:
  # REFERENCES:
  #   https://www.amortization-calc.com/mortgage-calculator/
  @classmethod
  def compute_payment(self, principal:float, term:int, interest:float):
    interest = interest / 100
    rate = interest / 12
    payment = (principal * pow(rate + 1, term) * rate) / (pow(rate + 1, term) - 1)
    return payment

  @classmethod
  def compute_amortization_schedule(self, principal:float, term:int, interest:float, payment:float):
    month = 1
    interest = interest / 100
    sched = []
    # principal must go to 0 after all terms are computed 
    # given the computed payment
    while principal > 0:
      interest_in_term = principal * (interest / 12)
      payment_less_interest = payment - interest_in_term
      if payment_less_interest < 0:
        break
      if principal < payment_less_interest:
        paid_principal = principal
      else:
        paid_principal = payment_less_interest
      principal = principal - paid_principal
      sched.append({"month": month, "balance": principal, "monthly_payment": payment, "interest_in_term": interest_in_term, "paid_principal": paid_principal})
      month += 1
    return sched

  @classmethod
  def compute_amortization_summary(self, principal:float, term:int, interest:float, payment:float, month:int):
    index = 1
    interest = interest / 100
    current_balance = 0
    aggregate_principal = 0
    aggregate_interest = 0
    # principal must go to 0 after all terms are computed 
    # given the computed payment
    while principal > 0 and index <= month:
      interest_in_term = principal * (interest / 12)
      payment_less_interest = payment - interest_in_term
      if payment_less_interest < 0:
        break
      if principal < payment_less_interest:
        paid_principal = principal
      else:
        paid_principal = payment_less_interest
      principal = principal - paid_principal
      current_balance = principal
      aggregate_principal += paid_principal
      aggregate_interest  += interest_in_term
      index = index + 1
    return current_balance, aggregate_principal, aggregate_interest

class Utility:
  @classmethod
  def get_loan(self, user_id:str, loan_id:str):
    conn = sqlite3.connect('loans.db')
    principal = 0
    term_in_months = 0
    interest = 0
    try:
      # Uses autoincrement to increase the loan_id primary key.
      cursor = conn.execute("SELECT PRINCIPAL, TERM_IN_MONTHS, INTEREST FROM LOANS WHERE LOAN_ID={loan_idf} and ID={user_idf}".format(loan_idf=loan_id, user_idf=user_id))
      for row in cursor:
         principal= float(row[0])
         term_in_months = int(row[1])
         interest = float(row[2])
         break
    except sqlite3.Error as er:
      logger.error('SQLite error: %s' % (' '.join(er.args)))
      conn.close()
      return None, None, None
    conn.close()
    return principal, term_in_months, interest

########
# MAIN #
########

logger.info("Loan App Starting...")

# Init SQL
SQLInit()

# Loan Calculations
liq = LoanIQ()

# Utility calculations
util = Utility()

# FastAPI logic
app = FastAPI()

@app.get("/")
def read_root():
    return {"Python Loan app"}

@app.get("/create/user")
def read_item(first_name: Union[str, None] = None, last_name: Union[str, None] = None, user_id: Union[str, None] = None):
    conn = sqlite3.connect('loans.db')
    try:
      conn.execute("INSERT INTO USERS (ID, FIRST_NAME, LAST_NAME) \
        VALUES (?, ?, ?)", (user_id, first_name, last_name))
      conn.commit()
    except sqlite3.Error as er:
      logger.error('SQLite error: %s' % (' '.join(er.args)))
      conn.close()
      return {"exception": "error in /create/user", "first_name": first_name, "last_name": last_name, "user_id": user_id}
    conn.close()
    return {"first_name": first_name, "last_name": last_name, "user_id": user_id}

@app.get("/create/loan")
def read_item(principal: Union[str, None] = None, loan_term_months: Union[str, None] = None, interest: Union[str, None] = None, user_id: Union[str, None] = None, description: Union[str, None] = None):
    conn = sqlite3.connect('loans.db')
    try:
      # Uses autoincrement to increase the loan_id primary key.
      conn.execute("INSERT INTO LOANS (ID, PRINCIPAL, TERM_IN_MONTHS, INTEREST, DESCRIPTION) \
        VALUES (?, ?, ?, ?, ?)", (user_id, float(principal), int(loan_term_months), float(interest), description))
      conn.commit()
    except sqlite3.Error as er:
      logger.error('SQLite error: %s' % (' '.join(er.args)))
      conn.close()
      return {"exception": "error in /create/loan", "principal": principal, "term": loan_term_months, "user_id": user_id, "interest": interest, "description": description}
    conn.close()
    return {"principal": principal, "term": loan_term_months, "user_id": user_id, "interest": interest, "description": description}

@app.get("/get/loan_id")
def read_item(user_id: Union[str, None] = None, description: Union[str, None] = None):
    conn = sqlite3.connect('loans.db')
    loan_id = -1
    try:
      # Uses autoincrement to increase the loan_id primary key.
      cursor = conn.execute("SELECT LOAN_ID FROM LOANS WHERE ID=? and DESCRIPTION=?",(user_id, description))
      for row in cursor:
         loan_id = int(row[0])
         break
    except sqlite3.Error as er:
      logger.error('SQLite error: %s' % (' '.join(er.args)))
      conn.close()
      return {"exception": "error in /get/loan_id", "user_id": user_id, "description": description}
    conn.close()
    return {"loan_id": loan_id}

@app.get("/fetch/loan_sched")
def read_item(user_id: Union[str, None] = None, loan_id: Union[str, None] = None):
   # Look up loan using unique loan_id for user
   # compute the schedule and return it back with the required fields
   principal, term_in_months, interest = util.get_loan(user_id, loan_id)
   if principal == None or term_in_months == None or interest == None:
    return {"exception": "/fetch/loan_sched couldn't retrive user loan", "user_id": user_id, "loan_id": loan_id}
   payment = liq.compute_payment(principal, term_in_months, interest)
   sched = liq.compute_amortization_schedule(principal, term_in_months, interest, payment)
   return {"amortization_schedule": sched}

@app.get("/fetch/loan_summary")
def read_item(user_id: Union[str, None] = None, loan_id: Union[str, None] = None, month: Union[str, None] = None):
   # Retrieve the loan
   # Compute payment and amortization schedule
   # Compute
   #  - Current principal balance at given month
   #  - The aggregate amount of principal already paid
   #  - The aggregate amount of interest already paid
   principal, term_in_months, interest = util.get_loan(user_id, loan_id)
   if principal == None or term_in_months == None or interest == None:
    return {"exception": "fetch/loan_summary couldn't retrive user loan", "user_id": user_id, "loan_id": loan_id}
   payment = liq.compute_payment(principal, term_in_months, interest)
   current_balance, aggregate_principal, aggregate_interest = liq.compute_amortization_summary(principal, term_in_months, interest, payment, int(month))
   return {"current_balance": current_balance, "aggregate_principal": aggregate_principal, "aggregate_interest": aggregate_interest}

@app.get("/fetch/all_loans")
def read_item(user_id: Union[str, None] = None):
    conn = sqlite3.connect('loans.db')
    loans = []
    try:
      # Uses autoincrement to increase the loan_id primary key.
      cursor = conn.execute("SELECT LOAN_ID, ID, PRINCIPAL, TERM_IN_MONTHS, INTEREST, DESCRIPTION FROM LOANS WHERE ID={idf}".format(idf=user_id))
      for row in cursor:
         loans.append({"loan_id":row[0],"id":row[1],"principal":row[2],"term_in_months":row[3],"interest":row[4],"description":row[5]})
    except sqlite3.Error as er:
      logger.error('SQLite error: %s' % (' '.join(er.args)))
      conn.close()
      return {"exception": "error in /fetch/all_loans", "user_id": user_id}
    conn.close()
    return {"loans": loans}

@app.get("/share/{loan_id}")
def read_item(loan_id: str, user_id: Union[str, None] = None, shared_id: Union[str, None] = None):
    conn = sqlite3.connect('loans.db')
    try:
      conn.execute("INSERT INTO SHARED_LOANS (LOAN_ID, ID, SHARED_ID) \
        VALUES ({loan_idf}, {idf}, {sidf})".format(loan_idf=loan_id, idf=user_id, sidf=shared_id))
      conn.commit()
    except sqlite3.Error as er:
      logger.error('SQLite error: %s' % (' '.join(er.args)))
      conn.close()
      return {"exception": "error in /share", "loan_id": loan_id, "user_id": user_id, "shared_id": shared_id}
    conn.close()
    return {"loan_id": loan_id, "user_id": user_id, "shared_id": shared_id}
