
import pika
import sys
from threading import Thread
import threading
import time
import logging
import os
import piRelay

rabbitMqHost = os.environ['RABBIT_MQ_HOST']
rabbitMqQueue = os.environ['RABBIT_MQ_QUEUE']
demoMode = eval(os.environ.get('DEMO_MODE', False))

connection = pika.BlockingConnection

relaisHats = {piRelay.Relay("RELAY1"),
              piRelay.Relay("RELAY2"),
              piRelay.Relay("RELAY3"),
              piRelay.Relay("RELAY4")}


# -------------------------------------------------------------------------------------------------------

def openConnection():
    global connection
    global rabbitMqHost
    global rabbitMqQueue

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMqHost))
    channel = connection.channel()
    channel.basic_consume(queue=rabbitMqQueue,on_message_callback=callback)
    logging.info("Waiting for Messages on Queue:" + rabbitMqQueue)
    channel.start_consuming()

# -------------------------------------------------------------------------------------------------------


def closeConnection():
    global connection
    connection.close


# -------------------------------------------------------------------------------------------------------

def callback(ch, method, properties, body):
    global rabbitMqQueue
    global relaisHats
    ch.basic_ack(delivery_tag=method.delivery_tag)
    if body.find("=") != -1:
        relaisIndex = body[0:body.find("=")]
        logging.debug("Message arrived")
        state = body[body.find("=") + 1:]
        if state.strip().upper() == "ON":
            try:
                relaisHats[relaisIndex].on()
                logging.info("Switch Relais:" + relaisIndex + " to ON")
            except ValueError:
                logging.error("Error while setting State of Ralais:" + relaisIndex + " to ON")
        elif state.strip().upper() == "OFF":
            try:
                relaisHats[relaisIndex].on()
                logging.info("Switch Relais:" + relaisIndex + " to OFF")
            except ValueError:
                logging.error("Error while setting State of Ralais:" + relaisIndex + " to OFF")
        else:
            logging.error("STATE is NOT ON or OFF -> " + state.strip().upper())
    else:
        logging.info("Message on Channel: " + rabbitMqQueue +
                     " has an unexpectedly Format -> expecting relaisNumber=ON/OFF")


# -------------------------------------------------------------------------------------------------------


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("---------------------------------------------")
    logging.info('gpioActor Started')
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
        time.sleep(5)
        sys.exit(2)
