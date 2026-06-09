from project.models import Course,Subjct,Chapter,Enrollment,Test_Track,Topics,File,Demo,Short_video,Certificate
from Auth_system.models import User
from project.utils.ai_generator import make_demo_video,attach_demo_pages,concatenate_video
from django.db import transaction
from project.utils.ai_generator import generate_certificate
import os
from datetime import datetime
from django.utils import timezone
from django.conf import settings
import uuid
from rest_framework import serializers


class CourseWriteSerializers(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only=True)
    class Meta:
        model = Course
        fields = ['title','desc','duration','fee','created_by','M_teacher','course_image']




class CoruseReadSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source = 'created_by.username')
    M_teacher = serializers.CharField(source = 'M_teacher.username')
    class Meta:
        model = Course
        fields = ['id','title','desc','duration','fee','created_by','M_teacher','course_image']




class SubjectSerializer(serializers.ModelSerializer):
    # teacher = serializers.CharField(source = 'teacher.username')
    teacher = serializers.SerializerMethodField()
    class Meta:
        model = Subjct
        fields = ['id','sub_name','total_chapter','teacher','desc','sub_image']

    
    def get_teacher(self, obj):
        
        if obj.teacher == None:
            return "No_Teacher"
        return obj.teacher.username
            


class CoruseReadSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source = 'created_by.username')
    # M_teacher = serializers.CharField(source = 'M_teacher.username')
    M_teacher = serializers.SerializerMethodField()

    

    class Meta:
        model = Course
        fields = ['id','title','desc','duration','fee','created_by','M_teacher','course_image']

    def get_M_teacher(self, obj):
        if obj.M_teacher:
            return obj.M_teacher.username
        
        return "NO_HEADTEACHER"


class CoruseSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source = 'created_by.username')
    # created_by = serializers.ReadOnlyField(source='created_by.username')
    M_teacher = serializers.SerializerMethodField()
    M_teacher_id = serializers.SerializerMethodField()

    
    class Meta:
        model = Course
        fields = ['id','title','desc','duration','fee','created_by','M_teacher','course_image','M_teacher_id']

    def get_M_teacher(self, obj):
        if obj.M_teacher:
            return obj.M_teacher.username
        
        return "NO_HEADTEACHER"

    def get_M_teacher_id(self, obj):
        if obj.M_teacher:
            return obj.M_teacher.id
        return 0


class CoruseUpdateSerializer(serializers.ModelSerializer):

    M_teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='head_teacher')
    )

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'desc',
            'duration',
            'fee',
            'M_teacher',
            'course_image'
        ]

    def validate(self, attrs):

        
        return attrs





class CoruseSubjectSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source = 'created_by.username')
    M_teacher = serializers.CharField(source = 'M_teacher.username')
    subjects = SubjectSerializer(many=True )
    
    class Meta:
        model = Course
        fields = ['id','title','desc','duration','fee','created_by','M_teacher','course_image','subjects']    
    


class EnrollmentSerlizer(serializers.ModelSerializer):
    student = serializers.CharField(source='student.username')
    class Meta:
        model = Enrollment
        fields = ['student','fee_submit','enroll']



class CoruseEnrollSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source = 'created_by.username')
    M_teacher = serializers.CharField(source = 'M_teacher.username')
    enrollments = EnrollmentSerlizer(many=True,read_only=True)
    class Meta:
        model = Course
        fields = ['id','title','desc','duration','fee','created_by','M_teacher','course_image','enrollments']        






class SubjectWriteSerlizer(serializers.ModelSerializer):
    # course = serializers.CharField(read_only=True)
    # teacher = serializers.CharField(source = 'teacher.id',
    # required=False,
    # allow_null=True)
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='teacher'),
        required=False,
        allow_null=True
    )
    class Meta:
        model = Subjct
        fields = ['sub_name','course','total_chapter','teacher','desc','sub_image']

        
    def validate(self, data):
        user = self.context['request'].user
        if user.role not in ['admin','head_teacher']:
            raise serializers.ValidationError("you are not authrizers")
        
        return data




class ChapterSerlizers(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id','index','name','desc','ch_image']


        
    


class SubjectReadSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source = 'course.title')
    teacher = serializers.SerializerMethodField()
    # CharField(source = 'teacher.username')
    class Meta:
        model = Subjct
        fields = ['id','sub_name','course','total_chapter','teacher','desc','sub_image']

    def get_teacher(self, obj):

        if obj.teacher is None:
            
            return "No_Teacher"
        else:
            
            return obj.teacher.username
    

