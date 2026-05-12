from fastapi import FastAPI

app =FastAPI()
courses_db =[
    {'id':1,'name':'atil','title':'Python','category':'Development'},
    {'id':2,'name':'esra','title':'Python','category':'Development'},
    {'id':3,'name':'atil','title':'DL','category':'AI'},
    {'id':4,'name':'osman','title':'C++','category':'Development'},
    {'id':5,'name':'sevinç','title':'Jenkins','category':'Development'},
    {'id':6,'name':'tuana','title':'Kubernetes','category':'Development'},
    {'id':7,'name':'ayse','title':'ML','category':'AI'}
    ]

@app.get("/hello")
async def hello_world():
    return{"message":"Hello"}


@app.get("/courses")
async def get_all_courses():
    return courses_db

#Path Parameter
@app.get("/courses/{course_title}")
async def get_course(course_title:str):
    for course in  courses_db:
        if course.get('title').upper()== course_title.upper():
            return course

@app.get("/courses/byid/{course_id}")
async def get_course_by_id(course_id :int):
    for course in  courses_db:
        if course.get('id')== course_id:
            return course

#query
