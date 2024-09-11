from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List,Optional
import psycopg2

app = FastAPI()


conn = psycopg2.connect(database="student_db", user="postgres_st",
                        password="postgres_st", host="192.168.1.35", port="5432")



class StudentModel(BaseModel):
    studentname: str
    studentage: int

class PartialStudentModel(BaseModel):
    studentname: Optional[str] = None
    studentage: Optional[int] = None


class StudentInDB(StudentModel):
    studentid: int


@app.get("/students", response_model=List[StudentInDB])
async def get_students():
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM students ORDER BY studentid;")
        result = cur.fetchall()
        students = [StudentInDB(studentid=r[0], studentname=r[1], studentage=r[2]) for r in result]
        if not students:
            raise HTTPException(status_code=404, detail="No students found")
        return students


@app.get("/students/{student_id}", response_model=StudentInDB)
async def get_student(student_id: int):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM students WHERE studentid = %s", (student_id,))
        result = cur.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")
        return StudentInDB(studentid=result[0], studentname=result[1], studentage=result[2])


@app.post("/students", response_model=StudentInDB, status_code=201)
async def create_student(student: StudentModel):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO students (studentname, studentage) VALUES (%s, %s) RETURNING studentid;",
                    (student.studentname, student.studentage))
        conn.commit()
        new_id = cur.fetchone()[0]
        return StudentInDB(studentid=new_id, studentname=student.studentname, studentage=student.studentage)


@app.put("/students/{student_id}", response_model=StudentInDB)
async def update_student(student_id: int, student: StudentModel):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE students SET studentname = %s, studentage = %s WHERE studentid = %s RETURNING studentid;",
            (student.studentname, student.studentage, student_id))
        conn.commit()
        updated_id = cur.fetchone()
        if updated_id is None:
            raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")
        return StudentInDB(studentid=student_id, studentname=student.studentname, studentage=student.studentage)


@app.patch("/students/{student_id}", response_model=StudentInDB)
async def partial_update_student(student_id: int, student: PartialStudentModel):
    with conn.cursor() as cur:
        cur.execute("SELECT studentname, studentage FROM students WHERE studentid = %s;", (student_id,))
        existing_student = cur.fetchone()
        if existing_student is None:
            raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")
        update_values = {
            "studentname": student.studentname if student.studentname is not None else existing_student[0],
            "studentage": student.studentage if student.studentage is not None else existing_student[1]
        }

        set_clause = ", ".join(f"{key} = %s" for key in update_values.keys())
        query = f"UPDATE students SET {set_clause} WHERE studentid = %s RETURNING studentid;"
        values = list(update_values.values()) + [student_id]
        cur.execute(query, values)
        updated_id = cur.fetchone()
        conn.commit()

        if updated_id is None:
            raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")
        return StudentInDB(studentid=student_id, **update_values)


@app.delete("/students/{student_id}", status_code=204)
async def delete_student(student_id: int):
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM students WHERE studentid = %s RETURNING studentid;", (student_id,))
            deleted_id = cur.fetchone()
            conn.commit()
            if deleted_id is None:
                raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code = 500, detail=str(e))
