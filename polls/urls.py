from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
  path('', views.index, name='index'),
  path('<int:question_id>/', views.detail, name='detail'),
  path('<int:question_id>/results/', views.results, name='results'),
  path('<int:question_id>/vote/', views.vote, name='vote'),
  path('add/', views.add_poll, name='add_poll'),
  path('search/', views.search, name='search'),
  path('register/', views.register, name='register'),
  path('login/', views.login_view, name='login'),
  path('logout/', views.logout_view, name='logout'),
  path('delete/<int:question_id>/', views.delete, name='delete')
]