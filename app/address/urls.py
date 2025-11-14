from django.urls import path
from .views import AddressViewSet

app_name = "address"

address_list = AddressViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

address_detail = AddressViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('address/', address_list, name='address-list'),
    path('address/<int:pk>/', address_detail, name='address-detail'),
]
