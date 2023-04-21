from django.db import models
# TODO Добавить миксин под все модели


class Holding(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=255, unique=True)
    address = models.CharField(verbose_name='адрес', max_length=255)

    def __str__(self):
        return self.name


class Organization(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=255)
    # TODO везде verbose_name='Имя' поменять на "Название" или что-то подобное
    address = models.CharField(verbose_name='Адрес', max_length=255)
    holding = models.ForeignKey(Holding, verbose_name="холдинг", on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name='Удален', default=False) # TODO Везде сделать is_deleted олк

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=255)
    address = models.CharField(verbose_name='Адрес', max_length=255)
    floor = models.CharField(verbose_name='Этаж', max_length=255)
    cabinet = models.CharField(verbose_name='Кабинет', max_length=255)
    organization = models.ForeignKey(Organization, verbose_name="организация", on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class MOL(models.Model):
    FIO = models.CharField(verbose_name='ФИО', max_length=255)
    phone_num = models.CharField(verbose_name='Номер телефона', max_length=255)
    department = models.ForeignKey(Department, verbose_name='Отдел', on_delete=models.PROTECT)
    post = models.CharField(verbose_name='Должность', max_length=255)

    def __str__(self):
        return self.FIO


class Property(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=255)
    u_m = models.CharField(verbose_name='Единица измерения', max_length=255)
    description = models.CharField(verbose_name='Описание', max_length=255)

    def __str__(self):
        return self.name


class InventoryList(models.Model):
    invent_num = models.CharField(verbose_name='Ивентарный номер', max_length=255, default='Отсутствует')
    serial_num = models.CharField(verbose_name='Серийный номер', max_length=255)
    amount = models.IntegerField(verbose_name='Количество')  # переделать на другой тайп филд
    account_date = models.DateTimeField(verbose_name='аккаунт_дата', null=True)
    MOL = models.ForeignKey(MOL, verbose_name='МОЛ', on_delete=models.PROTECT)
    property = models.ForeignKey(Property, verbose_name='Имущество', on_delete=models.PROTECT)
    description = models.CharField(verbose_name='Описание', max_length=255, default='')

    def __str__(self):
        return self.invent_num
