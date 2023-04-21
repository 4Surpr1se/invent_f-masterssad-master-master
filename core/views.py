import json
from abc import abstractmethod

from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.serializer import OrganizationSerializer, OrganizationCreateSerializer, DepartmentSerializer, \
    DepartmentCreateSerializer, HoldingCreateSerializer, HoldingSerializer, PropertySerializer, \
    OrganizationSerializer, OrganizationUpdateSerializer
from .fixture import script
from .models import Holding, Organization, Department, MOL, Property, InventoryList


# ModelViewSet
class ModelViewSetMixin(ModelViewSet):
    # serializer_class = DepartmentSerializer(many=True)
    renderer_classes = [TemplateHTMLRenderer]

    @property
    @abstractmethod
    def upper_queryset(self):
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
        if query_name := request.query_params.get('search'):
            queryset = self.get_queryset().filter(**{f'{self.search_filter}__contains': query_name})  # TODO

        elif upper_query := request.query_params.get(f'{self.upper_query_filter}_id'):
            queryset = self.get_queryset().filter(**{f'{self.upper_query_filter}__id': upper_query})

        else:
            queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)

        btn_fields = {
                'lower_name': self.search_filter,
                'lower_url': 'department',
                'upper_name': self.upper_query_filter,
                'upper_url': 'holding'
            }

        ser_hol = HoldingSerializer(self.upper_queryset, many=True)
        return Response({'btn_fields': btn_fields, 'model': self.model, 'query': serializer.data,
                         'organizations': queryset, 'holdings': ser_hol.data, 'hol_model': Holding,
                         'success_create': bool(request.query_params.get('success_create'))},  # TODO переделать
                        template_name='template.html')

    def create(self, request, *args, **kwargs):

        organization = super().create(request, *args, **kwargs)

        if request.META.get('HTTP_REFERER').split('?')[0] == 'http://127.0.0.1:8000/organization/':  # TODO убрать отношение к МЕТА данным
            return redirect("http://127.0.0.1:8000/organization/?success_create=True")
        else:
            return organization

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        return instance

    def destroy(self, request, *args, **kwargs):
        for instance in request.data:
            self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # def get_serializer(self, *args, **kwargs):
    #     if self.action == 'update': # TODO Реализовать через Meta.list_serializer_class
    #         # kwargs['many'] = True
    #         return OrganizationUpdateSerializer
    #     else:
    #         return super(ModelViewSetMixin, self).get_serializer(*args, **kwargs)
    def get_serializer_class(self):
        if self.action == 'update':
            return OrganizationUpdateSerializer
        else:
            return super().get_serializer()

    def get_object(self):
        if self.action == 'update':
            return [x for x in Organization.objects.filter(id__in=[x['id'] for x in self.request.data])]
        else:
            return super().get_object()

    def get_serializer(self, *args, **kwargs):
        if self.action == 'update':
            serializer_class = self.update_serializer
            self.renderer_classes = None
            kwargs.setdefault('context', self.get_serializer_context())
            kwargs['many'] = True
            return serializer_class(*args, **kwargs)

    # def perform_update(self, serializer):
    #     for s in serializer:
    #         s.save()
    # def update(self, request, *args, **kwargs):
    #     print(self.get_object(), 231321321)
    #     self.get_serializer(Holding, request.data)
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    # super().update()
    # super().get_serializer()

    # def update(self, request, *args, **kwargs):
    #     pass
        # TODO через fetch можно сделать

    # super().get_object()

# class HoldingModelViewSet(ModelViewSetMixin):
#     queryset = Holding.objects.all()
#     model = Holding
#     upper_query_filter = 'holding'
#     search_filter = 'name'
#     upper_queryset = Holding.objects.all()


class Udsa(UpdateAPIView):
    lookup_field = ''
    model = Organization
    queryset = Organization.objects.filter(is_deleted=False)
    # serializer_class = OrganizationafSerializer

    # def get_serializer_class(self):
    #     # if self.action == 'update':
    #     return OrganizationafSerializer
    #     # else:
    #     #     return super().get_serializer()

    # def get_serializer(self, *args, **kwargs):
    #     """
    #     Return the serializer instance that should be used for validating and
    #     deserializing input, and for serializing output.
    #     """
    #     serializer_class = OrganizationafSerializer
    #     kwargs.setdefault('context', self.get_serializer_context())
    #     kwargs['many'] = True
    #     return serializer_class(*args, **kwargs)

    # def get_object(self):
    #     # print(self.request.data)
    #     # if self.action == 'update':
    #     # return
    #     return [x for x in Organization.objects.filter(id__in=[x['id'] for x in self.request.data])]
    #     # else:
    #     #     return super().get_object()

    def perform_update(self, serializer):
        print(serializer)
        serializer.save()


class OrganizationModelViewSet(ModelViewSetMixin):
    queryset = Organization.objects.filter(is_deleted=False)
    model = Organization
    serializer_class = OrganizationSerializer
    update_serializer = OrganizationUpdateSerializer
    upper_query_filter = 'holding'
    search_filter = 'name'
    upper_queryset = Holding.objects.all()


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


class OrganizationCreate(CreateAPIView):
    model = Organization
    serializer_class = OrganizationCreateSerializer

    def post(self, request, *args, **kwargs):

        organization = self.create(request, *args, **kwargs)

        if request.META.get('HTTP_REFERER').split('?')[0] == 'http://127.0.0.1:8000/organization/':  # TODO убрать отношение к МЕТА данным
            return redirect("http://127.0.0.1:8000/organization/?success_create=True")
        else:
            return organization

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

        holding = self.create(request, *args, **kwargs)

        if request.META.get('HTTP_REFERER').split('?')[
            0] == 'http://127.0.0.1:8000/holding/':  # TODO убрать отношение к МЕТА данным и изменить так, чтобы работало на сервере
            return redirect("http://127.0.0.1:8000/holding/?success_create=True")
        else:
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
            queryset = InventoryList.objects.filter(MOL__department__cabinet__contains=query_name)
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
            obj.MOL = MOL.objects.filter(department__id=inv_row['department_id']).first()
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
