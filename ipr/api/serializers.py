from django.shortcuts import get_object_or_404
from rest_framework import serializers
from iprs.models import Comment, Ipr, Task
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "photo",
            "username",
            "first_name",
            "last_name",
            "patronymic",
            "email",
            "position",
            "superiors",
            'subordinates'
        ]


class EmployeeSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField(read_only=True)

    def get_fullname(self, obj):
        return f'{obj.last_name} {obj.first_name} {obj.patronymic}'

    class Meta:
        model = User
        fields = (
            'id',
            'photo',
            'fullname',
            'position'
        )


class ReadIprSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True
    )
    employee = EmployeeSerializer(
        read_only=True
    )
    # start_date = serializers.SerializerMethodField(read_only=True)
    # end_date = serializers.SerializerMethodField(read_only=True)

    # def get_start_date(self, obj):
    #     if obj.tasks_ipr.all().count() > 0:
    #         tasks = obj.tasks_ipr.all().order_by('start_date')
    #         return tasks.first().start_date
    #     else:
    #         return obj.start_date
    
    # def get_end_date(self, obj):
    #     if obj.tasks_ipr.all().count() > 0:
    #         tasks = obj.tasks_ipr.all().order_by('end_date')
    #         return tasks.last().end_date
    #     else:
    #         return obj.end_date

    class Meta:
        model = Ipr
        fields = (
            'id',
            'title',
            'employee',
            'author',
            'description',
            'status',
            'created_date',
            'start_date',
            'end_date',
        )


class CreateIprSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.prefetch_related('subordinates').all(),
    )

    def create(self, validated_data):
        employee = validated_data.get('employee')
        if Ipr.objects.filter(
            title=validated_data.get('title'),
            employee=employee
        ).exists():
            raise serializers.ValidationError(
                {'errors': 'Такой ИПР уже существует!'}
            )
        request = self.context.get('request')
        user = request.user
        if not employee in user.subordinates.all():
            raise serializers.ValidationError(
                {'errors': 'ИПР можно создать только для своего подчиненного!'}
            )
        else:
            ipr = Ipr.objects.create(**validated_data)
        return ipr

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request.user == instance.author:
            instance.title = validated_data.get(
                'title',
                instance.title
            )
            instance.description = validated_data.get(
                'description',
                instance.description
            )
            instance.status = validated_data.get(
                'status',
                instance.status
            )
            instance.start_date = validated_data.get(
                'start_date',
                instance.start_date
            )
            instance.end_date = validated_data.get(
                'end_date',
                instance.end_date
            )
        if request.user == instance.employee:
            instance.status = validated_data.get(
                'status',
                instance.status
            )
        instance.save()
        return instance

    def to_representation(self, obj):
        request = self.context.get('request')
        serializer = ReadIprSerializer(
            obj,
            context={'request': request}
        )
        return serializer.data

    class Meta:
        model = Ipr
        fields = (
            'title',
            'employee',
            'description',
            'status',
            # 'start_date',
            # 'end_date',
        )


class TaskSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    ipr = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'status',
            'author',
            'ipr',
            'end_date',
            'created_date',
            'start_date'
        )


class UpdateTaskSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'status',
            'author',
            'status',
            'end_date',
            'created_date',
            'start_date'
        )

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request.user == instance.author:
            instance.title = validated_data.get(
                'title',
                instance.title
            )
            instance.description = validated_data.get(
                'description',
                instance.description
            )
            instance.status = validated_data.get(
                'status',
                instance.status
            )
            instance.start_date = validated_data.get(
                'start_date',
                instance.start_date
            )
        instance.save()
        return instance

    def validate_status(self, value):
        user = self.context['request'].user
        if user.subordinates and value not in ['in_progress', 'done']:
            raise serializers.ValidationError("Невозможное значение")
        return value

    def validate(self, data):
        if self.instance and 'created_date' in data and data['created_date'] != self.instance.created_date:
            raise serializers.ValidationError({"created_date": "Нельзя изменять поле created_date."})

        if self.instance and 'end_date' in data and data['end_date'] != self.instance.end_date:
            raise serializers.ValidationError({"end_date": "Нельзя изменять поле end_date."})

        return data


class CreateTaskSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    status = serializers.CharField(default='no_status', read_only=True)

    def add_ipr_date(self, request, validated_data):
        ipr = get_object_or_404(Ipr, id=request.data.get('ipr'))
        if ipr.start_date == None and ipr.end_date == None:
            ipr.start_date = validated_data.get('start_date')
            ipr.end_date = validated_data.get('end_date')
            ipr.save()
        if ipr.start_date > validated_data.get('start_date'):
            ipr.start_date = validated_data.get('start_date')
            ipr.save()
        if ipr.end_date < validated_data.get('end_date'):
            ipr.end_date = validated_data.get('end_date')
            ipr.save()

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        if user.superiors:
            task = Task.objects.create(**validated_data)
            self.add_ipr_date(request, validated_data)
            return task
        raise serializers.ValidationError("Только руководитель может создавать задачи.")

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'status',
            'author',
            'ipr',
            'start_date',
            'end_date',
            'created_date'
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = (
            'id',
            'task',
            'author',
            'text',
            'created_date',
            'reply'
        )
        read_only_fields = ('task',)
