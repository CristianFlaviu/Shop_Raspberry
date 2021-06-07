
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
from imutils.video import VideoStream
import pika
import json
from playsound import playsound
import os
import vlc

p = vlc.MediaPlayer("/home/pi/Desktop/findBarcode/ceva.mp3")
p.play()


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="roedeer-01.rmq.cloudamqp.com",
                              virtual_host="tkfdwjro",
                              credentials=pika.credentials.PlainCredentials(
                                  "tkfdwjro", "calbiuNFyl_9kOwHQH6eBS5omW5Wb_zV")
                              ))
channel = connection.channel()

channel.queue_declare(queue='barcode_queue')

print("[INFO] starting video stream...")
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

userWebsocket = None

while True:

    frame = vs.read()
    frame = imutils.resize(frame, width=400)

    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type

        if barcodeType == 'QRCODE':
            decodedBarcode = json.loads(barcodeData)
            print(decodedBarcode)
            print(decodedBarcode['name'])


            userWebsocket = decodedBarcode['id']

        else:
            print(datetime.datetime.now(), barcodeData, barcodeType)
            if (userWebsocket is None):
                print("please login before")
            else:
                sentObj = {"socket": userWebsocket, "barcode": barcodeData}
                jsonSentObj = json.dumps(sentObj)
                channel.basic_publish(exchange='', routing_key='barcode_queue', body=jsonSentObj)
        time.sleep(5)

vs.stop()
