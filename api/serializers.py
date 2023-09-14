from rest_framework import serializers
from rest_framework_simplejwt.tokens import Token
from .models import *
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type':'password'},write_only=True)
    is_doctor = serializers.BooleanField(default=False,required=False)
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ['username','email','password','confirm_password','is_doctor']
        
    def validate(self,data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password != confirm_password:
            return serializers.ValidationError('Passwords Does Not Match!!!')
        return data
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_doctor'] = user.is_doctor
        if hasattr(user,'id_admin'):
            token['is_admin'] = user.is_admin
        return token

class DoctorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    hospital = serializers.CharField(required=False)
    department = serializers.CharField(required=False)
    class Meta:
        model = Doctor
        fields = ['id','hospital','department','user']
        read_only_fields =('user',)

class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    class Meta:
        model = User
        fields = ['id','first_name','last_name','username','email']

    def __init__(self,*args,**kwargs):
        print(args)
        super().__init__(*args,**kwargs)
        user = args[0]
        print(user)
        if user.is_doctor:
            self.fields['doctor']=DoctorSerializer()

    def update(self,instance,validated_data):
        instance.first_name = validated_data.get('first_name',instance.first_name)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.username =  validated_data.get('username',instance.username)
        instance.email = validated_data.get('email',instance.email)

        if instance.is_doctor:
            doctor_data = validated_data.get('doctor')
            if doctor_data:
                doctors = Doctor.objects.filter(user=instance)
                if doctors.exists():
                    doctor = doctors.first()
                    doctor.hospital = doctor_data.get('hospital',doctor.hospital)
                    doctor.department = doctor_data.get('department',doctor.department)
                    if doctor.hospital is not None and doctor.department is not None:
                        doctor.is_verified=True
                    doctor.save()
                else:
                    raise ValidationError("No doctor data found for this user.")
        instance.save()
        return instance

class UserProfileAdminSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id','first_name','last_name','username','email','is_doctor','is_active','doctor']

    def update(self,instance,validated_data):
        instance.is_active = validated_data.get('is_active',instance.is_active)
        instance.save()
        return instance

