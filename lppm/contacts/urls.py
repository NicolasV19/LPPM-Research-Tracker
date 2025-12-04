from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
    path('', views.index, name='index'),
    path('', views.proposal_list, name='proposal_list'),
    path('search/', views.search_contacts, name='search'),
    path('create/', views.create_contact, name='create_contact'),
    path('edit/<int:pk>/', views.edit_contact, name='edit_contact'),
    path('delete/<int:pk>/', views.delete_contact, name='delete_contact'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('new/', views.proposal_create, name='proposal_create'),
    path('<int:pk>/edit/', views.proposal_update, name='proposal_update'),
    path('<int:pk>/delete/', views.proposal_delete, name='proposal_delete'),
]
