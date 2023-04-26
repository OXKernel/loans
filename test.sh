#!/usr/bin/bash
# To test docs:
# http://127.0.0.1:8000/docs
#
curl "http://127.0.0.1:8000/create/user?first_name=old&last_name=dog&user_id=123"
printf "\n";
curl "http://127.0.0.1:8000/create/loan?principal=100&duration_months=10&user_id=123"
printf "\n";
curl "http://127.0.0.1:8000/fetch/loan_sched?user_id=123"
printf "\n";
curl "http://127.0.0.1:8000/fetch/loan_summary?user_id=123"
printf "\n";
curl "http://127.0.0.1:8000/fetch/all_loans?user_id=123"
printf "\n";
curl "http://127.0.0.1:8000/share/abc?user_id=123"

