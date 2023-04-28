import json
from abc import abstractmethod

from django.db import transaction, models
from django.http import JsonResponse, HttpResponse, QueryDict
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import filters, status, serializers
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.serializer import OrganizationSerializer, DepartmentSerializer, \
    DepartmentCreateSerializer, HoldingCreateSerializer, HoldingSerializer, PropertySerializer, \
    OrganizationSerializer, OrganizationCreateUpdateSerializer, DepartmentCreateUpdateSerializer, \
    HoldingCreateUpdateSerializer, MolCreateUpdateSerializer, MolSerializer, InventoryListSerializer, \
    InventoryListCreateUpdateSerializer, PropertyCreateUpdateSerializer
from .fixture import script
from .models import Holding, Organization, Department, Mol, Property, InventoryList


# ModelViewSet
class ModelViewSetMixin(ModelViewSet):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    @property
    @abstractmethod
    def create_update_serializer_class(self):
        pass

    @property
    @abstractmethod
    def search_filter(self):
        pass

    @property
    @abstractmethod
    def upper_query_filter(self):
        pass

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset().get(pk=kwargs['pk'])
        return Response({'organizations': [queryset]}, template_name='organization.html')

    def list(self, request, *args, **kwargs):
        self.queryset = self.get_queryset()
        if query_name := request.query_params.get('search'):
            self.queryset = self.queryset.filter(**{f'{self.search_filter}__contains': query_name})  # TODO

        if upper_query := request.query_params.get(f'{self.upper_query_filter}_id'):
            self.queryset = self.queryset.filter(**{f'{self.upper_query_filter}__id': upper_query})

        return Response(self.template_dict(request), template_name='template.html')

    def template_dict(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.queryset, many=True)
        upper_serializer = self.upper_serializer_class(self.upper_queryset, many=True) if hasattr(self, 'upper_serializer_class') else None
        return_dict = {
            'btn_fields': {
                'lower_name': self.lower_name if hasattr(self, 'lower_name') else self.search_filter,
                'lower_url': self.lower_url,
                'upper_name': self.upper_query_filter,
                'upper_url': self.upper_url  # TODO Переделать, чтобы можно было ввести upper_url и при его
                # TODO отсутствии вставлялся self.upper_query_filter и вообще в целом сделать чтобы словарь собирался
                # TODO через кастом класс где-нибудь за сценой

            },
            'query': serializer.data,
            'upper_query': upper_serializer.data if upper_serializer is not None else None,
            'model': self.queryset.model,  # TODO мб все-таки стоит оставить self.model
            'model_name': self.queryset.model.__name__.lower(),  # TODO мб можно избавиться
            # TODO если можно будет достававть имя в шаблоне
            'upper_model': self.upper_queryset.model if hasattr(self, 'upper_queryset') else None,
            'success_create': bool(request.query_params.get('success_create'))  # TODO переделать
        }

        return return_dict

    def create(self, request, *args, **kwargs):
        organization = super().create(request, *args, **kwargs)

        return organization

    def get_serializer_class(self):
        if self.action == 'update':  # TODO Реализовать через Meta.list_serializer_class
            return self.create_update_serializer_class
        elif self.action == 'create':
            return self.create_update_serializer_class
        else:
            return super(ModelViewSetMixin, self).get_serializer_class()

    def get_object(self):
        if self.action == 'update':
            return [x for x in self.queryset.filter(id__in=[x['id'] for x in self.request.data])]
        else:
            return super(ModelViewSetMixin, self).get_object()

    def get_serializer(self, *args, **kwargs):
        if self.action == 'update':
            serializer_class = self.create_update_serializer_class
            self.renderer_classes = None  # ?????
            kwargs.setdefault('context', self.get_serializer_context())
            kwargs['many'] = True
            return serializer_class(*args, **kwargs)
        else:
            return super(ModelViewSetMixin, self).get_serializer(*args, **kwargs)

    @action(methods=['DELETE'], detail=False)
    def delete(self, request):
        delete_id = request.data['id']
        query_before_update = list(self.queryset.filter(id__in=delete_id))
        delete_list = self.queryset.filter(id__in=delete_id).update(is_deleted=True)

        return Response(self.serializer_class(query_before_update, many=True).data)


