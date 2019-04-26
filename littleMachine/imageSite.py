#!/usr/bin/python3

from bottle import *

import serial

ser = serial.Serial("/dev/ttyUSB0", 9600)
ser.flushInput()

TEMPLATE_PATH.append('./')
root = os.path.abspath('./')


@route('/')
def index():
    return 'Hello there General Kenobi!'


@route('/getscreenshot')
def gss():
    return static_file('screenshot.jpg', root=root)


@route('/sendcolor')
def regions():
    r, g, b = request.query.r, request.query.g, request.query.b
    #r = int(r.encode('ascii'))
    #g = int(g.encode('ascii'))
    #b = int(b.encode('ascii'))
    #colorWipe(strip, Color(r, g, b))
    ser.write(bytes("{0},{1},{2}\n".format(r, g, b), 'utf-8'))
    return static_file('screenshot.jpg', root=root)

run(host='0.0.0.0', port=8001, debug=True)
