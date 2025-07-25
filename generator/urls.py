from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate/', views.generate_testcases, name='generate_testcases'),
    path('result/', views.result, name='result'),
    path('api/testcases.json', views.test_cases_json, name='test_cases_json'),
    path('api/testcase/<int:case_id>.json', views.test_case_json, name='test_case_json'),
]