class OrganizationModelViewSet(ModelViewSetMixin):
    queryset = Organization.objects.filter(is_deleted=False)
    model = Organization
    serializer_class = OrganizationSerializer
    create_update_serializer_class = OrganizationCreateUpdateSerializer
    upper_query_filter = 'holding'
    search_filter = 'name'
    lower_url = 'dep'
    upper_url = 'hol'
    upper_queryset = Holding.objects.all()
    upper_serializer_class = HoldingSerializer


class DepartmentModelViewSet(ModelViewSetMixin):
    queryset = Department.objects.filter(is_deleted=False)
    model = Department  # TODO НУЖНО ЛИ?
    serializer_class = DepartmentSerializer
    create_update_serializer_class = DepartmentCreateUpdateSerializer
    upper_query_filter = 'organization'
    search_filter = 'name'
    lower_url = 'mol'
    upper_url = 'org'
    upper_queryset = Organization.objects.filter(is_deleted=False)
    upper_serializer_class = OrganizationSerializer


class HoldingModelViewSet(ModelViewSetMixin):
    queryset = Holding.objects.filter(is_deleted=False)
    model = Holding  # TODO НУЖНО ЛИ?
    serializer_class = HoldingSerializer
    create_update_serializer_class = HoldingCreateUpdateSerializer
    upper_query_filter = ''
    search_filter = 'name'
    lower_url = 'org'
    upper_url = ''

class MolModelViewSet(ModelViewSetMixin):
    queryset = Mol.objects.filter(is_deleted=False)
    model = Mol  # TODO НУЖНО ЛИ?
    serializer_class = MolSerializer
    create_update_serializer_class = MolCreateUpdateSerializer
    upper_query_filter = 'department'
    search_filter = 'name'
    lower_url = 'inv'
    lower_name = 'FIO'
    upper_url = 'dep'
    upper_queryset = Department.objects.filter(is_deleted=False)
    upper_serializer_class = DepartmentSerializer


class InventoryListModelViewSet(ModelViewSetMixin):
    queryset = InventoryList.objects.filter(is_deleted=False)
    model = InventoryList  # TODO НУЖНО ЛИ?
    serializer_class = InventoryListSerializer
    create_update_serializer_class = InventoryListCreateUpdateSerializer
    upper_query_filter = 'mol'
    search_filter = 'invent_num'
    lower_url = 'prop'
    lower_name = 'property'
    upper_url = 'mol'
    upper_queryset = Mol.objects.filter(is_deleted=False)
    upper_serializer_class = MolSerializer


class PropertyModelViewSet(ModelViewSetMixin):
    queryset = Property.objects.filter(is_deleted=False)
    model = Property  # TODO НУЖНО ЛИ?
    serializer_class = PropertySerializer
    create_update_serializer_class = PropertyCreateUpdateSerializer
    upper_query_filter = ''
    search_filter = ''
    lower_url = ''
    upper_url = ''
    # upper_queryset = Organization.objects.filter(is_deleted=False)
    # upper_serializer_class = OrganizationSerializer
# ==================================================================================== #


class OrganizationRetrieve(RetrieveAPIView):
    model = Organization
    serializer_class = OrganizationSerializer
    renderer_classes = [TemplateHTMLRenderer]

    def retrieve(self, request, *args, **kwargs):
        queryset = Organization.objects.get(pk=kwargs['pk'])
        return Response({'organizations': [queryset]}, template_name='organization.html')


