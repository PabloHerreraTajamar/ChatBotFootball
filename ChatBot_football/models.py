from django.db import models

# Create your models here.
class Jugador(models.Model):
    name = models.CharField(max_length=10, verbose_name="Jugador")

    def __str__(self):
        return self.name