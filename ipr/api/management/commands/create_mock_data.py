import datetime as dt
from random import choice

from django.core.management.base import BaseCommand

from users.models import User
from iprs.models import Ipr, Task, Comment

NAMES = ('Иван', 'Олег', 'Петр', 'Михаил', 'Максим')
SURNAMES = ('Олегович', 'Кириллович', 'Александрович', 'Павлович')
LAST_NAMES = ('Иванов', 'Петров', 'Сидоров', 'Козлов', 'Майоров')
PASSWORD = 'superhardpassword1'


class Command(BaseCommand):
    help = 'Creates fake data for testing'

    def handle(self, *args, **options):
        superior = self.create_superior()
        self.create_subordinates(superior)
        self.create_iprs(superior)
        self.create_tasks(superior)
        self.create_comments(superior)
        self.stdout.write(self.style.SUCCESS('Тестовые данные созданы'))

    def create_superior(self) -> User:
        user = User.objects.create(
            username='superior',
            first_name='Кирилл',
            last_name='Сидоров',
            patronymic='Иванович',
            position='Team Lead',
        )
        user.set_password(PASSWORD)
        user.save()
        return user

    def create_subordinates(self, superior: User) -> None:
        for i in range(1, 10):
            user = User.objects.create(
                username=f'subordinate{i}',
                first_name=choice(NAMES),
                last_name=choice(LAST_NAMES),
                patronymic=choice(SURNAMES),
                position='Python developer',
            )
            user.superiors.add(superior)
            user.set_password(PASSWORD)
            user.save()
    
    def create_iprs(self, superior: User) -> None:
        for employee in User.objects.filter(superiors=superior).all():
            for i in range(1, 4):
                Ipr.objects.create(
                    title=f'Название ИПР №{i}',
                    employee=employee,
                    author=superior,
                    description=f'Описание ИПР №{i}',
                    status='No status',
                    created_date=dt.datetime.now(),
                )
    
    def create_tasks(self, superior: User) -> None:
        for ipr in Ipr.objects.all():
            for i in range(1, 4):
                Task.objects.create(
                    title=f'Название задачи №{i}',
                    description=f'Описание задачи №{i}',
                    status='No status',
                    author=superior,
                    ipr=ipr,
                    created_date=dt.datetime.now(),
                    start_date=dt.date.today(),
                    end_date=dt.date.today() + dt.timedelta(days=3)
                )
    
    def create_comments(self, superior: User) -> None:
        for task in Task.objects.all():
            comment = Comment.objects.create(
                author=superior,
                task=task,
                text='Комментарий руководителя',
                created_date=dt.datetime.now()
            )
            comment.save()
            Comment.objects.create(
                author=task.ipr.employee,
                task=task,
                text='Комментарий сотрудника в ответ на комментарий руководителя',
                created_date=dt.datetime.now(),
                # reply=comment
            )
