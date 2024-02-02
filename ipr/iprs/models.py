from django.db import models

from users.models import User


class Ipr(models.Model):
    NOT_STARTED = 'Not started'
    IN_PROGRESS = 'In progress'
    DONE = 'Done'
    FAILED = 'Failed'
    CANCELED = 'Canceled'
    NO_STATUS = 'No status'
    STATUS_CHOICES = (
        (NOT_STARTED, 'Не начат'),
        (IN_PROGRESS, 'В работе'),
        (DONE, 'Выполнен'),
        (FAILED, 'Не выполнен'),
        (CANCELED, 'Отменен'),
        (NO_STATUS, 'Отсутствует'),
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название ИПР',
    )
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ipr_employee',
        verbose_name='Сотрудник'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ipr_author',
        verbose_name='Автор ИПР'
    )
    description = models.TextField(
        max_length=200,
        verbose_name='Описание ИПР',
    )
    status = models.CharField(
        max_length=11,
        choices=STATUS_CHOICES,
        default=NO_STATUS,
        verbose_name='Статус ИПР'
    )
    created_date = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        verbose_name='Дата создания ИПР'
    )
    start_date = models.DateField(
        verbose_name='Дата начала ИПР',
        null=True
    )
    end_date = models.DateField(
        verbose_name='Дата завершения ИПР',
        null=True
    )

    class Meta:
        verbose_name = 'ИПР'
        verbose_name_plural = 'ИПР'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'employee'],
                name='unique_title_employee_iprs'
            )
        ]

    def __str__(self):
        return self.title


class Task(models.Model):
    """Модель задач"""
    STATUS_CHOICE = [
        ('Failed', 'Просрочен'),
        ('No status', 'Без статуса'),
        ('In progress', 'В работе'),
        ('Done', 'Выполнен'),
        ('Canceled', 'Отменен'),
    ]
    title = models.CharField(
        max_length=200,
        verbose_name="Название"
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default='No status',
        verbose_name='Статус'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='author_tasks'
    )
    ipr = models.ForeignKey(
        Ipr,
        on_delete=models.CASCADE,
        verbose_name='ИПР',
        related_name='tasks_ipr'
    )
    created_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    start_date = models.DateField(
        verbose_name='Плановое время начала'
    )
    end_date = models.DateField(
        verbose_name='Дата завершения'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ('-author',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Модель комментариев"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'
        ordering = ('id',)

    def __str__(self):
        return self.text