class OrganizationList(ListAPIView):
    queryset = Organization.objects.filter(is_deleted=False)
    model = Organization
    serializer_class = OrganizationSerializer
    renderer_classes = [TemplateHTMLRenderer]

    def list(self, request, *args, **kwargs):
        if query_name := request.query_params.get('search'):
            queryset = self.get_queryset().filter(name__contains=query_name)  # TODO МБ ПОЛУЧШЕ РЕШЕНИЕ ЕСТЬ
        elif holding_query := request.query_params.get('holding_id'):
            queryset = self.get_queryset().filter(holding__id=holding_query)
        else:
            queryset = self.get_queryset()
        holding_queryset = Holding.objects.all()  # TODO мб придется переделывать,/
        # TODO потому что 2 кверисета в одной вьюшке такое себе,/
        # TODO либо не все поля возвращать

        return Response({'organizations': queryset, 'holdings': holding_queryset,
                         'success_create': bool(request.query_params.get('success_create'))},  # TODO переделать
                        template_name='organization.html')


# class OrganizationCreate(CreateAPIView):
#     model = Organization
#     serializer_class = OrganizationCreateSerializer
#
#     def post(self, request, *args, **kwargs):
#
#         organization = self.create(request, *args, **kwargs)
#
#         if request.META.get('HTTP_REFERER').split('?')[
#             0] == 'http://127.0.0.1:8000/organization/':  # TODO убрать отношение к МЕТА данным
#             return redirect("http://127.0.0.1:8000/organization/?success_create=True")
#         else:
#             return organization

        # def perform_des


class OrganizationDelete(CreateAPIView):
    model = Organization
    serializer_class = OrganizationSerializer

    def post(self, request, *args, **kwargs):
        # TODO Сделать через map как строкой выше
        for i in Organization.objects.filter(pk__in=request.data):
            i.is_deleted = True
            i.save()


class OrganizationUpdate(CreateAPIView):
    model = Organization
    serializer_class = OrganizationSerializer

    def post(self, request, *args, **kwargs):
        for organization_row in request.data:
            obj = Organization.objects.get(pk=organization_row['id'])
            obj.name = organization_row['name']
            obj.address = organization_row['address']  # TODO через сериализатор можно или **

            obj.save()
        return Response(request.data)


class DepartmentRetrieve(RetrieveAPIView):
    model = Department
    serializer_class = DepartmentSerializer
    renderer_classes = [TemplateHTMLRenderer]

    def retrieve(self, request, *args, **kwargs):
        queryset = Department.objects.get(pk=kwargs['pk'])
        return Response({'departments': [queryset]}, template_name='department.html')


class DepartmentList(ListAPIView):
    queryset = Department.objects.all()
    model = Department
    serializer_class = DepartmentSerializer
    renderer_classes = [TemplateHTMLRenderer]

    def list(self, request, *args, **kwargs):
        queryset = Department.objects.all()
        if query_name := request.query_params.get('search'):
            queryset = Department.objects.filter(name__contains=query_name)  # TODO МБ ПОЛУЧШЕ РЕШЕНИЕ ЕСТЬ
        if query_org_id := request.query_params.get('organization_id'):
            queryset = Department.objects.filter(organization__id=query_org_id)
        organization_queryset = Organization.objects.all()  # TODO мб придется переделывать,/
        #  потому что 2 кверисета в одной вьюшке такое себе,/
        #  либо не все поля возвращать

        return Response({'departments': queryset, 'organizations': organization_queryset,
                         'success_create': bool(request.query_params.get('success_create'))},  # TODO переделать
                        template_name='department.html')


@method_decorator(csrf_exempt, name='dispatch')
class DepartmentCreate(CreateAPIView):
    model = Department
    serializer_class = DepartmentCreateSerializer

    def post(self, request, *args, **kwargs):

        department = self.create(request, *args, **kwargs)

        if request.META.get('HTTP_REFERER').split('?')[
            0] == 'http://127.0.0.1:8000/department/':  # TODO убрать отношение к МЕТА данным
            return redirect("http://127.0.0.1:8000/department/?success_create=True")
        else:
            return department