# 


class SubjectSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source = 'course.title')
    teacher = serializers.SerializerMethodField()
    chapters= ChapterSerlizers(many=True)
    class Meta:
        model = Subjct
        fields = ['id','sub_name','course','total_chapter','teacher','desc','chapters','sub_image']


    def get_teacher(self, obj):
        
        if obj.teacher == None:
            return "No_Teacher"
        return obj.teacher.username
            
        
    



class ChapterWriteSerlizers(serializers.ModelSerializer):
    subject = serializers.CharField(read_only=True)
    class Meta:
        model = Chapter
        fields = ['name','desc','index','subject','ch_image']
        read_only_fields = ['index']
    
    def create(self, validated_data):
        subject = validated_data['subject']
        chapter = Chapter.objects.filter(subject=subject).order_by('-index').first()
        if chapter:
            biggest_index = chapter.index
        else:
            biggest_index = 0
        validated_data['index'] = biggest_index+1

        Chapter.objects.create(**validated_data)
        return validated_data
        
        


class FileSerlizers(serializers.ModelSerializer):
    topics=serializers.CharField(read_only=True)
    class Meta:
        model = File
        fields = ['id','file','file_type','checked','topics','creater']
        read_only_fields = ['file_type', 'checked', 'creater']    
    @transaction.atomic
    def create(self, validated_data):
        topic =validated_data['topics']
        subject=topic.chapter.subject
        uploaded_file = validated_data.get('file')
        content_type = uploaded_file.content_type

        # Detect file type
        if content_type.startswith("image/"):
            detected_type = "IMAGE"
        elif content_type.startswith("video/"):
            detected_type = "VIDEO"
        elif content_type == "application/pdf":
            detected_type = "PDF"
        else:
            raise serializers.ValidationError('this is not any PDF,image or video')

        validated_data['file_type'] = detected_type
        instance = super().create(validated_data)
        # if topic.demo != False:
            # video=None
            # pdf=None
            # demo,data = Demo.objects.get_or_create(subject=subject)

            # if validated_data['file_type'] == 'VIDEO':
            #     existing_video_path = demo.video.path if demo.video else None
            #     video = make_demo_video(instance.file.path,existing_video_path)
            #     if existing_video_path != None:
            #         sort =Short_video.objects.create(file=instance,video=video)
            #         main_video = concatenate_video(existing_video_path,sort.video.path)
            #     else:
            #         main_video = video

            # if validated_data['file_type'] == 'PDF':
            #     if not demo.pdf:
            #         pdf=attach_demo_pages(subject.sub_name,uploaded_file,None)
            #     else:
            #         pdf=attach_demo_pages(subject.sub_name,uploaded_file,demo.pdf.path)
            # if video != None:
            #     demo.video = main_video 
            # if pdf != None:
            #     demo.pdf = pdf
            # demo.save()
            #delete last demo video + sort video 
            # if validated_data['file_type'] != 'PDF' and existing_video_path != None:
                # if os.path.exists(existing_video_path):
                    
                #     os.remove(existing_video_path)
                #     sort.delete()


        return validated_data



