from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    photo = models.ImageField(
        upload_to="users/photos", blank=True, null=True, verbose_name="Фото"
    )
    patronymic = models.CharField(max_length=50, verbose_name="Отчество")
    position = models.CharField(max_length=150, verbose_name="Должность")
    superior = models.ManyToManyField(
        'self',
        verbose_name='Руководители'
    )
    subordinates = models.ManyToManyField(
        'self',
        verbose_name='Подчиненные'
    )

    def __str__(self):
        return self.get_full_name()
