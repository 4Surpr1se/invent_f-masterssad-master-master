from django import template

register = template.Library()


@register.filter
# Gets the name of the passed in field on the passed in object
def verbose_name(the_object, the_field):
    return the_object._meta.get_field(the_field).verbose_name


@register.filter
def dict_id_pop(the_dict: dict):
    try:
        the_dict.pop('id')
        return the_dict.keys()
    except AttributeError:
        pass

@register.filter
def selection_step(the_list, upper_name: str):
    try:
        return list(the_list).index(upper_name) - 1
    except ValueError as e:
        pass