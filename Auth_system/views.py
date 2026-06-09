from django.shortcuts import render,get_object_or_404
from rest_framework.viewsets import ModelViewSet,ViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from threading import Thread

from RBAC.auth_permission import  is_Admin,is_HeadTeacher
from django.core.mail import send_mail
import random
from serializers.Auth_serializers import Login_serializer,Register_Serializer,Register_teacher_serializer,teacherReadSeriserz,verify_mailserlizers,UserReadSerializer
from .models import User,EmailOTP
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


# Create your views here.
def send_otp_email(user,otp):
    
    send_mail(
            subject="Welcome to Our Platform",
            message=f"Your OTP Your OTP is {otp} somjeetkumar30@gmail.com",
            # from_email [user.email],
            from_email=settings.EMAIL_HOST_USER,            
            recipient_list=[user.email],
            fail_silently=False,)

class RegisterViewSet(ViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]
    def create(self,request):
        serializer = Register_Serializer(data=request.data,            )
        serializer.is_valid(raise_exception=True)
        user =serializer.save()

        otp = str(random.randint(100000, 999999))

        EmailOTP.objects.create(user=user, otp=otp)
        
        Thread(
            target=send_otp_email,
            args=(user, otp)
        ).start()
        

        
        return Response({'message':"User is created"},status=status.HTTP_201_CREATED)
    


class LoginViewSet(ViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self,request):
        
        serliazer = Login_serializer(data=request.data)
        serliazer.is_valid(raise_exception=True)
        user = serliazer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        response = Response({
            "message":"user login successful",
            "access":str(refresh.access_token),
            "refresh":str(refresh),
            "user":{
                "id":user.id,
            "username":user.username,
            "email":user.email,
            "role":user.role
            }
            })
        response.set_cookie(key="access",value=str(refresh.access_token),httponly=True,samesite="Lax")
        response.set_cookie(key="refresh",value=str(refresh),httponly=True,samesite="Lax")
        return response
 



class RefreshAccessTokenView(APIView):
    permission_classes = [AllowAny]
    # authentication_classes = []

    def post(self,request):
        refresh_token = request.data.get('refresh')
        
        if(not refresh_token):
            return Response(
                {"error": "Refresh token required"},
                status=status.HTTP_400_BAD_REQUEST
            )


        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            return Response({
                "access": access_token
            })
        except :
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
class LoginUserDetails(ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self,request):
        return Response({
            "id":request.user.id,
            "username":request.user.username,
            "email":request.user.email,
            "role":request.user.role
        })
    



class Teacher_register_ViesSet(ViewSet):
    # authentication_classes = []
    def get_permissions(self):
        if self.action == 'create':
            return [is_Admin()]
        return []


    def create(self,request):
        
        serializer = Register_teacher_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message':"teacher is register"},status=status.HTTP_201_CREATED)
    
    def list(self,req):
        teachers =User.objects.filter(role__in= ['head_teacher','teacher'])
        return Response(teacherReadSeriserz(teachers,many=True).data,status=status.HTTP_200_OK)
    
    def retrieve(self,req,pk):
        user = get_object_or_404(User, pk=pk)
        return Response(teacherReadSeriserz(user).data,status=status.HTTP_200_OK)


    def update(self,req,pk):
        user = get_object_or_404(User, pk=pk)
        ser = teacherReadSeriserz(user, data=req.data,partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data,status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self,req,pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response({'message':"user is successFully delete"}, status=status.HTTP_204_NO_CONTENT)



class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        
        ser =verify_mailserlizers(data=request.data)
        ser.is_valid(raise_exception=True)
        if ser.validated_data['is_active'] == True:
            return Response({"message": "Account verified"})
        else:
            return Response({"message": "Account is not verified"})

        
class reSendOtpView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username")
        try:
            user = User.objects.get(username=username)
            old_otp = EmailOTP.objects.filter(user=user).last()
            if old_otp:
                old_otp.delete()
            else:
                pass           
            otp = str(random.randint(100000, 999999))
            EmailOTP.objects.create(user=user, otp=otp)
            # send_mail(f"Password Reset OTP Your OTP is {otp} your_email@gmail.com",[user.email])
            send_mail(
            subject="Welcome to Our Platform",
            message=f"Your OTP is {otp} somjeetkumar30@gmail.com",
            # from_email [user.email],
            from_email=settings.EMAIL_HOST_USER,            
            recipient_list=[user.email],
            fail_silently=False,)
            return Response({"message": "OTP sent to email"})

        except User.DoesNotExist:
            return Response({"error": "User not found"})
        




class ForgotPasswordView(APIView):
    
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get("username")
        try:
            user = User.objects.get(username=username)

            old_otp = EmailOTP.objects.filter(user=user).last()
            if old_otp:
                old_otp.delete()
            else:
                pass 

            otp = str(random.randint(100000, 999999))
            EmailOTP.objects.create(user=user, otp=otp)
            # send_mail(f"Password Reset OTP Your OTP is {otp} your_email@gmail.com",[user.email])
            send_mail(
            subject="Welcome to Our Platform",
            message=f"Your OTP Your OTP is {otp} somjeetkumar30@gmail.com",
            # from_email [user.email],
            from_email=settings.EMAIL_HOST_USER,            
            recipient_list=[user.email],
            fail_silently=False,)
            return Response({"message": "OTP sent to email"})

        except User.DoesNotExist:
            return Response({"error": "User not found"})




class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get("username")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        try:
            user = User.objects.filter(username=username).first()
            otp_obj = EmailOTP.objects.filter(user=user, otp=otp).last()

            if not otp_obj:
                return Response({"error": "Invalid OTP"},status=status.HTTP_400_BAD_REQUEST)
                

            if otp_obj.is_expired():
                return Response({"error": "OTP expired"},status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            otp_obj.delete()

            return Response({"message": "Password reset successful"})

        except User.DoesNotExist:
            return Response({"error": "User not found"},status=status.HTTP_400_BAD_REQUEST)
        



class TeacherListView(APIView):
    permission_classes = [is_Admin | is_HeadTeacher]
    

    def get(self, request):
        if request.user.role == 'admin':
            teachers = User.objects.filter(role__in=['teacher'])

        elif request.user.role == 'head_teacher':
            teachers = User.objects.filter(
                role='teacher',
                subjects__course__M_teacher=request.user
            ).distinct()

        serializer = UserReadSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    





class HeadTeacherListView(APIView):
    permission_classes = [is_Admin]
    

    def get(self, request):
        
        teachers = User.objects.filter(role='head_teacher')

        serializer = UserReadSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)