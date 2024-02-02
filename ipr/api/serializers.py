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


class ReadIprSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True
    )
    employee = serializers.StringRelatedField(
        read_only=True
    )
    start_date = serializers.SerializerMethodField(read_only=True, default=None)
    end_date = serializers.SerializerMethodField(read_only=True, default=None)

    def get_start_date(self, obj):
        if obj.tasks_ipr.all().count() > 0:
            tasks = obj.tasks_ipr.all().order_by('start_date')
            return tasks.first().start_date
        else:
            return obj.start_date
    
    def get_end_date(self, obj):
        if obj.tasks_ipr.all().count() > 0:
            tasks = obj.tasks_ipr.all().order_by('end_date')
            return tasks.last().end_date
        else:
            return obj.end_date

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
            'created_date',
            'end_date',
            'start_date'
        )

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request.user == instance.author:
            allowed_statuses = ['Failed', 'Canceled']
            instance.status = validated_data.get(
                'status',
                instance.status
            )
            if instance.status not in allowed_statuses:
                raise serializers.ValidationError("Недопустимый статус")
            instance.title = validated_data.get(
                'title',
                instance.title
            )
            instance.description = validated_data.get(
                'description',
                instance.description
            )
            instance.start_date = validated_data.get(
                'start_date',
                instance.start_date
            )
            instance.end_date = validated_data.get(
                'end_date',
                instance.end_date
            )
        if request.user in instance.author.subordinates.all():
            allowed_statuses = ['Done', 'In progress']
            instance.status = validated_data.get(
                'status',
                instance.status
            )
            if instance.status not in allowed_statuses:
                raise serializers.ValidationError("Недопустимый статус")
        instance.save()
        return instance


class CreateTaskSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    status = serializers.CharField(default='No status', read_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        if user.superiors:
            task = Task.objects.create(**validated_data)
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
            # 'reply'
        )
        read_only_fields = ('task',)
