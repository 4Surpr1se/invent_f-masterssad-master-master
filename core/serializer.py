import datetime
import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Organization, Holding, Department, Property, Mol, InventoryList, Operation, OperationType


class ListUpdateSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):
        list_ = zip(instance, validated_data)
        print("=======================================")

        for obj in list(list_):
            for k, v in obj[1].items():
                setattr(obj[0], k, v)  # TODO сделать элегантнее
            obj[0].save()
        return instance


# ==================================================================================== #


class HoldingCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holding
        fields = '__all__'
        list_serializer_class = ListUpdateSerializer


class HoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holding
        fields = ['id', 'name', 'address']


# ==================================================================================== #


class OrganizationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        list_serializer_class = ListUpdateSerializer


class OrganizationSerializer(serializers.ModelSerializer):
    holding = HoldingSerializer(read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'address', 'holding']


# ==================================================================================== #


class DepartmentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        list_serializer_class = ListUpdateSerializer


class DepartmentSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'address', 'floor', 'cabinet', 'organization']


# ==================================================================================== #


class MolCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mol
        fields = '__all__'
        list_serializer_class = ListUpdateSerializer


class MolSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Mol
        fields = ['id', 'FIO', 'phone_num', 'post', 'department']


class MolWithNameSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='FIO')

    class Meta:
        model = Mol
        fields = ['id', 'name', 'phone_num', 'post', 'department']


# ==================================================================================== #

class InventoryListCreateUpdateSerializer(serializers.ModelSerializer):
    account_date = serializers.CharField(allow_blank=True)

    class Meta:
        model = InventoryList
        fields = '__all__'
        list_serializer_class = ListUpdateSerializer

    def validate(self, attrs):
        if attrs.get('account_date') in ['', None, 'None']:
            attrs['account_date'] = None
            return super().validate(attrs)
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', attrs.get('account_date')) is None:
            raise ValidationError({'account_date': "дата указана в неверном формате"}, code=400)
        else:
            return super().validate(attrs)

    # @staticmethod # TODO понять почему не работает
    # def validate_account_date(value):
    #     print(2313213123213211)
    #     if value == '':
    #         value = None
    #
    #     return value


class InventoryListSerializer(serializers.ModelSerializer):
    mol = MolWithNameSerializer(read_only=True)
    property = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = InventoryList
        fields = ['id', 'invent_num', 'serial_num', 'amount', 'account_date', 'property', 'description', 'mol']


class InventoryListWithNameSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='invent_num')

    class Meta:
        model = InventoryList
        fields = ['id', 'name', 'serial_num', 'amount', 'account_date', 'property', 'description', 'mol']


# ==================================================================================== #

class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'
        list_serializer_class = ListUpdateSerializer


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'name', 'u_m', 'description']


# ==================================================================================== #

class OperationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'
        list_serializer_class = ListUpdateSerializer


class TypeRepr(serializers.Field):
    def to_representation(self, value: Operation):
        return value.get_type_display()


class OperationSerializer(serializers.ModelSerializer):
    inventory_list = InventoryListWithNameSerializer(read_only=True)
    fromm = DepartmentSerializer(read_only=True)
    to = DepartmentSerializer(read_only=True)

    type = TypeRepr(source='*')

    class Meta:
        model = Operation
        fields = ['id', 'inventory_list', 'data_time', 'waybill', 'fromm', 'to', 'type']


# ==================================================================================== #


class DepartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class OrganizationDeleteSerializer(serializers.ModelSerializer):
    pass


class HoldingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holding
        fields = '__all__'
