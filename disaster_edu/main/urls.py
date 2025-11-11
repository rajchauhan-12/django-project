from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('awareness/', views.awareness, name='awareness'),
    path('awareness/<str:disaster_name>/', views.disaster_detail, name='disaster_detail'),
    path('tips/', views.tips, name='tips'),
    path('quiz/', views.quiz, name='quiz'),
    path('contact/', views.contact, name='contact'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    
]
