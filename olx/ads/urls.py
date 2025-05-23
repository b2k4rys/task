from django.urls import path
from . import views

urlpatterns = [
    path('ad/create/', views.ad_create, name='ad_create'),
    path('ad/edit/<int:ad_id>/', views.ad_edit, name='ad_edit'),
    path('ad/delete/<int:ad_id>/', views.ad_delete, name='ad_delete'),
    path('ad/list/', views.ad_list, name='ad_list'),
    path('proposal/create/<int:ad_sender_id>/<int:ad_receiver_id>/', views.proposal_create, name='proposal_create'),
    path('proposal/update/<int:proposal_id>/', views.proposal_update, name='proposal_update'),
    path('proposal/list/', views.proposal_list, name='proposal_list'),
]