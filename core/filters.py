import django_filters
from django.db.models import ForeignKey
from django_filters.rest_framework import backends, FilterSet

from core.models import Organization, Operation


# class MixinFilter(FilterSet):
#     # def __init__(self, model, data=None, queryset=None, *, request=None, prefix=None):
#     #     self.foreign_fields = [x.name for x in model._meta._get_fields(reverse=False) if x.__class__ is ForeignKey]
#     #     self.not_foreign_fields = [x.name for x in model._meta._get_fields(reverse=False) if x.__class__ is not ForeignKey]
#     #
#     #     for foreign_field in self.foreign_fields:
#     #         setattr(MixinFilter, foreign_field, django_filters.CharFilter(lookup_expr='icontains', field_name='name'))
#     #
#     #     MixinFilter.Meta.model = model
#     #     MixinFilter.Meta.fields = dict.fromkeys(self.not_foreign_fields, ['contains'])
#     #     print(dir(MixinFilter), '\n', dir(MixinFilter.Meta), '\n', (MixinFilter.Meta.model))
#     #     super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
#
#     class Meta:
#         pass
#
#
# class own_backend(django_filters.rest_framework.backends.DjangoFilterBackend):
#     def get_filterset_class(self, view, queryset=None):
#         """
#         Return the `FilterSet` class used to filter the queryset.
#         """
#         model = getattr(view, "model", None)
#         filterset_class = getattr(view, "filterset_class", None)
#         self.foreign_fields = [x.name for x in model._meta._get_fields(reverse=False) if x.__class__ is ForeignKey]
#         self.not_foreign_fields = [x.name for x in model._meta._get_fields(reverse=False) if
#                                    x.__class__ is not ForeignKey]
#
#         for foreign_field in self.foreign_fields:
#             setattr(filterset_class, foreign_field, django_filters.CharFilter(lookup_expr='icontains', field_name='name'))
#
#         filterset_class.Meta.model = model
#         filterset_class.Meta.fields = dict.fromkeys(self.not_foreign_fields, ['contains'])
#         # print(dir(MixinFilter), '\n', dir(MixinFilter.Meta), '\n', (MixinFilter.Meta.model))
#
#         filterset_fields = getattr(view, "filterset_fields", None)
#
#         if filterset_class:
#             filterset_model = filterset_class._meta.model
#
#             # FilterSets do not need to specify a Meta class
#             if filterset_model and queryset is not None:
#                 assert issubclass(
#                     queryset.model, filterset_model
#                 ), "FilterSet model %s does not match queryset model %s" % (
#                     filterset_model,
#                     queryset.model,
#                 )
#
#             return filterset_class
#
#         if filterset_fields and queryset is not None:
#             MetaBase = getattr(self.filterset_base, "Meta", object)
#
#             class AutoFilterSet(self.filterset_base):
#                 class Meta(MetaBase):
#                     model = queryset.model
#                     fields = filterset_fields
#
#             return AutoFilterSet
# #
#         return None
#     # def get_filterset_kwargs(self, request, queryset, view):
#     #     return_kwargs = super().get_filterset_kwargs(request, queryset, view)
#     #     return_kwargs['model'] = queryset.model
#     #     return return_kwargs
#     #
#     # def filter_queryset(self, request, queryset, view):
#     #     a = super().filter_queryset(request, queryset, view)
#     #     print(a)
#     #     return a
#
#
# #
# #
# # class MixinFilter(FilterSet):
# #     class Meta:
# #         pass
#
#
# # def rendererer(model):
# #     pass
#
#
# # foreign_fields = [x.name for x in model._meta._get_fields(reverse=False) if x.__class__ is ForeignKey]
# # not_foreign_fields = [x.name for x in model._meta._get_fields(reverse=False) if x.__class__ is not ForeignKey]
# #
# # for foreign_field in foreign_fields:
# #     setattr(MixinFilter, foreign_field, django_filters.CharFilter(lookup_expr='icontains', field_name='name'))
# #
# # MixinFilter.Meta.model = model
# # MixinFilter.Meta.fields = dict.fromkeys(not_foreign_fields, ['contains'])
# # print(MixinFilter.Meta.fields)
# # return MixinFilter
#
#
# class MDSADSA(django_filters.FilterSet):
#     holding = django_filters.CharFilter(lookup_expr='icontains', field_name='name')
#
#     class Meta:
#         model = Organization
#         fields = {'name': ['contains']}
#
#
#

# class MixinFilter(FilterSet):
#     asd = django_filters.CharFilter(lookup_expr='icontains', field_name='name')
#     class Meta:
#         model = Organization
#         fields = {'name': ['contains']}
#
#     def filter_queryset(self, queryset):
#         a = super().filter_queryset(queryset)
#         return a

# # filterset_class = getattr(view, "filterset_class", None)
# MixinFilter.foreign_fields = [x.name for x in MixinFilter._meta.model._meta._get_fields(reverse=False) if x.__class__ is ForeignKey]
# MixinFilter.not_foreign_fields = [x.name for x in MixinFilter._meta.model._meta._get_fields(reverse=False) if
#                            x.__class__ is not ForeignKey]
#
# for foreign_field in MixinFilter.foreign_fields:
#     setattr(MixinFilter, foreign_field, django_filters.CharFilter(lookup_expr='icontains', field_name='name'))
#
# MixinFilter.Meta.model = MixinFilter._meta.model
# MixinFilter.Meta.fields = dict.fromkeys(MixinFilter.not_foreign_fields, ['contains'])


class OperationFilter(FilterSet):
    inventory_list = django_filters.CharFilter(lookup_expr='icontains', field_name='id')


class OrgFilter(django_filters.rest_framework.FilterSet):
    inv_list = django_filters.CharFilter(lookup_expr='exact', field_name='inventory_list_id')
