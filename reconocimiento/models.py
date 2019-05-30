from django.db import models

# Create your models here.

class Usuarios(models.Model):
	nombre = models.CharField(max_length=200)
	nombreCompleto = models.CharField(max_length=200)
	password = models.CharField(max_length=200)
	habilitado = models.IntegerField(default=1)

class Perfiles(models.Model):
	idUsuario = models.IntegerField()
	ventana = models.IntegerField()
	luz = models.IntegerField()
	tv = models.IntegerField()
	bocinas = models.IntegerField()
	ac = models.IntegerField()
	habilitado = models.IntegerField(default=1)