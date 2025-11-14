from django.urls import path
from .views import AddressViewSet

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
    path('addresses/', address_list, name='address-list'),
    path('addresses/<int:pk>/', address_detail, name='address-detail'),
]
