#!/usr/bin/env python
import pika
import sys
import time
import logging
import os
import traceback

rabbitMqHost = os.environ['RABBIT_MQ_HOST']
rabbitMqQueue = os.environ['RABBIT_MQ_QUEUE']
demoMode = eval(os.environ.get('DEMO_MODE',False))

connection = pika.BlockingConnection

ports = ["21", "20", "12", "16", "8", "7", "24", "25"]

# -------------------------------------------------------------------------------------------------------


def initGpioPorts():
    global ports
    logging.info("Port initialisation...")
    if not demoMode:
        for entry in ports:
            if os.path.isdir("/sys/class/gpio/gpio" + entry) == False:
                logging.info("Init Gpio Port : " + entry)
                f = open("/sys/class/gpio/export", "w")
                f.write(entry)
                f.close()
            else:
                logging.info("Pin:" + entry + " already initialized")
        time.sleep(1)
        logging.info("Setting Port Directions to OUT")
        for entry in ports:
            logging.info("Set Port:" + entry + " as OUTPUT Port")
            f = open("/sys/class/gpio/gpio" + entry + "/direction", "w")
            f.write("out")
            f.close()
    else:
        logging.info("This is the Demo Mode - Port initialisation skipped")
# -------------------------------------------------------------------------------------------------------


def setPort(pin, value):
    logging.info("Set PIN:" + pin + " to value:" + value)
    if not demoMode:
        f = open("/sys/class/gpio/gpio" + pin + "/value", "w")
        if value == "ON":
            f.write("1")
        else:
            f.write("0")
        f.close()
    else:
        logging.info("Write to Pin skipped in Demo Mode")
# -------------------------------------------------------------------------------------------------------


def openConnection():
    global connection
    global rabbitMqHost
    global rabbitMqQueue

    logging.info("Open Connection on Host:" + rabbitMqHost + " Queue:" + rabbitMqQueue)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMqHost))
    channel = connection.channel()
    channel.basic_consume(queue=rabbitMqQueue, on_message_callback=callback)
    logging.info("Waiting for Messages on Queue:" + rabbitMqQueue)
    channel.start_consuming()
# -------------------------------------------------------------------------------------------------------


def closeConnection():
    global connection
    connection.close()
# -------------------------------------------------------------------------------------------------------


def callback(ch, method, properties, body):
    global rabbitMqQueue
    global ports

    ch.basic_ack(delivery_tag=method.delivery_tag)
    logging.debug("Message arrived")

    if body.find("=") != -1:
        pin = body[0:body.find("=")]
        state = body[body.find("=")+1:]
        if state.strip().upper() == "ON" or state.strip().upper() == "OFF":
            try:
                ports.index(pin)
                setPort(pin, state)
            except ValueError:
                logging.error("PIN:" + pin + " not configured...")
        else:
            logging.error("STATE is NOT ON or OFF -> " + state.strip().upper())
    else:
        logging.info("Message on Channel: " + rabbitMqQueue +
                     " has an unexpectedly Format -> expecting PinNumber=ON/OFF")
# -------------------------------------------------------------------------------------------------------


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("---------------------------------------------")
    logging.info('gpioActor Started')
    initGpioPorts()
    openConnection()

    logging.info('Finished')
    closeConnection()
    logging.info("---------------------------------------------")


if __name__ == '__main__':
    try:
        main()
    except:
        logging.info("---------------------------------------------")
        logging.info("-- CRITICAL ERROR OCCURED...")
        logging.info("---------------------------------------------")
        traceback.print_exc(file=sys.stdout)
        time.sleep(5)
        sys.exit(2)
