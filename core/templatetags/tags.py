from django import template

register = template.Library()


@register.filter
# Gets the name of the passed in field on the passed in object
def verbose_name(the_object, the_field):
    return the_object._meta.get_field(the_field).verbose_name


@register.filter
def dict_id_pop(the_dict: dict):
    the_dict.pop('id')
    return the_dict.keys()
