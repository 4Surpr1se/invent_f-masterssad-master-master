from rest_framework import serializers

from core.models import Organization, Holding, Department, Property, Mol, InventoryList


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

    class Meta:
        model = InventoryList
        fields = '__all__'
        list_serializer_class = ListUpdateSerializer


class InventoryListSerializer(serializers.ModelSerializer):
    mol = MolWithNameSerializer(read_only=True)
    property = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = InventoryList
        fields = ['id', 'invent_num', 'serial_num', 'amount', 'account_date', 'property', 'description', 'mol']


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

