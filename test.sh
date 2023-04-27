#!/usr/bin/bash
# To test docs:
# http://127.0.0.1:8000/docs
#

# Create two users
curl "http://127.0.0.1:8000/create/user?first_name=old&last_name=dog&user_id=123"
printf "\n";
curl "http://127.0.0.1:8000/create/user?first_name=new&last_name=dog&user_id=124"
printf "\n";

# Create a loan
curl "http://127.0.0.1:8000/create/loan?principal=100000&loan_term_months=180&user_id=123&interest=4.5&description=test"
printf "\n";

# Retrieve the loan id
curl "http://127.0.0.1:8000/get/loan_id?user_id=123&description=test"
printf "\n";

# Get the amortization schedule
curl "http://127.0.0.1:8000/fetch/loan_sched?user_id=123&loan_id=1"
printf "\n";

# Get the amortization schedule summary up to a specific month
curl "http://127.0.0.1:8000/fetch/loan_summary?user_id=123&loan_id=1&month=10"
printf "\n";

# Get all loans for a user
curl "http://127.0.0.1:8000/fetch/all_loans?user_id=123"
printf "\n";

# Setup to share the loan between two users
curl "http://127.0.0.1:8000/share/1?user_id=123&shared_id=124"
printf "\n";
