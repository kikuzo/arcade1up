#!/usr/bin/python
#-*-coding: utf-8-*-

import RPi.GPIO as GPIO
import time
import requests, json
import urlparse

"""
try:
    # Python 3
    from http.server import BaseHTTPRequestHandler
    from http.server import HTTPServer
    from socketserver import ThreadingMixIn
except ImportError:
"""
# Python 2
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

# webサーバパート
class GreetingHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        # query = parsed_path.query
        # print("クエリ文字列は %s" % query)
        print("PATHは %s" % parsed_path.path)
        if parsed_path.path == "/clear_LED" :
            GPIO.output(PIN_LED_RESPONSED, GPIO.HIGH)
            GPIO.output(PIN_LED_ON, GPIO.HIGH)
        elif parsed_path.path == "/turnon_LED" :
            GPIO.output(PIN_LED_RESPONSED, GPIO.LOW)
            GPIO.output(PIN_LED_ON, GPIO.LOW)
        elif parsed_path.path == "/setBreath" :
            GPIO.output(PIN_LED_RESPONSED, GPIO.HIGH)
            GPIO.output(PIN_LED_ON, GPIO.LOW)
        elif parsed_path.path == "/setBrink" :
            GPIO.output(PIN_LED_RESPONSED, GPIO.LOW)
            GPIO.output(PIN_LED_ON, GPIO.HIGH)


        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()

        self.wfile.write(b'OK.\r\n')


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """マルチスレッド化した HTTPServer"""
    pass


PIN_FIRE = 14
PIN_EMERGENCY = 18
PIN_LED_ON = 23
PIN_LED_RESPONSED =24
PIN_TESTBUTTON = 25

# times-s_kikuchi
#WEB_HOOK_URL = "https://hooks.slack.com/services/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"
# archade1up
WEB_HOOK_URL = "https://hooks.slack.com/services/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"

LOW = 0
HIGH = 1
repeat_count = 0
last_status = LOW

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_FIRE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_EMERGENCY, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_LED_ON, GPIO.OUT)
GPIO.setup(PIN_LED_RESPONSED, GPIO.OUT)
GPIO.setup(PIN_TESTBUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def switch_callback(self):
    time.sleep(0.05)
    #if GPIO.input(PIN_EMERGENCY) != GPIO.HIGH:
    #    return
    print("エマージェンシーボタン押下")
    GPIO.output(PIN_LED_ON, GPIO.HIGH)
    GPIO.output(PIN_LED_RESPONSED, GPIO.LOW)
    requests.post(WEB_HOOK_URL, data = json.dumps({
        'text': u'エマージェンシーボタンが押されました。\n \
        応答を返す場合には <http://172.31.27.241:8001/setBreath |応答 > をクリックしてください。\n \
        エマージェンシー状態をクリアする場合は <http://172.31.27.241:8001/clear_LED |クリア > をクリックしてください。',
        'username': u'arcade1up_watcherbot',
        'icon_emoji': u':smile_cat:',
        'link_names': 1,
    }))
    #if GPIO.input(PIN_TESTBUTTON) == GPIO.LOW:
    #    print("テストボタン押下")
    #    GPIO.output(PIN_LED_ON, GPIO.HIGH)
    #    #GPIO.output(PIN_LED_RESPONSED, GPIO.LOW)
    return

def power_status_check(repeat_count, last_status):
    if repeat_count == 10:
        if last_status == LOW:
            requests.post(WEB_HOOK_URL, data = json.dumps({
            'text': u'電源が落とされました。',
            'username': u'arcade1up_watcherbot',
            'icon_emoji': u':smile_cat:',
            'link_names': 1,
            }))
            #print("電源断")
        else:
            requests.post(WEB_HOOK_URL, data = json.dumps({
            'text': u'電源投入されました。',
            'username': u'arcade1up_watcherbot',
            'icon_emoji': u':smile_cat:',
            'link_names': 1,
            }))
            #print("電源導入")
    return

GPIO.add_event_detect(PIN_EMERGENCY, GPIO.RISING, bouncetime=100)
GPIO.add_event_callback(PIN_EMERGENCY, switch_callback)

server_address = ('172.31.27.241', 8001)
httpd = ThreadedHTTPServer(server_address, GreetingHandler)
httpd.serve_forever()

#print("来てる？")

try:
    while True:
        if GPIO.input(PIN_FIRE) == GPIO.LOW:
            #print("LOW===========================")
            if last_status == LOW:
                repeat_count += 1
            else:
                repeat_count = 0
            last_status = LOW
        else:
            #print("HIGH")
            if last_status == HIGH:
                repeat_count += 1
            else:
                repeat_count = 0
            last_status = HIGH
        power_status_check(repeat_count, last_status)
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()

