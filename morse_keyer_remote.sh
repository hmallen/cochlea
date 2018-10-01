#!/bin/bash

echo "Starting."
PIGPIO_ADDR=192.168.1.198 python morse_keyer.py &&
echo "Done."
