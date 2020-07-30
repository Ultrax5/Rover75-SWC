#!/usr/bin/env python3
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
import alsaaudio
import os
import threading
from threading import Thread
from adafruit_ads1x15.analog_in import AnalogIn
def vol_down(mixer):
    current_volume = mixer.getvolume()
    if current_volume[0]-5>=0:
        mixer.setvolume(current_volume[0]-5)
        return
    if current_volume[0]<5:
        mixer.setvolume(0)
    return
def vol_up(mixer):
    current_volume = mixer.getvolume()
    if current_volume[0]+5 <=100:
        mixer.setvolume(current_volume[0]+5)
        return
    if 95<current_volume[0]<100:
        mixer.setvolume(100)
    return
def mode(saved_volume, mixer):
    if mixer.getvolume()[0]==0:
        if saved_volume!=-1:
            mixer.setvolume(saved_volume)
        else:
            mixer.setvolume(30)
    else:
        mixer.setvolume(0)
    return
def next_track(mixer):
    mixer = alsaaudio.Mixer()
    current_volume = mixer.getvolume()
    return
def prev_track(mixer):
    mixer = alsaaudio.Mixer()
    current_volume = mixer.getvolume()
    return
# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)
# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

#Create single-ended input on channel 0
ignition = AnalogIn(ads, ADS.P1)
swc = AnalogIn(ads, ADS.P3)
lock = threading.Lock()
lock2 = threading.Lock()
saved_swc_v=-1
def main():
    mixer = prepare()
    loop(mixer)
def loop(mixer):
    global lock
    global lock2
    global saved_swc_v
    mute_time = -1
    last_time = -1
    saved_volume = -1
    while True:
#         with lock:
        temp=swc.voltage
#         with lock2:
        temp_saved=saved_swc_v
        if temp > 1.7:
            saved_swc_v = (saved_swc_v+temp)/2
        print("SAVED"+str(saved_swc_v))
        print(temp_saved*0.5)
        print("current: "+str(temp))
        print(temp_saved*0.6)
        if temp < 0 and ignition.voltage > 0:
            vol_down(mixer)
        elif 0.075*temp_saved < temp < 0.125*temp_saved:
            vol_up(mixer)
        elif 0.35*temp_saved < temp < 0.45*temp_saved:
            prev_track(mixer)
        elif 0.2*temp_saved < temp < 0.3*temp_saved:
            next_track(mixer)
        elif 0.5*temp_saved < temp < 0.6*temp_saved:
            print("mode")
            if mixer.getvolume()[0]!=0:
                saved_volume = mixer.getvolume()[0]
            if mute_time+200000000<time.time_ns() or mute_time==-1:
                mute_time = time.time_ns()
                mode(saved_volume, mixer)
        if ignition.voltage < 0:
            if last_time == -1:
                last_time=time.time_ns()
            else:
                if last_time+60000000000<time.time_ns():
                    os.system('systemctl poweroff')
        else:
            last_time = -1
# def update_voltage():
#     global saved_swc_v
#     global lock
#     while True:
#         sum_v = 0
#         for x in range(0, 10):
#     #         print("co za kurwa jebana")
#             with lock:
#                 print("co tu sie odpierdala"+str(swc.voltage))
#                 sum_v += swc.voltage
#     #         print(sum_v)
#         with lock2:
#             saved_swc_v = sum_v/10
#         time.sleep(2)
def prepare():
#     sum_v = 0
#     global saved_swc_v
#     for x in range(0, 10):
# #         print("co za kurwa jebana")
#         sum_v += swc.voltage
# #         print(sum_v)
#         time.sleep(0.1)
#     saved_swc_v = sum_v/10
#     print(saved_swc_v)
    while True:
        try:
            mixer = alsaaudio.Mixer("Master")
            break
        except:
            pass
        time.sleep(1)
    return mixer
main()
