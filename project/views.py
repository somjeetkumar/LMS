from rest_framework.permissions import IsAuthenticated
from django.shortcuts import  get_object_or_404
from rest_framework.decorators import action
from pypdf import  PdfReader
from rest_framework.viewsets import ViewSet,ModelViewSet

from io import BytesIO
import requests
from PyPDF2 import PdfReader

from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

from RBAC.auth_permission import  is_Admin,is_Student
from Auth_system.models import User
import os
from rest_framework.views import APIView
from .utils.ai_generator import generate_mcqs_from_text,doubt_solve
from RBAC.permission import RBAC_Permission
from PyPDF2 import PdfReader

from .models import Course,Subjct,Chapter,Enrollment,Test_Track,Topics,File,Demo,Payment,Certificate
from serializers.project_serializers import (
    CoruseReadSerializer,
    CourseWriteSerializers, 
    SubjectWriteSerlizer,
    SubjectReadSerializer,
    CoruseSerializer,
    ChapterWriteSerlizers,
    SubjectSerializer,
    ChapterReadSerlizers,
    EnrollmentWriteSerlizers,
    CoruseEnrollSerializer,
    CoruseSubjectSerializer,
    TestTrackWriteSerlizer,
    ChapterdSerlizers,
    ChapterReadStaffSerlizers,
    TopicsSerlizers,
    TopicsWriteSerlizers,
    FilePDFSerlizer,
    FileSerlizers, 
    DemoSerlizerss,
    FileSerlizers_ForCheck,
    ChapterSerlizers,
    CoruseUpdateSerializer,
    CertificatewriteSerlizer
    )
from rest_framework.permissions import AllowAny,IsAuthenticated
from RBAC.policies import RoleBasedPermission
from .razorpay_client import client,razorpay
from django.conf import settings





