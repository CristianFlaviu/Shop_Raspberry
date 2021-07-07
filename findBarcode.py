import cv2
from pyzbar import pyzbar
import datetime
import imutils
import time
from imutils.video import VideoStream
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="roedeer-01.rmq.cloudamqp.com",
                              virtual_host="tkfdwjro",
                              credentials=pika.credentials.PlainCredentials(
                                  "tkfdwjro", "calbiuNFyl_9kOwHQH6eBS5omW5Wb_zV"),
                              heartbeat=0
                              ))
channel = connection.channel()
channel.queue_declare(queue='barcode_queue')

print("[INFO] Connection started ...")

vs = VideoStream(usePiCamera=True).start()
print("[INFO] Starting video stream...")

time.sleep(2.0)

previousBarcodeRead = None
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
            print("[INFO]", datetime.datetime.now(), "- user identified -", decodedBarcode['id'])
            userWebsocket = decodedBarcode['id']
            time.sleep(1.5)


        else:

            if userWebsocket is None:
                print("please login before")

            elif previousBarcodeRead is None:
                previousBarcodeRead = barcodeData

            elif previousBarcodeRead != barcodeData:
                previousBarcodeRead = barcodeData

            elif previousBarcodeRead == barcodeData:
                sentObj = {"socket": userWebsocket, "barcode": barcodeData}
                jsonSentObj = json.dumps(sentObj)
                channel.basic_publish(exchange='', routing_key='barcode_queue', body=jsonSentObj)
                print("[INFO]", datetime.datetime.now(), "- barcode identified -", "type:", barcodeType, "Value:",
                      barcodeData)
                print("[INFO] Message sent to", userWebsocket)

                time.sleep(4)

    cv2.imshow("barcode ", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
vs.stop()
# p = vlc.MediaPlayer("/home/pi/Desktop/findBarcode/ceva.mp3")
# p.play()
