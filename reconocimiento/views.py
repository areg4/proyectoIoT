from django.shortcuts import render
from django.http import HttpResponse
import paho.mqtt.publish as publish
from reconocimiento.models import Perfiles
from reconocimiento.models import Usuarios

# Create your views here.
def index(request):
	#publish.single("uaq/luz", 0, hostname="broker.hivemq.com")
	#return HttpResponse('Aquí va el login')
	nombre = "Gerardo"
	idUsuario = Usuarios.objects.filter(nombre=nombre).values('id')
	caracteristicas = Perfiles.objects.filter(id=idUsuario)
	for caracteristica in caracteristicas:
		print(caracteristica.id)
		publish.single("uaq/ventana", caracteristica.ventana, hostname="broker.hivemq.com")
		print(caracteristica.ventana)
		publish.single("uaq/luz", caracteristica.luz, hostname="broker.hivemq.com")
		print(caracteristica.luz)
		publish.single("uaq/tv", caracteristica.tv, hostname="broker.hivemq.com")
		print(caracteristica.tv)
		publish.single("uaq/bocinas", caracteristica.bocinas, hostname="broker.hivemq.com")
		print(caracteristica.bocinas)
		publish.single("uaq/ac", caracteristica.ac, hostname="broker.hivemq.com")
		print(caracteristica.ac)
		msg = "Listo"
	#print(caracteristicas)
	return render(request, 'index.html', {'msg': msg})

def perfil(request):
	return None