import json
from abc import abstractmethod
from time import sleep

import django_filters
from django.db import transaction, models
from django.db.models import QuerySet, CharField, ForeignKey
from django.http import JsonResponse, HttpResponse, QueryDict
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from core.serializer import OrganizationSerializer, DepartmentSerializer, \
    DepartmentCreateSerializer, HoldingCreateSerializer, HoldingSerializer, PropertySerializer, \
    OrganizationSerializer, OrganizationCreateUpdateSerializer, DepartmentCreateUpdateSerializer, \
    HoldingCreateUpdateSerializer, MolCreateUpdateSerializer, MolSerializer, InventoryListSerializer, \
    InventoryListCreateUpdateSerializer, PropertyCreateUpdateSerializer, OperationSerializer, \
    OperationCreateUpdateSerializer, MolWithNameSerializer, InventoryListWithNameSerializer
from .filters import OperationFilter, OrgFilter
from .fixture import script
from core.models import Holding, Organization, Department, Mol, Property, InventoryList, Operation
from rest_framework.utils.serializer_helpers import ReturnList


# ModelViewSet
class ModelViewSetMixin(ModelViewSet):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    upper_serializer_class = None
    dep_field = None
    lower_name = None
    upper_queryset = None
    UNEDITABLE_FIELDS = ['is_deleted']


    @property
    @abstractmethod
    def create_update_serializer_class(self):
        pass

    @property
    @abstractmethod
    def model(self):
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
        self.queryset = self.get_queryset().filter(
                pk=kwargs['pk'])  # TODO сделать чтобы вместо filter был get и many = False
        self.lower_url = f'../{self.lower_url}'
        self.upper_url = f'../{self.upper_url}'

        return Response(self.template_dict(request, retrieve=True), template_name='template.html')

    def list(self, request, *args, **kwargs):
        self.queryset = self.filtered_queryset(request, *args, **kwargs)  # Нужен ли здесь *args, **kwargs
        return Response(self.template_dict(request), template_name='template.html')

    def filtered_queryset(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if query_name := request.query_params.get('search'):
            queryset = self.queryset.filter(**{f'{self.search_filter}__contains': query_name})  # TODO
        if upper_query := request.query_params.get(f'{self.upper_query_filter}_id'):
            queryset = self.queryset.filter(**{f'{self.upper_query_filter}__id': upper_query})
        # ModelViewSetMixin.filterset_class = self.filterset_class_render(queryset=queryset)
        return queryset

    def template_dict(self, request, retrieve=False, *args, **kwargs):
        serializer = self.get_serializer(self.queryset, many=True).data if self.queryset else self.empty_queryset(request)
        upper_serializer = self.upper_serializer(many=True)


        return_dict = {
            'btn_fields': {
                'lower_name': self.lower_name or self.search_filter,
                'lower_url': self.lower_url,
                'upper_name': self.upper_query_filter,
                'upper_url': self.upper_url
            },
            'dep_field': self.dep_field,
            'query': serializer,
            'upper_query': upper_serializer.data if upper_serializer is not None else None,
            'model': self.model,  # TODO мб все-таки стоит оставить self.model
            'model_name': self.model.__name__.lower(),  # TODO мб можно избавиться
            # TODO если можно будет достававть имя в шаблоне
            'upper_model': self.upper_model,
            'success_create': bool(request.query_params.get('success_create')),
            'serializer': list(self.get_serializer(self.queryset.first()).data.keys()),  # TODO переделать
            'retrieve': True if retrieve is True else False
        }

        return return_dict

    def empty_queryset(self, request, *args, **kwargs):
        return {x.name: '' for x in self.model._meta._get_fields(reverse=False) if x.name not in self.UNEDITABLE_FIELDS}

    # def filterset_class_render(self, queryset=None):
    #     return MixinFilter(self.model, queryset)

    def upper_model(self):
        if self.upper_queryset is not None:
            return self.upper_queryset.model
        else:
            return None

    def upper_serializer(self, many: bool):
        if self.upper_serializer_class is not None and self.upper_queryset is not None:
            return self.upper_serializer_class(self.upper_queryset, many=many)
        else:
            return None

    def get_serializer_class(self):
        if self.action in ['create', 'update']:  # TODO Реализовать через Meta.list_serializer_class
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
    upper_serializer_class = MolWithNameSerializer

    def template_dict(self, request, *args, **kwargs):
        return_dict = super().template_dict(request, *args, **kwargs)
        return_dict["extra_select"] = [
            "property", ]  # TODO создать класс который через __init__ будет это распределять по словарям
        return_dict["extra_query"] = {"property": Property.objects.filter(is_deleted=False)}
        return_dict["extra_query_keys"] = {"property": PropertySerializer(Property.objects.filter(
            is_deleted=False).first()).data.keys()}  # TODO Чтобы он сам брал ключи из кверисета, но можно было бы переопределить
        return_dict["extra_url"] = {"property": 'prop'}
        return return_dict


class PropertyModelViewSet(ModelViewSetMixin):
    queryset = Property.objects.filter(is_deleted=False)
    model = Property  # TODO НУЖНО ЛИ?
    serializer_class = PropertySerializer
    create_update_serializer_class = PropertyCreateUpdateSerializer
    upper_query_filter = ''
    search_filter = 'name'
    lower_url = ''
    upper_url = ''

    # upper_queryset = Organization.objects.filter(is_deleted=False)
    # upper_serializer_class = OrganizationSerializer

    def filtered_queryset(self, request, *args, **kwargs):
        queryset = super().filtered_queryset(request, *args, **kwargs)
        if query_name := request.query_params.get('inventorylist_id'):
            inv_queryset = InventoryList.objects.get(pk=query_name)
            return Property.objects.filter(id=inv_queryset.property.id)
        else:
            return queryset


class Beta:

    @property
    def model(self):
        return Operation

    type = [{"id": 1, "name": "Закупка"},
            {"id": 2, "name": "Перемещение"},
            {"id": 3, "name": "Списание"},
            ]

    counter = 0

    def __next__(self):
        if self.counter > 2:
            raise StopIteration
        return_ans = self.type[self.counter]
        self.counter += 1
        return return_ans

    def __iter__(self):
        return self


class OperationModelViewSet(ModelViewSetMixin):
    queryset = Operation.objects.filter(is_deleted=False)
    model = Operation  # TODO НУЖНО ЛИ?
    serializer_class = OperationSerializer
    create_update_serializer_class = OperationCreateUpdateSerializer
    upper_query_filter = 'inventory_list'
    search_filter = 'waybill'
    lower_url = 'dep'
    lower_name = ''
    dep_field = ['fromm', 'to']
    upper_url = 'inv'
    upper_queryset = InventoryList.objects.filter(is_deleted=False)
    upper_serializer_class = InventoryListWithNameSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = OrgFilter
    # filterset_fields = ('inventory_list', )

    def filtered_queryset(self, request, *args, **kwargs):
        queryset = super().filtered_queryset(request, *args, **kwargs)
        if query_name := request.query_params.get('inventorylist_id'):
            queryset = queryset.filter(inventory_list__pk=query_name)
        return queryset

    def template_dict(self, request, *args, **kwargs):

        return_dict = super().template_dict(request, *args, **kwargs)
        return_dict["extra_select"] = ["fromm", "to",
                                       "type"]  # TODO создать класс который через __init__ будет это распределять по словарям

        return_dict["extra_query"] = {"fromm": Department.objects.filter(is_deleted=False),
                                      "to": Department.objects.filter(is_deleted=False),
                                      "type": Beta
                                      }

        return_dict["extra_query_keys"] = {
            "fromm": DepartmentSerializer(Department.objects.filter(is_deleted=False).first()).data.keys(),
            "to": DepartmentSerializer(Department.objects.filter(is_deleted=False).first()).data.keys(),
            # TODO Чтобы он сам брал ключи из кверисета, но можно было бы переопределить
            "type": Beta.type[0].keys()}
        return_dict["extra_url"] = {"fromm": 'dep', "to": 'dep'}
        return_dict["pdf_file"] = True
        return_dict["property_in"] = True

        return return_dict

    def create(self, request, *args, **kwargs):
        try:
            file = request.data['pdf_file']
        except KeyError:
            raise ParseError('Request has no resource file attached')
        Operation.objects.create(
            inventory_list=InventoryList.objects.get(pk=request.data['inventory_list']),
            data_time=request.data['data_time'] if request.data['data_time'] not in ['', '""', None, 'None'] else None,
            fromm=Department.objects.get(pk=request.data['fromm']),
            to=Department.objects.get(pk=request.data['to']),
            type=request.data['type'],
            pdf_file=file
        )
        return Response(status=200)

    @action(methods=['POST'], detail=False)
    def file_update(self, request):
        try:
            for id, file in request.data.items():
                if 'undefined' not in file:
                    operation = Operation.objects.get(pk=id)
                    operation.pdf_file = file
                    operation.save()
            return Response(status=200)
        except Exception as e:
            return Response(str(e), status=400)


# ==================================================================================== #

# ==================================================================================== #


class OrganizationRetrieve(RetrieveAPIView):
    model = Organization
    serializer_class = OrganizationSerializer
    renderer_classes = [TemplateHTMLRenderer]

    def retrieve(self, request, *args, **kwargs):
        queryset = Organization.objects.get(pk=kwargs['pk'])
        return Response({'organizations': [queryset]}, template_name='organization.html')


class FileUpload(ModelViewSet):
    serializer_class = OperationSerializer
    model = Operation
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def create(self, request, *args, **kwargs):
        try:
            file = request.data.get('file')
        except KeyError:
            raise ParseError('yaaaaa')
        asi = Operation.objects.get(pk=10)
        asi.pdf_file = file
        asi.save()
        return Response('dsa', status=201)

    def list(self, request, *args, **kwargs):
        return Response(template_name='file_upload.html')


# class OrganizationList(ListAPIView):
#     queryset = Organization.objects.filter(is_deleted=False)
#     model = Organization
#     serializer_class = OrganizationSerializer
#     renderer_classes = [TemplateHTMLRenderer]
#
#     def list(self, request, *args, **kwargs):
#         if query_name := request.query_params.get('search'):
#             queryset = self.get_queryset().filter(name__contains=query_name)  # TODO МБ ПОЛУЧШЕ РЕШЕНИЕ ЕСТЬ
#         elif holding_query := request.query_params.get('holding_id'):
#             queryset = self.get_queryset().filter(holding__id=holding_query)
#         else:
#             queryset = self.get_queryset()
#         holding_queryset = Holding.objects.all()  # TODO мб придется переделывать,/
#         # TODO потому что 2 кверисета в одной вьюшке такое себе,/
#         # TODO либо не все поля возвращать
#
#         return Response({'organizations': queryset, 'holdings': holding_queryset,
#                          'success_create': bool(request.query_params.get('success_create'))},  # TODO переделать
#                         template_name='organization.html')

class OrganizationList(ListAPIView):
    queryset = Operation.objects.filter(is_deleted=False)
    model = Operation  # TODO НУЖНО ЛИ?
    serializer_class = OperationSerializer
    # filter_backends = [DjangoFilterBackend, ]
    # filterset_class = OrgFilter
    # def filtered_queryset(self):

        # def __new__(cls, *args, **kwargs):
    #     foreign_fields = [x.name for x in cls.model._meta._get_fields(reverse=False) if x.__class__ is ForeignKey]
    #     not_foreign_fields = [x.name for x in cls.model._meta._get_fields(reverse=False) if x.__class__ is not ForeignKey]
    #
    #     for foreign_field in foreign_fields:
    #         setattr(cls.filterset_class, foreign_field, django_filters.CharFilter(lookup_expr='icontains', field_name='name'))
    #
    #     cls.filterset_class.Meta.model = cls.model
    #     cls.filterset_class.Meta.fields = dict.fromkeys(not_foreign_fields, ['contains'])
    #     print(cls.filterset_class.Meta.model)
    #
    #     return super().__new__(cls, *args, **kwargs)


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