class HoldingRetrieve(RetrieveAPIView):
    model = Holding
    serializer_class = HoldingSerializer
    renderer_classes = [TemplateHTMLRenderer]

    def retrieve(self, request, *args, **kwargs):
        queryset = Holding.objects.get(pk=kwargs['pk'])
        return Response({'holdings': [queryset]}, template_name='holding.html')


class HoldingList(ListAPIView):
    queryset = Holding.objects.all()
    model = Holding
    serializer_class = HoldingSerializer
    renderer_classes = [TemplateHTMLRenderer]

    def list(self, request, *args, **kwargs):
        queryset = Holding.objects.all()
        if query_name := request.query_params.get('search'):
            queryset = Holding.objects.filter(name__contains=query_name)  # TODO МБ ПОЛУЧШЕ РЕШЕНИЕ ЕСТЬ

        # organization_queryset = Organization.objects.all()  # TODO мб придется переделывать,/

        return Response({'holdings': queryset,
                         # 'organizations': organization_queryset,
                         'success_create': bool(request.query_params.get('success_create'))},  # TODO переделать
                        template_name='holding_new.html')


@method_decorator(csrf_exempt, name='dispatch')
class HoldingCreate(CreateAPIView):
    model = Holding
    serializer_class = HoldingCreateSerializer

    def post(self, request, *args, **kwargs):
        print(321321)
        holding = self.create(request, *args, **kwargs)

        # if request.META.get('HTTP_REFERER').split('?')[
        #     0] == 'http://127.0.0.1:8000/holding/':  # TODO убрать отношение к МЕТА данным и изменить так, чтобы работало на сервере
        #     return redirect("http://127.0.0.1:8000/holding/?success_create=True")
        # else:
        return holding


class HoldingUpdate(CreateAPIView):
    model = Holding
    serializer_class = HoldingSerializer

    def post(self, request, *args, **kwargs):
        for holding_row in request.data:
            obj = Holding.objects.get(pk=holding_row['id'])
            obj.name = holding_row['name']
            obj.address = holding_row['address']  # TODO через сериализатор можно или **

            obj.save()
        return Response(request.data)


class Inner(ListAPIView):
    queryset = Department.objects.all()
    model = Department
    serializer_class = DepartmentSerializer
    renderer_classes = [TemplateHTMLRenderer]

    def list(self, request, *args, **kwargs):
        queryset = InventoryList.objects.all()
        if query_name := request.query_params.get('search'):
            queryset = InventoryList.objects.filter(Mol__department__cabinet__contains=query_name)
        # TODO мб придется переделывать,/
        properties = Property.objects.all().order_by('name')
        departments = Department.objects.all()
        organizations = Organization.objects.all()
        #  потому что 2 кверисета в одной вьюшке такое себе,/
        #  либо не все поля возвращать

        return Response({'invent_lists': queryset, 'properties': properties, 'departments': departments,
                         'organizations': organizations,
                         'success_create': bool(request.query_params.get('success_create'))},  # TODO переделать
                        template_name='handler.html')


class InnerUpdate(CreateAPIView):
    model = InventoryList
    serializer_class = OrganizationSerializer

    def post(self, request, *args, **kwargs):
        for inv_row in request.data:
            obj = InventoryList.objects.get(pk=inv_row['id'])
            obj.Mol = Mol.objects.filter(department__id=inv_row['department_id']).first()
            obj.invent_num = inv_row['inv_num']
            obj.property = Property.objects.get(pk=inv_row['property_id'])
            obj.amount = inv_row['amount']
            obj.description = inv_row['description']
            obj.save()

        return Response(request.data)


class PropertyCreate(CreateAPIView):
    queryset = Property.objects.all()
    model = Property
    serializer_class = PropertySerializer
