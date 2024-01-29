# Generated by Django 4.2 on 2024-01-26 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iprs', '0002_remove_task_ipr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('failed', 'Просрочен'), ('no_status', 'Без статуса'), ('not_started', 'Не начат'), ('in_progress', 'В работе'), ('done', 'Выполнен'), ('canceled', 'Отменен')], default='no_status', max_length=20, verbose_name='Статус'),
        ),
    ]
