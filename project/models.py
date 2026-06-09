from django.db import models
from Auth_system.models import User

# Create your models here.

class Course(models.Model):
    title = models.CharField(max_length=100)
    desc = models.TextField()
    duration = models.CharField(max_length=50)
    fee = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE ,  related_name='course_create')
    M_teacher = models.OneToOneField(User, on_delete=models.DO_NOTHING, blank=True,null=True, related_name='courses',limit_choices_to={'role':"head_teacher"})
    course_image = models.ImageField('project/', null=True, blank=True)

    def __str__(self):
        return self.title



class Subjct(models.Model):
    sub_name = models.CharField(max_length=50)
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='subjects')
    total_chapter = models.IntegerField()
    teacher = models.OneToOneField(User, on_delete=models.SET_NULL, related_name="subjects",limit_choices_to={'role':"teacher"},null=True,blank=True)
    desc = models.TextField()
    sub_image = models.ImageField('project/',null=True,blank=True)

    def __str__(self):
        return self.sub_name



class Chapter(models.Model):
    name = models.CharField(max_length=50)
    desc = models.TextField()
    index = models.IntegerField(default=0)
    subject = models.ForeignKey(Subjct, on_delete=models.CASCADE, related_name='chapters')
    ch_image = models.ImageField('project/',null=True,blank=True)
    
    def __str__(self):
        return self.name


class Topics(models.Model):
    name = models.CharField(max_length=50)
    desc = models.TextField()
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='topics')
    creater = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name='topics')
    role = models.CharField(default='staff')
    demo = models.BooleanField(default=True)
    checked = models.BooleanField(default=True,null=True,blank=True)

    def __str__(self):
        return self.name



class File(models.Model):
    topics = models.ForeignKey(Topics,on_delete=models.CASCADE, related_name='Files')
    file = models.FileField(upload_to='content/',null=True,blank=True)
    checked = models.BooleanField(default=False)
    creater = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name='Files',default=11)

    file_type = models.CharField(max_length=50,choices=(
            ('video', 'Video'),
            ('pdf', 'PDF'),
            ('image', 'Image'),)
        )
    



class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', limit_choices_to={'role':"student"})
    course = models.ForeignKey(Course,  on_delete=models.CASCADE, related_name='enrollments')
    fee_submit = models.BooleanField(default=True)
    enroll = models.BooleanField(default=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')



class Test_Track(models.Model):
    pass_choice = (
        ('pass','Pass'),
        ('runing','Runing'),
        ('fail','Fail')
    )
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests',limit_choices_to={'role':'student'})
    course = models.ForeignKey(Course,  on_delete=models.CASCADE, related_name='tests')
    subject = models.ForeignKey(Subjct, on_delete=models.CASCADE, related_name='tests')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE,  related_name='tests')
    total_Q = models.IntegerField(blank=True,null=True, default=0)
    correct_Q = models.IntegerField(blank=True,null=True,default=0)
    pass_status = models.CharField(max_length=50,choices=pass_choice, default='runing')
    test_Time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student.username
    


class Demo(models.Model):
    subject = models.OneToOneField(Subjct,on_delete=models.CASCADE,related_name='demo')
    video = models.FileField(upload_to='Demo/',null=True,blank=True)
    pdf = models.FileField(upload_to='Demo/',null=True,blank=True)

    def __str__(self):
        return self.subject.sub_name
    


class Short_video(models.Model):
    file = models.ForeignKey(File, related_name='shorts', on_delete=models.CASCADE)
    video = models.FileField(upload_to='short/')



class Payment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    order_id = models.CharField(max_length=255, unique=True)
    payment_id = models.CharField(max_length=255, blank=True, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "PENDING"),
            ("SUCCESS", "SUCCESS"),
            ("FAILED", "FAILED")
        ],
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)






class Certificate(models.Model):

    student = models.ForeignKey(User,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    certificate_id = models.CharField(max_length=100,unique=True)
    certificate_file = models.FileField(upload_to="certificates/")
    issued_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = (
            "student",
            "course"
        )