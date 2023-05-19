from django.db import models

from core.model_validators import validate_account_date


# TODO Добавить миксин под все модели


class Holding(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=255)
    address = models.CharField(verbose_name='адрес', max_length=255)
    is_deleted = models.BooleanField(verbose_name='Удален', default=False)

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
    is_deleted = models.BooleanField(verbose_name='Удален', default=False)

    def __str__(self):
        return self.name


class Mol(models.Model):
    FIO = models.CharField(verbose_name='ФИО', max_length=255)
    phone_num = models.CharField(verbose_name='Номер телефона', max_length=255)
    department = models.ForeignKey(Department, verbose_name='Отдел', on_delete=models.PROTECT)
    post = models.CharField(verbose_name='Должность', max_length=255)
    is_deleted = models.BooleanField(verbose_name='Удален', default=False)

    def __str__(self):
        return self.FIO


class Property(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=255)
    u_m = models.CharField(verbose_name='Единица измерения', max_length=255)
    description = models.CharField(verbose_name='Описание', max_length=255)
    is_deleted = models.BooleanField(verbose_name='Удален', default=False)

    def __str__(self):
        return self.name


class InventoryList(models.Model):
    invent_num = models.CharField(verbose_name='Ивентарный номер', max_length=255, default='Отсутствует')
    serial_num = models.CharField(verbose_name='Серийный номер', max_length=255)
    amount = models.IntegerField(verbose_name='Количество')  # переделать на другой тайп филд
    account_date = models.DateTimeField(verbose_name='аккаунт_дата', null=True, blank=True)
    mol = models.ForeignKey(Mol, verbose_name='МОЛ', on_delete=models.PROTECT)
    property = models.ForeignKey(Property, verbose_name='Имущество', on_delete=models.PROTECT)
    description = models.CharField(verbose_name='Описание', max_length=255, default='')
    is_deleted = models.BooleanField(verbose_name='Удален', default=False)

    def __str__(self):
        return self.invent_num


class OperationType(models.IntegerChoices):
    purchase = 1, "Закупка"
    displacement = 2, "Перемещение"
    write_off = 3, "Списание"


class Operation(models.Model):
    inventory_list = models.ForeignKey(InventoryList, verbose_name='Инвертарная запись', on_delete=models.PROTECT)
    data_time = models.DateTimeField(verbose_name='аккаунт_дата', null=True)
    fromm = models.ForeignKey(Department, verbose_name='Из отдела', related_name='fromm', on_delete=models.PROTECT)
    to = models.ForeignKey(Department, verbose_name='В отдел', on_delete=models.PROTECT)
    type = models.PositiveSmallIntegerField(verbose_name='Тип операции', choices=OperationType.choices,
                                            default=OperationType.displacement)
    pdf_file = models.FileField(verbose_name='Накладная', upload_to="uploads/", default='', blank=True, null=True)  # uploads/%Y/%m/%d/ = MEDIA_ROOT/uploads/2015/01/30
    is_deleted = models.BooleanField(verbose_name='Удален', default=False)
