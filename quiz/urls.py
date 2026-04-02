from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_list, name='quiz_exam_list'),
    path('exam/<int:exam_id>/', views.quiz_list, name='quiz_list'),
    path('exam/<int:exam_id>/lookup/', views.question_lookup, name='question_lookup'),
    path('quiz/<int:quiz_id>/start/', views.quiz_start, name='quiz_start'),
    path('quiz/<int:quiz_id>/question/<int:index>/', views.quiz_question, name='quiz_question'),
    path('quiz/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    path('quiz/check-answer/', views.check_answer, name='quiz_check_answer'),
]
