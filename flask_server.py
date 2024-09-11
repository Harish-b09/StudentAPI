from flask import Flask, request
from flask_restful import Api, Resource, fields, marshal_with, abort
import psycopg2

app = Flask(__name__)
api = Api(app)

conn = psycopg2.connect(database="student_db", user="postgres_st",
                        password="postgres_st", host="192.168.1.35", port="5432")

resource_fields = {
    'studentid': fields.Integer,
    'studentname': fields.String,
    'studentage': fields.Integer
}

class Student(Resource):
    @marshal_with(resource_fields)
    def get(self, student_id=None):
        with conn.cursor() as cur:
            if student_id:
                cur.execute("SELECT * FROM students WHERE studentid = %s", (student_id,))
                result = cur.fetchone()
                if result is None:
                    abort(404, message="Student with id {} not found".format(student_id))
                student = {"studentid": result[0], "studentname": result[1], "studentage": result[2]}
                return student
            else:
                cur.execute("SELECT * FROM students ORDER BY studentid;")
                result = cur.fetchall()
                students = [{"studentid": r[0], "studentname": r[1], "studentage": r[2]} for r in result]
                if not students:
                    abort(404, message="No students found")
                return students

    def post(self):
        data = request.get_json()
        studentname = data.get('studentname')
        studentage = data.get('studentage')

        if not studentname or not isinstance(studentage, int):
            abort(400, message="Invalid data: Provide studentname and studentage")

        with conn.cursor() as cur:
            cur.execute("INSERT INTO students (studentname, studentage) VALUES (%s, %s) RETURNING studentid;",
                        (studentname, studentage))
            conn.commit()
            new_id = cur.fetchone()[0]

        return {"message": "Student added", "studentid": new_id}, 201

    def put(self, student_id):
        data = request.get_json()
        studentname = data.get('studentname')
        studentage = data.get('studentage')

        if not studentname or not isinstance(studentage, int):
            abort(400, message="Invalid data: Provide studentname and studentage")

        with conn.cursor() as cur:
            cur.execute(
                "UPDATE students SET studentname = %s, studentage = %s WHERE studentid = %s RETURNING studentid;",
                (studentname, studentage, student_id))
            conn.commit()
            updated_id = cur.fetchone()
            if updated_id is None:
                abort(404, message="Student with id {} not found".format(student_id))

        return {"message": "Student updated", "studentid": student_id}, 200

    def patch(self, student_id):
        data = request.get_json()
        studentname = data.get('studentname', None)
        studentage = data.get('studentage', None)
        if studentname is None and studentage is None:
            abort(400, message="Provide at least one field to update")
        update_fields = []
        values = []

        if studentname:
            update_fields.append("studentname = %s")
            values.append(studentname)

        if studentage:
            update_fields.append("studentage = %s")
            values.append(studentage)
        values.append(student_id)
        query = f"UPDATE students SET {', '.join(update_fields)} WHERE studentid = %s RETURNING studentid;"

        with conn.cursor() as cur:
            cur.execute(query, tuple(values))
            conn.commit()
            updated_id = cur.fetchone()
            if updated_id is None:
                abort(404, message="Student with id {} not found".format(student_id))
        return {"message": "Student updated", "studentid": student_id}, 200

    def delete(self, student_id):
        with conn.cursor() as cur:
            cur.execute("DELETE FROM students WHERE studentid = %s RETURNING studentid;", (student_id,))
            conn.commit()
            deleted_id = cur.fetchone()
            if deleted_id is None:
                abort(404, message="Student with id {} not found".format(student_id))

        return {"message": "Student deleted", "studentid": student_id}, 200



api.add_resource(Student, '/students', '/students/<int:student_id>')

if __name__ == "__main__":
    app.run(host='192.168.1.35', port=8080, debug=True)
