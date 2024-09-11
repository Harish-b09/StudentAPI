import requests

BASE_URL = 'http://192.168.1.35:8080/students'

def get_request():
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        json_data = response.json()
        return json_data
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def get_by_id_request(studentid):
    try:
        response = requests.get(f"{BASE_URL}/{studentid}")
        response.raise_for_status()
        json_data = response.json()
        return json_data
    except requests.exceptions.HTTPError as err:
        if response.status_code == 404:
            print(f"Student with id {studentid} not found.")
        else:
            print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def post_request(studentname, studentage):
    new_student = {
        "studentname": studentname,
        "studentage": studentage
    }
    try:
        response = requests.post(BASE_URL, json=new_student)
        response.raise_for_status()
        json_data = response.json()
        print(json_data)
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def update_student(studentid, studentname, studentage):
    updated_info = {"studentname": studentname, "studentage": studentage}
    try:
        response = requests.put(f"{BASE_URL}/{studentid}", json=updated_info)
        response.raise_for_status()
        json_data = response.json()
        print(json_data)
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def partial_update(studentid, studentage=None, studentname=None):
    if studentage is None and studentname is None:
        raise ValueError("Provide at least one parameter to update")
    partial_info = {}
    if studentage:
        partial_info["studentage"] = studentage
    if studentname:
        partial_info["studentname"] = studentname

    try:
        response = requests.patch(f"{BASE_URL}/{studentid}", json=partial_info)
        response.raise_for_status()
        json_data = response.json()
        print(json_data)
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def delete_student_by_id(student_id):
    try:
        response = requests.delete(f"{BASE_URL}/{student_id}")
        if response.status_code == 204:
            print(f"Student with id {student_id} deleted successfully.")
        else:
            json_data = response.json()
            print(json_data)
    except requests.exceptions.HTTPError as err:
        if response.status_code == 404:
            print(f"Student with id {student_id} not found.")
        else:
            print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


print(get_request())
delete_student_by_id(100)
print(get_request())