class FileSerlizers_ForCheck(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id','file','file_type','checked','topics','creater']



class FilePDFSerlizer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id','file','checked','file_type']




class TopicsSerlizers(serializers.ModelSerializer):
    files = FilePDFSerlizer(
        source='Files',
        many=True,
        read_only=True
    )

    chapter=serializers.CharField(source='chapter.name')
    creater=serializers.CharField(source='creater.username')

    class Meta:
        model = Topics
        fields = ['id','name','desc','chapter','creater','demo','checked','files']





class ChapterReadStaffSerlizers(serializers.ModelSerializer):
    subject = serializers.CharField(source = 'subject.sub_name')
    class Meta:
        model = Chapter
        fields = ['id','name','desc','subject','ch_image']
    



class ChapterReadSerlizers(serializers.ModelSerializer):
    test_stutas=serializers.SerializerMethodField()
    # subject = serializers.CharField(source = 'subject.sub_name')
    subject = serializers.PrimaryKeyRelatedField(queryset=Subjct.objects.all())
    
    # M_teacher = serializers.PrimaryKeyRelatedField(
    #     queryset=User.objects.filter(role='head_teacher')
    # )
    class Meta:
        model = Chapter
        fields = ['id','name','desc','subject','test_stutas','index','ch_image']
    
    def get_test_stutas(self,obj):
        request =self.context.get('request')
        
        if not request or not request.user.is_authenticated:
            return None
        
        user = request.user
        test = Test_Track.objects.filter(student=user,chapter=obj).first()

        if not test:
            return "Locked"
        return test.pass_status
    



class ChapterdSerlizers(serializers.ModelSerializer):
    topics = TopicsSerlizers(many=True)
    
    class Meta:
        model = Chapter
        fields = ['id','name','desc','topics','ch_image']

        



class TopicsWriteSerlizers(serializers.ModelSerializer):
    chapter = serializers.CharField(read_only=True)
    creater = serializers.CharField(read_only=True)
    class Meta:
        model = Topics
        fields = ['name','desc','chapter','creater']

    def create(self, validated_data):
        user =self.context['request'].user
        role = user.role
        Topics.objects.create(
            name=validated_data['name'],
            desc=validated_data['desc'],
            chapter=validated_data['chapter'],
            creater = user,
            role=role,
            )

        return  validated_data


        

class EnrollmentWriteSerlizers(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['course']

    @transaction.atomic
    def create(self, validated_data):
        student = self.context['request'].user
        course = validated_data.get('course')
        subjects = Subjct.objects.filter(course=course)
        enrollment =Enrollment.objects.create(student=student,course=course)
        test_track = []

        for subject in subjects:
            chapter = Chapter.objects.filter(subject=subject).order_by('id').first()
            

            if chapter:
                test_track.append(
                    Test_Track(
                        student=student,
                        course=course,
                        subject=subject,
                        chapter=chapter,
                    )
                )
        Test_Track.objects.bulk_create(test_track)
        return enrollment
       
        

class TestTrackWriteSerlizer(serializers.ModelSerializer):
    class Meta:
        model = Test_Track
        fields = ['total_Q','correct_Q',]

    # @transaction.atomic
    def update(self, instance, validated_data):
        TQ=validated_data.get('total_Q')
        CQ=validated_data.get('correct_Q')
        pass_status_ = 'fail'
        if TQ == 0 or  CQ ==0 :
            raise serializers.ValidationError('please give valid test')
        marks =(CQ/TQ)*100
        if marks >= 70:
            pass_status_ = 'pass'
        if pass_status_ == 'pass':
            instance.pass_status = pass_status_
            instance.total_Q = TQ
            instance.correct_Q = CQ
            instance.save()    

            chapter = Chapter.objects.filter(subject=instance.subject, index=instance.chapter.index+1).first()
            if chapter:
                Test_Track.objects.create(
                    student=instance.student,
                    course=instance.course,
                    subject=instance.subject,
                    chapter=chapter,
                    pass_status='runing'
                    )
        return instance



class DemoSerlizerss(serializers.ModelSerializer):
    video = serializers.FileField(use_url=True)
    class Meta:
        model = Demo
        fields = ['id','subject','video','pdf']





class CertificatewriteSerlizer(serializers.ModelSerializer):

    class Meta:
        model = Certificate
        fields = ['course']

    def create(self, validated_data):
        student = self.context['request'].user
        course = validated_data['course']

        # Check all chapters are passed
        chapters = Chapter.objects.filter(
            subject__course=course
        ).distinct()

        for chapter in chapters:
            passed = Test_Track.objects.filter(
                student=student,
                chapter=chapter,
                pass_status='pass'
            ).exists()

            if not passed:
                raise serializers.ValidationError(
                    "Please complete all tests after downloading the certificate."
                )

        # Certificate already exists
        existing_certificate = Certificate.objects.filter(
            student=student,
            course=course
        ).first()

        if existing_certificate:
            return existing_certificate

        # Generate certificate
        certificate_id = f"LMS-{uuid.uuid4().hex[:8].upper()}"

        today_date = timezone.now().strftime("%d %B %Y")

        file_name = f"{certificate_id}.png"

        file_path = os.path.join(
            settings.MEDIA_ROOT,
            "certificates",
            file_name
        )

        generate_certificate(
            student_name=student.username,
            course_name=course.title,
            certificate_id=certificate_id,
            completion_date=today_date,
            template_path=os.path.join(
                settings.MEDIA_ROOT,
                "certificates",
                "template.png"
            ),
            output_path=file_path
        )

        # IMPORTANT
        certificate = Certificate.objects.create(
            student=student,
            course=course,
            certificate_id=certificate_id,
            certificate_file=f"certificates/{file_name}"
        )

        return certificate