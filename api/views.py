from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from . serializers import *
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from django.db.models import Q
from .custompermission import UserPermision


class UserRegistration(APIView):
    def post(self,request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            User.objects.create_user(
                username = serializer.validated_data['username'],
                email = serializer.validated_data['email'],
                password = serializer.validated_data['password'],
                is_doctor = serializer.validated_data['is_doctor'],
            )
            return Response({"Message":"Registration Success!!!"},status=status.HTTP_201_CREATED)
        return Response({"Message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer = MyTokenObtainPairSerializer

class UserProfile(APIView):
    def get(self,request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def patch(self,request):
        serializer = UserProfileSerializer(request.user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"Message":"Profile Updated","profile":serializer.data},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request):
        user = User.objects.get(id=request.user.id)
        user.delete()
        return Response({"Message":"Deleted"},status=status.HTTP_200_OK)

@permission_classes([IsAdminUser])
class UserProfileView(APIView):
    def get(self,request,pk=None):
        if pk is None:
            user = User.objects.exclude(is_admin=True)
            serializer = UserProfileAdminSerializer(user,many=True)
            return Response(serializer.data)
        user = User.objects.get(pk=pk)
        serializer = UserProfileAdminSerializer(user)
        return Response(serializer.data)
    def patch(self,request,pk=None):
        if pk is not None:
            user=User.objects.get(pk=pk)
            serializer=UserProfileAdminSerializer(user,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                if serializer.validated_data['is_active']:
                    return Response({"Message":"User Unblocked.!!!"},status=status.HTTP_200_OK)
                return Response({"Message":"User Blocked.!!"},status=status.HTTP_200_OK)
            return Response(serializer.errors)
        
@permission_classes([UserPermision])
class UserDoctorView(APIView):
    def get(self,request):
        q = request.GET.get('q')
        Q_Base = Q(doctor__is_verified=True)
        search_query = Q()
        if q:
            search_query = Q(username__icontains=q)|Q(doctor__department__icontains=q)|Q(doctor__hospital__icontains=q)
            Q_Base &= search_query 
        user = User.objects.filter(Q_Base)
        serializer = UserProfileAdminSerializer(user,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)