## Create User API

**Auth related API -------------------------------------------------------------------**
=================================================================

**for user register**
[POST](http://127.0.0.1:8000/auth/register):
                            {
                              "username":"teacher",
                              "email":"kamal@gmail.com",
                              "role":"admin",
                              "password":"ram12345",
                              "check_password":"ram12345"
                            }


**for user Login**
[POST](http://127.0.0.1:8000/auth/login):
                            {
                              "username":"teacher",
                              "password":"ram12345",
                            }




**for user teacher register**
[POST](http://127.0.0.1:8000/auth/teacherRegister):
                            {
                              "username":"teacher",
                              "email":"kamal@gmail.com",
                              "role":"head_teacher",
                              "password":"ram12345"
                            }



**get teacher list for admin or head teacker**
[GET](http://127.0.0.1:8000/auth/teacherList):


**get Head teacher list for admin **
[GET](http://127.0.0.1:8000/auth/headTeacherListView):

<!--  -->
                          


**for user Login User Details**
[GET](http://127.0.0.1:8000/auth/LoginUserDetails):                            
<!-- fields = ['username','email','role','profile_image','password'] -->
**for user verify mail**
[POST](http://127.0.0.1:8000/auth/verify_mail)
                                            {
                                            "username":
                                            "otp":
                                            }

**for user forgot password**
[POST](http://127.0.0.1:8000/auth/forgot_password)
                                            {
                                              "username":
                                            }

**for user forgot reset password**
[POST](http://127.0.0.1:8000/auth/reset_password)
                                            {
                                              "username":
                                              "otp":
                                              "new_password":
                                            }



===============================
##### public API => 
<!-- check all course -->
[get](http://127.0.0.1:8000/study/course_all/)




==========================
<!-- only admin can use it -->
#### Course => 
-----------------course--------------------------------
<!-- get all course -->
[GET](http://127.0.0.1:8000/study/course/)


<!-- create new course -->
[POST](http://127.0.0.1:8000/study/course/)
    {
        "id": 3,
        "title": "Python for Beginners",
        "desc": "Complete beginner friendly Python course",
        "duration": "3 month",
        "fee": 2999,
        "created_by": "raman",
        "M_teacher": "ha_teacher",
        "course_image": "http://127.0.0.1:8000/media/download_1.jpeg"
    }


<!-- [update, delete retrieve] new course -->
[PUT,DELETE](http://127.0.0.1:8000/study/course/id/)    

<!-- get all subject according each enroled students -->
[GET](http://127.0.0.1:8000/study/course/4/enrollment/)

[POST](http://127.0.0.1:8000/study/enrol/)
{
  "course":12
}

<!-- get all subject according each subject -->
[GET,POST](http://127.0.0.1:8000/study/course/3/subject/)

<!-- get hpw many course any student enrolled (in list format) -->
[GET](http://127.0.0.1:8000/study/course/enrolled/)

<!-- for update Course (we can partial update) -->
[GET,PATCH](http://127.0.0.1:8000/study/course/updateCourse/)




###  Subject =>>
<!-- get all subject -->
[GET,POST](http://127.0.0.1:8000/study/subject/)


<!-- subject with chapters with Update + delete -->
[GET,PUT,DELETE](http://127.0.0.1:8000/study/subject/1/)

<!-- subject according chapter (for students)-->
[PUT](http://127.0.0.1:8000/study/subject/1/test/)


<!-- subject according chapter -->
[GET,POST](http://127.0.0.1:8000/study/subject/1/chapter/)

<!-- subject according  -->
[GET](http://127.0.0.1:8000/study/subject/1/PDF/)

<!-- subject according chapter (for students)-->
[GET](http://127.0.0.1:8000/study/subject/1/demo/)





### chapter => 


[GET,put,delete](http://127.0.0.1:8000/study/chapter/1/)


<!-- content create only -->
[post](http://127.0.0.1:8000/study/chapter/1/topcs/)





### Topics => 

[GET](http://127.0.0.1:8000/study/Topics/1/)
[GET,put,delete](http://127.0.0.1:8000/study/Topics/1/)

[GET,put,delete](http://127.0.0.1:8000/study/Topics/1/Teacher_files)

[GET,put,delete](http://127.0.0.1:8000/study/Topics/1/student_files)







