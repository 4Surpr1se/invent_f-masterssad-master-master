from rest_framework import serializers

from core.models import Organization, Holding, Department, Property


# class OrganizationListSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Organization
#         fields = '__all__'
#
#     def update(self, instance, validated_data):
#         print(instance)


# serializers.ListSerializer
class OrganizationListUpdateSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):
        # print(instance, '\n', validated_data)
        list_ = zip(instance, validated_data)
        # # print(list(list_))
        # print(list(list_)[0])
        # print(list(list_)[0])
        # print(list(list_)[0])

        for obj in list(list_):
            obj[0].name = obj[1]['name']
            obj[0].address = obj[1]['address']
            obj[0].holding = obj[1]['holding']
            obj[0].save()
        return instance


class OrganizationUpdateSerializer(serializers.ModelSerializer):

    # @classmethod
    # def many_init(cls, *args, **kwargs):
    #     # Instantiate the child serializer.
    #     kwargs['child'] = cls()
    #     # Instantiate the parent list serializer.
    #     print(args, kwargs)
    #     return OrganizationUpdateSerializer(*args, **kwargs)

    class Meta:
        model = Organization
        fields = '__all__'
        list_serializer_class = OrganizationListUpdateSerializer


class OrganizationSerializer(serializers.ModelSerializer):
    holding = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = Organization
        fields = ['id', 'name', 'address', 'holding']


class OrganizationCreateSerializer(serializers.ModelSerializer):
    holding = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = Organization
        fields = ['id', 'name', 'address', 'holding']

    def create(self, validated_data):

        validated_data['holding'] = Holding.objects.get(name=validated_data.get("holding"))  # TODO переделать,
        # TODO чтобы искал по id, а не name
        organization = Organization.objects.create(**validated_data)
        return organization

    # def update(self, instance, validated_data):
    #     super(OrganizationCreateSerializer, self).update()


class OrganizationDeleteSerializer(serializers.ModelSerializer):
    # super().update()
    pass


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class DepartmentCreateSerializer(serializers.ModelSerializer):
    organization = serializers.CharField(max_length=255)

    class Meta:
        model = Department
        fields = '__all__'

    def create(self, validated_data):
        validated_data['organization'] = Organization.objects.get(name=validated_data.get("organization"))
        department = Department.objects.create(**validated_data)
        return department


class HoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holding
        fields = '__all__'


class HoldingCreateSerializer(serializers.ModelSerializer):
    # holding = serializers.CharField(max_length=255)

    class Meta:
        model = Holding
        fields = '__all__'


class PropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = '__all__'

    # def create(self, validated_data):
    #     validated_data['organization'] = Organization.objects.get(name=validated_data.get("organization"))
    #     department = Department.objects.create(**validated_data)
    #     return department

    # def create(self, validated_data):
    #     holding = Holding.objects.get(name=validated_data.get('holding'))

