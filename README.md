# loans
Python based loans app

# Description
Simple Python Based Loan amortization tool

# Run FastAPI
uvicorn main:app --reload

# Algorithm

## Monthly payment is computed using:
   payment = (principal * pow(rate + 1, term) * rate) / (pow(rate + 1, term) - 1)

## Amortization schedule is computed as:
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
      month += 1

In this implementation, monthly payment is computed, and
then applied per month reducing the balance (principal)
and calculating the principal and interest paid. Using
the above formula, we can generate a schedule and
store it in a JSON array. We can also compute the 
aggregate interest and principal paid.

# Notes:
This implementation uses sqlite3 which adds functionality
to make the data persist and allows us to be able to query the data.