class CourseView_set(ModelViewSet):
    permission_classes = [RBAC_Permission]



    def get_serializer_class(self):

        if self.action == 'course_subject':
        
            if self.request.method == 'POST':
                return SubjectWriteSerlizer
    
            return CoruseSubjectSerializer
    
        if self.action == 'create' and self.request.user.role == 'admin':
            return CourseWriteSerializers
    
        if self.action == 'update':
            return CoruseUpdateSerializer
    
        if self.action == 'partial_update':
            return CoruseUpdateSerializer
    
        if self.action == 'retrieve':
            return CoruseSerializer
    
        if self.request.user.role == 'head_teacher':
            return CoruseSerializer
    
        return CoruseReadSerializer



    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Course.objects.all()
        if self.request.user.role == 'head_teacher':
            return Course.objects.filter(M_teacher=self.request.user)
        if self.request.user.role == 'teacher':
            return Course.objects.filter(subjects__teacher=self.request.user)
        if self.request.user.role =='student':
            return Course.objects.all()
        return Course.objects.none()
    
    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)
    

    @action(detail=True,methods=['get'],url_path='enrollment', permission_classes=[RBAC_Permission])
    def course_enroll(self,req,pk=None):
        course =self.get_object()
        return Response(CoruseEnrollSerializer(course).data,status=status.HTTP_200_OK)


    @action(detail=True,methods=['get','post'],url_path='subject',permission_classes=[RBAC_Permission])
    def course_subject(self,req,pk=None):
        course =self.get_object()
        if req.method == 'GET':
            return Response(self.get_serializer(course).data,status=status.HTTP_200_OK)
        if req.method=='POST':
            ser = self.get_serializer(data=req.data,context={"request":req})
            ser.is_valid(raise_exception=True)
            ser.save(course=course)
            return Response(ser.data, status=status.HTTP_201_CREATED)
    
    
    @action(detail=False,methods=['get'],url_path='enrolled',permission_classes=[is_Student])
    def allCourse(self,req):
        course = Course.objects.filter(enrollments__student = req.user)
        return Response(CoruseReadSerializer(course,many=True,context={'request': req}).data, status=status.HTTP_200_OK)
    

    @action(detail=True,methods=['patch'],url_path='updateCourse',permission_classes=[is_Admin])
    def headTeacherAssign(self,request,pk):
        course = self.get_object()
        ser =CourseWriteSerializers(course,data=request.data,partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({"message":"course has updated"}, status=status.HTTP_200_OK)

    



class courseShow_all(ModelViewSet):
    serializer_class = CoruseReadSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        if self.action in['list', 'retrieve', 'course_all_subject']:
            return Course.objects.all()
        if self.action in  ['create','update','partial_update']:
            raise PermissionError('you are not able to perform these oprations ')
        return Course.objects.none()

    @action(detail=True,methods=['get'],url_path='subjects')
    def course_all_subject(self,req,pk=None):
        course =self.get_object()
        
        return Response(CoruseSubjectSerializer(course,context={'request': req}).data,status=status.HTTP_200_OK)
        
        




class SubjectViewSet(ViewSet):
    permission_classes = [IsAuthenticated,RBAC_Permission]

    serlizers_action_custom_classes = {
        "chapterOFSubject":{
            "POST":ChapterWriteSerlizers,
            "GET":SubjectSerializer,
        },
        "test":{
            "PUT":TestTrackWriteSerlizer
        },
    
    }

    serlizers_classes = {
        # "list_teacher":SubjectSerializer,
        "list":SubjectReadSerializer,
        "create":SubjectWriteSerlizer,
        "retrieve":SubjectSerializer,
        "update":SubjectWriteSerlizer,
    }

    def get_serializer_class(self):

        if self.action in self.serlizers_action_custom_classes:
            action = self.serlizers_action_custom_classes.get(self.action)
            return action.get(self.request.method)

        if self.action =='list' and self.request.user.role == 'teacher':
            return SubjectSerializer

        if self.action in self.serlizers_classes:
            return self.serlizers_classes.get(self.action)
        
        return SubjectSerializer


    def get_serializer(self,*args, **kwargs):
        get_serializer = self.get_serializer_class()
        return get_serializer(*args, **kwargs)
    

    def list(self,req):
        if req.user.role == 'teacher':
            querySet = Subjct.objects.filter(teacher=req.user)

        elif req.user.role == 'head_teacher':
            querySet = Subjct.objects.filter(course__M_teacher=req.user)

        elif req.user.role =='student':
            querySet = Subjct.objects.filter(course__enrollments__student=req.user)

        else:
            querySet = Subjct.objects.all()
        
        serlizers = self.get_serializer(querySet,many=True,context={'request': req})
        return Response(serlizers.data,status=status.HTTP_200_OK)
    

    def create(self,req):
        ser =self.get_serializer(data=req.data,context={"request":req})
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)


    def retrieve(self,req,pk=None):
        ser = get_object_or_404(Subjct,pk=pk)
        serializer =self.get_serializer(ser,context={'request': req})
        data = serializer.data

        if req.user.role == 'student':
            for item in data['chapters']:
                chapter=get_object_or_404(Chapter,pk=item['id'])
                test=Test_Track.objects.filter(student=req.user,chapter=chapter).first()
                item['pass_status'] = "locked" if test is None else test.pass_status
        return Response(data, status=status.HTTP_200_OK)
    

    def update(self,req,pk=None):
        subject=get_object_or_404(Subjct,pk=pk)
        serializer = self.get_serializer(subject,data=req.data,partial=True, context={"request": req})
        serializer.is_valid(raise_exception=True)
        
        teach = serializer.validated_data['teacher']
        
        
        if teach.role != 'teacher':
            return Response({'message':"Your need to set any teacher here"})
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def destroy(self,req,pk=None):
        subject=get_object_or_404(Subjct,pk=pk)
        subject.delete()
        return Response({"message": "Subject deleted successfully"},status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True,methods=['put'],url_path='test', permission_classes=[IsAuthenticated,is_Student])
    def test(self,req,pk=None):
        subject=get_object_or_404(Subjct,pk=pk)
        test_instance = Test_Track.objects.filter(student=req.user,subject=subject,pass_status='runing').first()
        if not test_instance:
            return Response({"message": "No running test found"},status=400)
        
        if req.user.role == 'student':
            ser = self.get_serializer(test_instance,data=req.data,context={"request":req})
            ser.is_valid(raise_exception=True)
            ser.save()
            return Response({'message':"you comlete your statsu successfull"}, status=status.HTTP_200_OK)
        return Response({'message':"you can not give test"}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['GET','post'], url_path='chapter', permission_classes=[RBAC_Permission])
    def chapterOFSubject(self,req,pk=None):

        sub =get_object_or_404(Subjct,pk=pk)

        if req.user.role == 'student':
            if req.method == 'POST':
                return Response({"message":"you can not send post request"})
            if not Enrollment.objects.filter(course=sub.course,student=req.user).exists():
               if req.method in ['GET','POST']:
                   return Response({"message":"you can not access"})
                
        if req.method == 'GET':
            return Response(self.get_serializer(sub).data,status=status.HTTP_200_OK)
        
        if req.method =='POST':
            ser=self.get_serializer(data=req.data)
            ser.is_valid(raise_exception=True)     
            ser.save(subject = sub)
            return Response(ser.data,status=status.HTTP_201_CREATED)


    @action(detail=True,methods=['get'], url_path='pdf',permission_classes=[IsAuthenticated,RBAC_Permission])
    def get_pdf(self,req,pk=None):
        subject =get_object_or_404(Subjct,pk=pk)
        file =File.objects.filter(topics__chapter__subject =subject)
        return Response(FilePDFSerlizer(file,many=True).data,status=status.HTTP_200_OK)
    
    @action(detail=True,methods=['get'], url_path='demo',permission_classes=[IsAuthenticated])
    def getDemo(self,req,pk=None):
        subject =get_object_or_404(Subjct,pk=pk)
        demo =Demo.objects.filter(subject=subject)
        return Response(DemoSerlizerss(demo,many=True).data,status=status.HTTP_200_OK)


        





class ChapterViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated,RBAC_Permission]


    def get_serializer_class(self):
        if self.action == "topics":
            if self.request.method == 'POST':
                return TopicsWriteSerlizers
            else:
                return ChapterdSerlizers
        if self.action == 'create':
            return ChapterWriteSerlizers
        # if self.action == 'retrieve':
        #     return ChapterSerlizers
        return ChapterReadSerlizers
    
    

    def get_queryset(self):
        if self.request.user.role in ['admin','head_teacher']:
            return Chapter.objects.all()
        

        if self.request.user.role == 'teacher':
            return Chapter.objects.filter(subject__teacher=self.request.user)
        
        if self.request.user.role =='student':
            return Chapter.objects.filter(subject__course__enrollments__student=self.request.user ).order_by('index')
        
        return Chapter.objects.all()
    

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role =='student':
            tast = Test_Track.objects.filter(student=request.user,chapter=instance).first()

            if not tast:
                return Response({'message':"first complete your prev chapter"}, status=status.HTTP_400_BAD_REQUEST)
        return super().retrieve(request, *args, **kwargs)
        
        
    @action(detail=True,methods=['get','post'],url_path="topics",permission_classes=[IsAuthenticated,RBAC_Permission])
    def topics(self, request, pk=None):
        chapter = self.get_object()
        if request.method == 'GET':
            return Response(ChapterdSerlizers(chapter,context={"request":request}).data,status=status.HTTP_200_OK)
            

        if request.method == 'POST':

            if request.user.role == 'student':
                return Response({'message': 'You cannot create topics'},status=status.HTTP_403_FORBIDDEN)
            
            serializer = TopicsWriteSerlizers(data=request.data, context={'request':request})
            serializer.is_valid(raise_exception=True)
            serializer.validated_data['chapter']=chapter
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    @action(detail=True,methods=['get'],url_path="studentTest",permission_classes=[IsAuthenticated,RBAC_Permission])
    def studentTestData(self,request,pk=None):
        
        chapter = Chapter.objects.get(id=pk)
        pdfs = File.objects.filter(
            topics__chapter=chapter,
            file_type='PDF'
        )   

        full_text = ""
        for pdf in pdfs:
            pdf_path = pdf.file.url
            response = requests.get(pdf_path)
            reder = PdfReader(BytesIO(response.content))
            for page in reder.pages:
                full_text += page.extract_text() or ""
        full_text += "\n\n"
        
        questionData = generate_mcqs_from_text(full_text)
        
        cacheData = {}
        UiData = []
        for question in questionData["questions"]:
            qid = question["id"]

            cacheData[qid] = question["correct_answer"]

            cacheData[question["id"]] = question["correct_answer"]

            UiData.append({
                "id": qid,
                "question": question["question"],
                "options": question["options"]
            })
        cache_key = f"test_{request.user.id}_{chapter.id}"
        cache.set(
            cache_key,
            cacheData,
            timeout=1800
            )
        
        return Response({'question':UiData},
        status=status.HTTP_200_OK)
 
 
    @action(detail=True,methods=['get','put'],url_path="studentTestsubmitcheck",permission_classes=[IsAuthenticated,RBAC_Permission])
    def studentTestsubmit(self,request,pk=None):
        if request.method == 'GET':
            return Response({"msg":"good"})
        chapter = Chapter.objects.get(id=pk)
        cache_key = f"test_{request.user.id}_{chapter.id}"
        cacheData = cache.get(cache_key)
        userData = request.data
        
        correct_ans = 0
        totalQuestion = len(cacheData)
        for key in cacheData:
            selected = userData.get(str(key))
            if selected is None:
                continue
            if cacheData[key] == int(selected):
                correct_ans+=1

        percentage = (correct_ans/totalQuestion)*100

        test_track = Test_Track.objects.get(student=request.user,subject=chapter.subject,chapter=chapter)
        cache.delete(cache_key)
        if percentage >= 70:
            test_track.total_Q = totalQuestion
            test_track.correct_Q = correct_ans
            test_track.pass_status = 'pass'
            test_track.save()

            next_chapter = Chapter.objects.filter(
                subject=chapter.subject,
                index__gt=chapter.index,

            ).order_by('index').first()
            if next_chapter!= None:

                Test_Track.objects.get_or_create(
                    student=request.user,
                    course=test_track.course,
                    subject=test_track.subject,
                    chapter=next_chapter,
                    total_Q=0,
                    correct_Q=0
                )

                return Response({
                    "message": "Congratulations! You passed the test and the next chapter has been unlocked.",
                    "status": "pass",
                    "score": correct_ans,
                    "total": totalQuestion,
                    "percentage": percentage,
                    "marks":correct_ans/totalQuestion
                
                })
            else:
                return Response({
                    "message": "Congratulations! You passed all test",
                    "status": "pass",
                    "score": correct_ans,
                    "total": totalQuestion,
                    "percentage": percentage,
                    "marks":correct_ans/totalQuestion
                
                })
            
        else:
            test_track.total_Q = totalQuestion
            test_track.correct_Q = correct_ans
            test_track.pass_status = 'fail'
            test_track.save()
            return Response({
                    "message": "You have not met the passing criteria for this assessment. Please review the chapter content and retake the test.",
                    "status": "fail",
                    "score": correct_ans,
                    "total": totalQuestion,
                    "percentage": percentage,
                    "marks":correct_ans/totalQuestion
                
                })
    


    


    
class TopicViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated,RBAC_Permission]

    def get_serializer_class(self):
        if self.action in ['TeacherfileOpration','studentfileOpration','studentUncheckfileOpration']:
            return FileSerlizers 
        if self.action == 'studentUncheckfileOpration':
            return FileSerlizers_ForCheck
        if self.action in ['create','update']:
            return TopicsWriteSerlizers
        return TopicsSerlizers

    def get_queryset(self):
        if self.request.user.role in ['admin','head_teacher']:
            return Topics.objects.filter(role__in=['teacher','head_teacher','admin'])
        if self.request.user.role == 'teacher':
            return Topics.objects.filter(chapter__subject__teacher = self.request.user,role__in=['teacher','head_teacher','admin'])
        
        if self.request.user.role == 'student':
            return Topics.objects.filter(chapter__subject__course__enrollments__student = self.request.user,role__in=['teacher','head_teacher','admin'])

        return Topics.objects.none()
    

    def perform_create(self, serializer):
        user =self.request.user
        chapter = serializer.validated_data.get('chapter')
        if user.role == 'teacher':
            if chapter.subject.teacher != 'user':
                raise PermissionError('you are not able to upload content for this chapter ')
        serializer.save()


    @action(detail=True,methods=['get','post'],url_path='Teacher_files',permission_classes=[IsAuthenticated,RBAC_Permission])
    def TeacherfileOpration(self,req,pk=None):
        topic =self.get_object()
        if req.method == 'POST':
            ser=FileSerlizers(data=req.data)
            ser.is_valid(raise_exception=True)
            if req.user.role != 'student':
                checked = True
            else:
                checked = False
            ser.save(checked=checked,topics=topic,creater=req.user)

            return Response(ser.data,status=status.HTTP_201_CREATED)
        if req.method == 'GET':
            file = File.objects.filter(topics=topic,topics__role__in=['teacher','head_teacher','admin'])
            
            return Response(FileSerlizers(file,many=True,context={"request":req}).data,status=status.HTTP_200_OK)
        

    @action(detail=True,methods=['get','post'],url_path='student_files',permission_classes=[IsAuthenticated,RBAC_Permission])
    def studentfileOpration(self,req,pk=None):
        topic =self.get_object()
        if req.method == 'POST':
            ser=FileSerlizers(data=req.data)
            ser.is_valid(raise_exception=True)
            ser.topics=topic
            if req.user.role != 'student':
                checked = True
            else:
                checked = False
            ser.checked = checked
            ser.save(topics=topic,creater=req.user)
            return Response(ser.data,status=status.HTTP_201_CREATED)
        if req.method == 'GET':
            file = File.objects.all()
            serializer = FileSerlizers(file, many=True,context={"request":req})

            return Response(serializer.data,status=status.HTTP_200_OK)


    @action(detail=True,methods=['get','put'],url_path='uncheck_files',permission_classes=[IsAuthenticated,RBAC_Permission])
    def studentUncheckfileOpration(self,req,pk=None):
        topic =self.get_object()
        if req.method == 'PUT':
            ser=FileSerlizers_ForCheck(data=req.data,partail=True)
            ser.is_valid(raise_exception=True)
            ser.save(checked=checked,topics=topic,creater=req.user)
            return Response(ser.data,status=status.HTTP_201_CREATED)
        if req.method == 'GET':
            file = File.objects.filter(topics=topic,checked=False)
            return Response(FileSerlizers_ForCheck(file,many=True).data,status=status.HTTP_200_OK)
        
   

    @action(detail=True,methods=["post"],url_path="ai-topic-tutor",permission_classes=[IsAuthenticated])
    def studentDoutSolve(self, request, pk=None):
        doubt = request.data.get("Dout")
 

        if not doubt:
            return Response(
                {"error": "Dout is required"},
                status=400
            )
 
        solution = doubt_solve(            
            doubt
        )
        

        return Response(
            {"data": solution}
        )


class FileViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated,RBAC_Permission]
    serializer_class = FileSerlizers_ForCheck

    queryset = File.objects.filter(checked=False)
    http_method_names = ['get', 'patch']
    # doubt_solve()




class EnrollmentView_Set(ViewSet):
    def create(self,req):
        ser =EnrollmentWriteSerlizers(data=req.data,context={'request':req})
        if req.user.role != "student":
            return Response({"error": "You are not authorized"},
                status=status.HTTP_403_FORBIDDEN
            )
        ser.is_valid(raise_exception=True)
        course = ser.validated_data['course']
        # subjects=course.subjects.all()
        
        # for subject in subjects:
            # first_chapter = Chapter.objects.filter(
            #     subject_id=subject.id
            # ).order_by('index').first()

            # Test_Track.objects.create(
            #     student=req.user,
            #     course=course,
            #     subject=subject,
            #     chapter=first_chapter,
            #     total_Q=0,
            #     correct_Q=0
            # )
        ser.save(student=req.user)
        return Response({'message':f"you have enrilled in {course} course"},status=status.HTTP_201_CREATED)
    





class BuyCourseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):

        course = Course.objects.get(id=course_id)

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        # amount_in_paise = int(course.fee * 100)
        amount_in_paise = int(course.fee * 100)

        order = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR"
        })

        Payment.objects.create(
            student=request.user,
            course=course,
            order_id=order["id"],
            amount=course.fee
        )

        return Response({
            "order_id": order["id"],
            "amount": amount_in_paise,
            "key": settings.RAZORPAY_KEY_ID
        })
    




class VerifyPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        if not all([
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature
        ]):
            return Response(
                {
                    "status": False,
                    "message": "Missing payment data"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            client = razorpay.Client(
                auth=(
                    settings.RAZORPAY_KEY_ID,
                    settings.RAZORPAY_KEY_SECRET
                )
            )

            # client.utility.verify_payment_signature({
            #     "razorpay_order_id": razorpay_order_id,
            #     "razorpay_payment_id": razorpay_payment_id,
            #     "razorpay_signature": razorpay_signature
            # })

            payment = Payment.objects.get(
                order_id=razorpay_order_id
            )

            payment.payment_id = razorpay_payment_id
            payment.status = "SUCCESS"
            payment.save()

            # Enrollment.objects.get_or_create(
            #     student=request.user,
            #     course=payment.course,
            #     defaults={
            #         "fee_submit": True,
            #         "enroll": True
            #     }
            # )

            serializer = EnrollmentWriteSerlizers(
                data={
                    "course": payment.course.id
                },
                context={
                    "request": request
                }
            )

            serializer.is_valid(raise_exception=True)

            serializer.save(student=request.user)

            return Response(
                {
                    "status": True,
                    "message": "Payment verified successfully"
                },
                status=status.HTTP_200_OK
            )

        except Payment.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Payment record not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )    
        

class GenerateCertificateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        student = request.user

        try:
            course = Course.objects.get(id=pk)
        except Course.DoesNotExist:
            return Response(
                {"error": "Course not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        certificate = Certificate.objects.filter(
            student=student,
            course=course
        ).first()

        if not certificate:
            serializer = CertificatewriteSerlizer(
                data={"course": course.id},
                context={"request": request}
            )

            serializer.is_valid(raise_exception=True)

            certificate = serializer.save()

            message = "Certificate generated successfully"

        else:
            message = "Certificate already exists"

        file_url = request.build_absolute_uri(
            certificate.certificate_file.url
        )

        return Response(
            {
                "message": message,
                "certificate_id": certificate.certificate_id,
                "certificate_file": file_url
            },
            status=status.HTTP_200_OK
        )
