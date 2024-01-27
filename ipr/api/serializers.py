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
            "firstname",
            "lastname",
            "patronymic",
            "email",
            "position",
            "superior",
            "subordinates",
        ]


class ReadIprSerializer(serializers.ModelSerializer):
    # tasks = serializers.StringRelatedField(
    #     many=True,
    #     read_only=True
    # )
    author = serializers.StringRelatedField(
        read_only=True
    )
    employee = serializers.StringRelatedField(
        read_only=True
    )

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
            'end_date',
            # 'tasks',
        )


class CreateIprSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField( 
        queryset=User.objects.all(),
    )

    def create(self, validated_data):
        if Ipr.objects.filter(
            title=validated_data.get('title'),
            employee=validated_data.get('employee')
        ).exists():
            raise serializers.ValidationError(
                {'errors': 'Такой ИПР уже существует!'}
            )
        request = self.context.get('request')
        # if validated_data.get('employee') == request.user.subordinates:
        if request.user.superior: # Если руководитель/подчиненный определяется в модели User типом bool
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
            'end_date',
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

    def create(self, validated_data):
        user = self.context['request'].user
        if user.superior:
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
            'reply'
        )
        read_only_fields = ('task',)
