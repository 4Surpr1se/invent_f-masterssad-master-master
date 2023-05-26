from django import template

from core.models import Mol, InventoryList, Operation
from core.views import Beta

register = template.Library()


@register.filter
# Gets the name of the passed in field on the passed in object
def verbose_name(the_object, the_field):
    # print(f'| {the_object} | {the_field} | {Operation()}')
    # print(the_object.__class__ == Operation().__class__)
    # print(the_object.__class__.__name__, Operation().__class__.__name__)


    if the_object is Mol and the_field == 'name': # TODO Сделать не так уебищно
        return the_object._meta.get_field('FIO').verbose_name
    elif the_object is InventoryList and the_field == 'name':
        return the_object._meta.get_field('invent_num').verbose_name
    elif the_object.__class__ == Operation().__class__ and the_field == 'name':
        return 'Тип Операции'
    elif the_field == 'property':
        return 'Наименование'
    else:
        print(type(the_object), '|', the_field)
        return the_object._meta.get_field(the_field).verbose_name


@register.filter
def dict_id_pop(the_dict: dict):
    try:
        return_list = list(the_dict)
        return_list.remove('id')
        return return_list
    except ValueError:
        return the_dict

@register.filter
def selection_step(the_list, upper_name: str):
    try:
        return list(the_list).index(upper_name) - 1
    except ValueError as e:
        pass

@register.filter
def index(indexable, i):
    return indexable[i]

@register.simple_tag
def dict_get(the_dict, the_key):
    return the_dict.get(the_key)

@register.simple_tag
def get_query_keys(the_serializer):
    return [the_serializer]

@register.filter
def pdf_name(file: str):
    try:
        return file.split('/media/uploads/')[1]
    except Exception:
        return ''

