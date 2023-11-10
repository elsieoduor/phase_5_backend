from django.urls import path, include
from . import views


urlpatterns = [ 
    #authentication
    path('register/', views.registerView.as_view(), name='register'),
    path('login/', views.loginView.as_view(), name='login'),
    path('user/', views.userView.as_view()),
    path('logout/', views.logoutView.as_view(), name='logout'),

    #user part
    #Children's Homes user functionality
    path('children_orphanages/', views.children_orphanages, name='children_orphanages'),
    path('orphanage/search/', views.orphanage_search, name='search_children_orphanage'),
    path('orphanage/<int:id>/', views.orphanage_detail, name='orphanage_detail'),
    
    path('donations/', views.donations, name='donations'),
    path('reviews/', views.reviews, name='reviews'),
    path('visits/', views.visit, name='visits'),

    #chief part
    path('chief_dashboard/', views.chief_dashboard, name='chief_dashboard'),
    #crud on users
    path('users/', views.users, name='users'),
    path('user/<int:id>', views.user_details, name='user_detail'),

   
    path('analytics/most_visited_home', views.most_visited_home, name='most_visited_home'),
    path('analytics/most_in_need_home', views.most_in_need_home, name='most_in_need_home'),
 
    
]