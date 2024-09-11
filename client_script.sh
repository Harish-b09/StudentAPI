#!/bin/bash


BASE_URL="http://192.168.1.35:8080"


echo "Getting all students"
curl -X GET "$BASE_URL/students"


STUDENT_ID=107

echo "Getting student with ID $STUDENT_ID"
curl -X GET "$BASE_URL/students/$STUDENT_ID"


echo "Creating a new student"
curl -X POST "$BASE_URL/students" \
     -H "Content-Type: application/json" \
     -d '{"studentname": "John", "studentage": 27}'


echo "Updating student with ID $STUDENT_ID"
curl -X PUT "$BASE_URL/students/$STUDENT_ID" \
     -H "Content-Type: application/json" \
     -d '{"studentname": "Jayesh", "studentage": 23}'


echo "Partially updating student with ID $STUDENT_ID"
curl -X PATCH "$BASE_URL/students/$STUDENT_ID" \
     -H "Content-Type: application/json" \
     -d '{"studentage": 24}'


echo "Deleting student with ID $STUDENT_ID"
curl -X DELETE "$BASE_URL/students/$STUDENT_ID"


