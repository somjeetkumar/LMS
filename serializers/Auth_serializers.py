from Auth_system.models import User,EmailOTP
from rest_framework import serializers
import random
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.conf import settings



class Register_Serializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True)
    check_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username','email','role','profile_image','password','check_password','is_active']
        read_only_fields = ['is_active']

    def validate(self, data):
        
        if data['role'] in ['teacher','head_teacher']:
            raise serializers.ValidationError('you are authenticate for create this role user')
        if data.get('password') != data.get('check_password'):
            raise serializers.ValidationError('password is not match')
        
        return data

    def create(self, validated_data):
        
        check_password = validated_data.pop('check_password')
        password =  validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = False
        user.save()

        return user
    


class Login_serializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        
        user = User.objects.filter(username=data['username']).first()
        
        if user == None:
            raise serializers.ValidationError('incorrect username or password')
        if user.is_active == False:
            old_otp = EmailOTP.objects.filter(user=user).last()
            if old_otp:
                old_otp.delete()
            else:
        
                pass
            otp = str(random.randint(100000, 999999))
            EmailOTP.objects.create(user=user, otp=otp)
            # send_mail("Your OTP",f"Your OTP is {otp}","somjeetkumar30@gmail.com",[user.email],)
            # f"Your OTP Your OTP is {otp} somjeetkumar30@gmail.com",
            send_mail(
            subject="Welcome to Our Platform",
            message=f"Your OTP Your OTP is {otp} somjeetkumar30@gmail.com",
            # from_email [user.email],
            from_email=settings.EMAIL_HOST_USER,            
            recipient_list=[user.email],
            fail_silently=False,)
            raise serializers.ValidationError({"message":"Email not verified frist fill your OTP","err":"account_not_verified"})
        
        user = authenticate(
            username=data['username'],
            password=data['password'],
        )
        
        if not user:
            raise serializers.ValidationError('Invalid Information')
    
        
        data['user'] = user
        return data
    


class Register_teacher_serializer(serializers.ModelSerializer): 
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username','email','role','profile_image','password']

    def validate(self, data):
    
        if not data['role'] in ['teacher','head_teacher']:
            raise serializers.ValidationError('you can not admin role user')
        
        return data
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
        



class teacherReadSeriserz(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =['id','username','email','role']




class verify_mailserlizers(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField(write_only=True)

    def validate(self, data):     
        
        username =data.get('username')   
        otp= data.get('otp')
        user = User.objects.get(username=username)
        otp_obj = EmailOTP.objects.filter(user=user, otp=otp).last()

        if not otp_obj:
            raise serializers.ValidationError( 'otp not valid')
        if otp_obj.is_expired():
            raise serializers.ValidationError({"error": "OTP expired"})
        user.is_active = True
        user.save()
        otp_obj.delete()
        data['is_active']=True
        return data






class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','role','profile_image','is_active']