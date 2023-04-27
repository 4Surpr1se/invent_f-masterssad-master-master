from rest_framework import serializers

from core.models import Organization, Holding, Department, Property


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


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'
