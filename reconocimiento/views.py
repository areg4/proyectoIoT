from django.shortcuts import render
from django.http import HttpResponse
import paho.mqtt.publish as publish
from reconocimiento.models import Perfiles
from reconocimiento.models import Usuarios
import cv2 as cv
import numpy as np
import os
from finalIoT.settings import BASE_DIR
import base64
from PIL import Image
from io import BytesIO

# Create your views here.
def index(request):
	publish.single("uaq/luz", 0, hostname="broker.hivemq.com")
	return render(request, 'index.html')

confThreshold = 0.85
nmsThreshold = 0.9
inpWhidth = 320
inpHeight = 320

classesFile = os.path.join(BASE_DIR, 'static/yolo/obj.names')
classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

modelConfiguration = os.path.join(BASE_DIR, 'static/yolo/yolov3-obj.cfg')
modelWeights = os.path.join(BASE_DIR, 'static/yolo/yolov3-caras.weights')

net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
# net.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

def getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

def postprocess(frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    classIds = []
    confidences = []
    boxes = []
    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            # print(repr(confidence))
            if (confidence >= confThreshold and confidence <= 1):
                # print("si : "+ repr(confidence))
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        # print(str(confidences[i]))
        return drawPred(classIds[i], confidences[i], left, top, left + width, top + height, frame)

def drawPred(classId, conf, left, top, right, bottom, img):
    # Draw a bounding box.
    # cv.rectangle(img, (left, top), (right, bottom), (0, 0, 255))
    # print(conf)
    label = '%.2f' % conf

    # Get the label for the class name and its confidence
    if classes:
        assert(classId < len(classes))
        label = '%s' % (classes[classId])

    # print(label)
    #Display the label at the top of the bounding box
    labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, labelSize[1])
    return label
    # print(label)
    # cv.putText(img, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))

def readb64(uri):
	sbuf = BytesIO()
	encoded_data = uri.split(',')[1]
	sbuf.write(base64.b64decode(encoded_data))
	pimg = Image.open(sbuf)
	return cv.cvtColor(np.array(pimg), cv.COLOR_RGB2BGR)

def perfil(request):
	b64 = request.POST['base']
	img = readb64(b64)
	# cv.imshow('img', img)
	# cv.waitKey(0)
	# cv.destroyAllWindows()
	blob = cv.dnn.blobFromImage(img, 1/255, (inpWhidth, inpHeight), [0,0,0], 1, crop=False)
	net.setInput(blob)
	outs = net.forward(getOutputsNames(net))
	l = postprocess(img, outs)
	# print(type(l))
	if l is not None:
		nombre = l
		print(l)
		idUsuario = Usuarios.objects.filter(nombre=nombre).values('id')
		caracteristicas = Perfiles.objects.filter(id=idUsuario)

		for caracteristica in caracteristicas:
			st = "Ventana: %s \n motor: %s \n luz: %s \n tv: %s \n bocinas: %s \n ac: %s" % (caracteristica.ventana, caracteristica.ventana, caracteristica.luz, caracteristica.tv, caracteristica.bocinas, caracteristica.ac)
			print(st)
			publish.single("uaq/ventana", caracteristica.ventana, hostname="broker.hivemq.com")
			publish.single("uaq/motor", caracteristica.ventana, hostname="broker.hivemq.com")
			# print(caracteristica.ventana)
			publish.single("uaq/luz", caracteristica.luz, hostname="broker.hivemq.com")
			# print(caracteristica.luz)
			publish.single("uaq/tv", caracteristica.tv, hostname="broker.hivemq.com")
			# print(caracteristica.tv)
			publish.single("uaq/bocinas", caracteristica.bocinas, hostname="broker.hivemq.com")
			# print(caracteristica.bocinas)
			publish.single("uaq/ac", caracteristica.ac, hostname="broker.hivemq.com")
			# print(caracteristica.ac)
	return HttpResponse(l)
	# return HttpResponse("Kiubo")
