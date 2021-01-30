#!/bin/bash

export RABBIT_MQ_HOST=192.168.2.52
export RABBIT_MQ_QUEUE=hc-gpio-actor

export DEMO_MODE=True

python gpioActor.py

