#!/bin/bash

export RABBIT_MQ_HOST=devPi
export RABBIT_MQ_QUEUE=hc-gpio-actor

export DEMO_MODE=True

python gpioActor.py

