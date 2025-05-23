from django.contrib.auth.models import AbstractUser


# Create your models here.


class User(AbstractUser):
    class Meta:
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
