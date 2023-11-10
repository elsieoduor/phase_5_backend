from django.shortcuts import render, redirect
from rest_framework import status
from django.urls import reverse
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .serializer import UserSerializer, ReviewSerializer, VisitSerializer, DonationSerializer, ChildrenOrphanageSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import Donation, ChildrenOrphanage, User, Review, Visit
import jwt, datetime, secrets
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.db.models import F
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
#Authentications.
def is_chief(user):
    return user.role == 'Chief'

def is_user(user):
    return user.role == 'User'

class registerView(APIView):
  def post(self, request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
  
class loginView(APIView):
  def post(self, request):
    email = request.data['email']
    password = request.data['password']

    user = User.objects.filter(email=email).first()
    if user is None:
      raise AuthenticationFailed('user not found!')
    
    if not user.check_password(password):
      raise AuthenticationFailed('incorrect password!')
    
    payload ={
      'id':user.id,
      'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
      'iat': datetime.datetime.utcnow()
    }
    # token = jwt.encode(payload, 'secret', algorithm= 'HS256').decode('utf-8')
    token_bytes = jwt.encode(payload, 'secret', algorithm='HS256')
    refresh_token = secrets.token_urlsafe(20)

    if isinstance(token_bytes, bytes):
        token = token_bytes.decode('utf-8')
    else:   
        token = token_bytes

    response = Response()
    response.set_cookie(key='jwt', value=token, httponly=True)
    response.data = {'jwt': token, 'refresh_token': refresh_token}

    if user.role == 'Chief':
        return HttpResponseRedirect(reverse('chief_dashboard'))  # Use 'reverse' with the URL name
    elif user.role == 'User':
        return HttpResponseRedirect(reverse('donations'))  # Use 'reverse' with the URL name
    else:
        raise AuthenticationFailed('Invalid user role')
    # return response
  
class userView(APIView):
  def get(self, request):
    token = request.COOKIES.get('jwt')

    if not token:
      raise AuthenticationFailed('Not authenticated')
    
    try:
      payload = jwt.decode(token, 'secret', algorithm=['HS256'])
    except jwt.ExpiredSignatureError:
      raise AuthenticationFailed('Token expired or invalid')
    
    user = User.objects.filter(id =payload['id']).first()

    if user.role == 'Chief':
        return HttpResponseRedirect(reverse('chief_dashboard'))
    elif user.role == 'User':
        return HttpResponseRedirect(reverse('donations')) 
    else:
        raise AuthenticationFailed('Invalid user role')
   
class logoutView(APIView):
  def post(self, request):
    response = Response()
    response.delete_cookie('jwt')
    response.data ={
      'message': 'delete successful'
    }
    return response
  
@login_required
@user_passes_test(is_user)
@api_view(['GET', 'POST'])
def reviews(request): 
    if request.method == 'GET':
        review = Review.objects.all()
        serializer = ReviewSerializer(review, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ReviewSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@user_passes_test(is_user)
@api_view(['GET', 'POST'])
def visit(request):
    if request.method == 'GET':
        visit = Visit.objects.all()
        serializer = VisitSerializer(visit, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data
        serializer = VisitSerializer(data=data)
        if serializer.is_valid():
            visit = serializer.save()

            home_id = data.get('children_orphanage')
            home = ChildrenOrphanage.objects.get(id = home_id)
            home.visit +=1
            home.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
@login_required
@user_passes_test(is_user)
@api_view(['GET', 'POST'])
def children_orphanages(request):
    if request.method == 'GET':
        homes = ChildrenOrphanage.objects.all()
        serializer = ChildrenOrphanageSerializer(homes, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ChildrenOrphanageSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@user_passes_test(is_user)
@api_view(['GET','POST'])
def donations(request):
    if request.method == 'GET':
        donations = Donation.objects.all()
        serializer = DonationSerializer(donations, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = DonationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            donation = serializer.instance 
            children_home = ChildrenOrphanage.objects.get(id=id)

            if donation.donated_item == 'clothes':
                ChildrenOrphanage.objects.filter(id=id).update(needs_clothes=F('needs_clothes') - 1)
            elif donation.donated_item == 'hygiene':
                ChildrenOrphanage.objects.filter(id=id).update(needs_hygiene_supplies=F('needs_hygiene_supplies') - 1)
            elif donation.donated_item == 'food':
                ChildrenOrphanage.objects.filter(id=id).update(needs_food=F('needs_food') - 1)
            elif donation.donated_item == 'money':
                ChildrenOrphanage.objects.filter(id=id).update(needs_money=F('needs_money') - 1)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
# @user_passes_test(is_chief)
def orphanage_search(request):
    if 'query' in request.GET:
        query = request.GET['query']
    else:
        query = None

    if 'location' in request.GET:
        location = request.GET['location']
    else:
        location = None

    if query and location:
        results = ChildrenOrphanage.objects.filter(name__icontains=query, location__icontains=location)
    elif query:
        results = ChildrenOrphanage.objects.filter(name__icontains=query)
    elif location:
        results = ChildrenOrphanage.objects.filter(location__icontains=location)
    else:
        results = None

    return render(request, 'default/children_homes_search.html', {'results': results})

@login_required
@user_passes_test(is_chief)

#Admin MVP
@login_required
@user_passes_test(is_chief)
def chief_dashboard(request):
    return render(request, 'chief/dashboard.html')

@api_view(['GET', 'PUT', 'DELETE'])
def orphanage_detail(request, id):
    try:
        children_orphanage = ChildrenOrphanage.objects.get(id=id)
    except ChildrenOrphanage.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ChildrenOrphanageSerializer(children_orphanage)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ChildrenOrphanageSerializer(children_orphanage, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST )
    elif request.method == 'DELETE':
        children_orphanage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#User CRUD
@login_required
@user_passes_test(is_chief)
@api_view(['GET', 'POST'])
def users(request):
    if request.method == 'GET':
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@user_passes_test(is_chief)
@api_view(['GET', 'PUT', 'DELETE'])
def user_details(request, id):
  try:
        user = User.objects.get(id=id)
  except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

  if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
  elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST )
  elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  


#Analytics
@login_required
@user_passes_test(is_chief)
@api_view(['GET'])
def most_visited_home(request):
    upcoming_visits = Visit.objects.filter(visit_date__gte=timezone.now())
    most_visited_home = ChildrenOrphanage.objects.order_by('-visit').first()
    
    if most_visited_home:
        serializer = ChildrenOrphanageSerializer(most_visited_home)
        context = {
            'most_visited_home': serializer.data,
            "upcoming_visits": VisitSerializer(upcoming_visits, many=True).data
        }
        return Response(context, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'No most visited home found'}, status=status.HTTP_404_NOT_FOUND)

@login_required
@user_passes_test(is_chief)
@api_view(['GET'])
def most_in_need_home(request):
    if request.method == 'GET':
        most_in_need_home = ChildrenOrphanage.objects.order_by('-needs').first()
        serializer = ChildrenOrphanageSerializer(most_in_need_home)
        return Response(serializer.data, status=status.HTTP_200_OK)
