from django import template
EMPTY_FIELD_RETURN = 'Отсутствует'

register = template.Library()


@register.simple_tag
def fio_constructor(fio):
    try:
        fio_list = fio.split(' ')
        print(fio_list)
        return {'first_name': fio_list[1],
            'last_name': fio_list[0],
            'father_name': fio_list[2]}
    except IndexError as e:
        return {'first_name': EMPTY_FIELD_RETURN,
                'last_name': EMPTY_FIELD_RETURN,
                'father_name': EMPTY_FIELD_RETURN}
