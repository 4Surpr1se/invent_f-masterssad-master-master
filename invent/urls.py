"""invent URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter

from core import views
from core.views import OrganizationRetrieve, OrganizationList, OrganizationCreate, DepartmentRetrieve, DepartmentList, \
    DepartmentCreate, HoldingRetrieve, HoldingList, HoldingCreate, OrganizationDelete, OrganizationUpdate, Inner, \
    InnerUpdate, PropertyCreate, HoldingUpdate, OrganizationModelViewSet, Udsa

router = DefaultRouter()
router.register('org', OrganizationModelViewSet, basename='org')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('organization/<pk>', OrganizationRetrieve.as_view()),
    path('organization/', OrganizationList.as_view()),
    path('organization/create/', OrganizationCreate.as_view()),
    path('department/<pk>', DepartmentRetrieve.as_view(), ),
    path('department/', DepartmentList.as_view()),
    path('department/create/', DepartmentCreate.as_view()),
    path('holding/<pk>', HoldingRetrieve.as_view(), name='holding'),
    path('department/(?P<organization_id>[0-9]+)$', DepartmentList.as_view(), name='name'),
    path('holding/', HoldingList.as_view()),
    path('holding/create/', HoldingCreate.as_view()),
    path('organization/delete/', OrganizationDelete.as_view()),
    path('organization/update/', OrganizationUpdate.as_view()),
    path('inner/', Inner.as_view()),
    path('inner/update/', InnerUpdate.as_view()),
    path('inner/create/', PropertyCreate.as_view()),
    path('holding/update/', HoldingUpdate.as_view()),
    path('', include(router.urls)),
    path('s/update/', Udsa.as_view())
]

