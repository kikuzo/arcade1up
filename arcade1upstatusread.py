#!/usr/bin/python
#-*-coding: utf-8-*-

import RPi.GPIO as GPIO
import time
import requests, json

PIN_FIRE = 14
PIN_EMERGENCY = 18

# slack webhook archade1up channel
WEB_HOOK_URL = "https://hooks.slack.com/services/XXXXXXXXX/YYYYYYYYYYYYY"

LOW = 0
HIGH = 1
repeat_count = 0
last_status = LOW

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_FIRE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_EMERGENCY, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def switch_callback(self):
    time.sleep(0.03)
    if GPIO.input(PIN_EMERGENCY) != GPIO.HIGH:
        return
    requests.post(WEB_HOOK_URL, data = json.dumps({
        'text': u'エマージェンシーボタンが押されました。\n \
        応答を返す場合には <http://172.31.27.241/reply_led |応答(未実装) > をクリックしてください。\n \
        エマージェンシー状態をクリアする場合は <http://172.31.27.241/clear_led |クリア(未実装) > をクリックしてください。',
        'username': u'arcade1up_watcherbot',
        'icon_emoji': u':smile_cat:',
        'link_names': 1,
    }))
    return

def power_status_check(repeat_count, last_status):
    if repeat_count == 10:
        if last_status == LOW:
            requests.post(WEB_HOOK_URL, data = json.dumps({
            'text': u'電源が落とされたようです。',
            'username': u'arcade1up_watcherbot',
            'icon_emoji': u':smile_cat:',
            'link_names': 1,
            }))
            print("電源断")
        else:
            requests.post(WEB_HOOK_URL, data = json.dumps({
            'text': u'電源が投入されたようです。',
            'username': u'arcade1up_watcherbot',
            'icon_emoji': u':smile_cat:',
            'link_names': 1,
            }))
            print("電源導入")
    return

GPIO.add_event_detect(PIN_EMERGENCY, GPIO.RISING, bouncetime=100)
GPIO.add_event_callback(PIN_EMERGENCY, switch_callback)

try:
    while True:
        if GPIO.input(PIN_FIRE) == GPIO.LOW:
            print("LOW===========================")
            if last_status == LOW:
                repeat_count += 1
            else:
                repeat_count = 0
            last_status = LOW
        else:
            print("HIGH")
            if last_status == HIGH:
                repeat_count += 1
            else:
                repeat_count = 0
            last_status = HIGH
        power_status_check(repeat_count, last_status)
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
