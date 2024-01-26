from django.core.management.base import BaseCommand, CommandError
from users.models import User


class Command(BaseCommand):
    help = "Создаём в БД 10 сотрудников"

    def handle(self, *args, **options):
        try:
            for i in range(1, 10):
                User.objects.create(
                    username="User" + f"{i}",
                    first_name="Иван" + f"{i}",
                    last_name="Иванов",
                    patronymic="Иванович",
                    position="инженер",
                )
        except Exception:
            raise CommandError("Ошибка создания пользователей")

        self.stdout.write(self.style.SUCCESS("Пользователи созданы"))
