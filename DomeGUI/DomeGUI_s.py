import tkinter as tk
import math
import serial
import configparser
import time
from tkinter import *
from math import *

window = Tk()
window.title("DomeGUI")
window.geometry('400x400')          # размер окна программы
window.maxsize(400, 400)
window.minsize(400, 400)

config = configparser.ConfigParser()            # чтение конфигурации
config.read('DomeGUI.ini')
COM_port = config.get('Serial','COM_port')
baudrate = config.get('Serial','serial_speed')

# Установка цвета элементов
bg_color="#999999"                  # фон
bg_observ="#888888"                 # обсерватория
bg_dome="#dddddd"                   # купол
bg_button="#ffeedd"                 # кнопки
i_on="#33aa00"
i_off="#990000"
i_alert="#ddcc00"
button_on="LightGreen"
symbol="#363230"

az_relay = int(config.get('Dome','azimut_relay'))   # Азимут парковочного датчика
turn_sec = int(config.get('Dome','turn_sec'))       # Время оборота купола, сек


window.configure(bg=bg_color)
c0 = tk.Canvas(window, width = 400, height = 400, bg=bg_color, highlightthickness=0)    # холст на все окно
c0.place(x=0, y=0)
c = tk.Canvas(window, width = 240, height = 240, bg=bg_color, highlightthickness=0)     # холст для купола
c.place(x=150, y=150)

ser = serial.Serial(COM_port, baudrate, bytesize=8, parity='N', stopbits=1, timeout=1)  # конфигурирование COM-порта
# S -запрос состояния купола при включении
time.sleep(2)
ser.write(b'S')
shat_open, srun_on, srelay_0, srelay_1 = ser.readline().decode('utf-8').strip().split(',')

# синхронизация состояния по Arduino
if (int(shat_open) == 1):
    hat_Open = True
else:
    hat_Open = False

if (int(srun_on) == 1):
    run_On = True
else:
    run_On = False

if (int(srelay_0) == 1):
    power_On = True
else:
    power_On = False

if (int(srelay_1) == 1):
    power1_On = True
else:
    power1_On = False

print(hat_Open, run_On, power_On, power1_On)  
# z -запрос текущего азимута от Arduino, синхронизация индикатора
ser.write(b'z')
az = round(float(ser.readline().decode('utf-8').strip())) + az_relay
if az >= 360:
    az -= 360
elif az <= 0:
    az += 360
az_graph=az_relay+90-az

# r -вращение вправо
# l -вращение влево
# o -открыть купол
# c -закрыть купол
# p -парковка
# 0 -питание телескопа
# 1 -питание реле №1
# A -включить ведение
# x -выключить ведение

def btn_right_click():
    global az, az_relay, az_graph
    ser.write(b'r')
    az += 5
    az_graph -= 5
    if az >= 360:
        az -= 360
    c.itemconfig(sector, start = (az_graph-20))
    c.itemconfig(azimut_label, text=(str(az)+chr(176)))
    if az == az_relay:
        c.itemconfig(line_0, fill=i_on)
    else:
        c.itemconfig(line_0, fill=bg_dome)
    return az

def btn_left_click():
    global az, az_relay, az_graph
    ser.write(b'l')
    az -= 5
    az_graph += 5
    if az <= 0:
        az += 360
    c.itemconfig(sector, start = (az_graph-20))
    c.itemconfig(azimut_label, text=(str(az)+chr(176)))
    if az == az_relay:
        c.itemconfig(line_0, fill=i_on)
    else:
        c.itemconfig(line_0, fill=bg_dome)
    return az

##############################################################################################
def autorun():
    global az, az_relay, az_graph
    az += 1
    az_graph -= 1
    if az >= 360:
        az -= 360
    c.itemconfig(sector, start = (az_graph-20))
    ser.write(b'A')
    window.after(200, btn_run_m)
    return az

def btn_run_click():
    global az, az_relay, az_graph, run_On
#    az += 5
#    az_graph -= 5
#    if az >= 360:
#        az -= 360
    c.itemconfig(sector, start = (az_graph-20))
    c.itemconfig(azimut_label, text=(str(az)+chr(176)))
    run_On = not run_On
    if run_On:
        btn_run.configure(bg=button_on)
        ser.write(b'A')
    else:
        btn_run.configure(bg=bg_button)
        ser.write(b'x')
    return az

def btn_park_click():
    global az, az_relay, az_graph, run_On
    ser.write(b'p')
    az = az_relay
    az_graph = 90
    run_On = False
    btn_run.configure(bg=bg_button)
    c.itemconfig(sector, start = (90-20))
    c.itemconfig(azimut_label, text=(str(az)+chr(176)))
    c.itemconfig(line_0, fill=i_on)
    return az

def btn_open_click():
    global hat_Open
    ser.write(b'o')
    hat_Open = True
    c.itemconfig(sector, outline=i_on)
    return hat_Open

def btn_close_click():
    global hat_Open
    ser.write(b'c')
    hat_Open = False
    c.itemconfig(sector, outline=i_off)
    return hat_Open

def btn_scop_click():
    global power_On
    ser.write(b'0')
    power_On = not power_On
    if power_On:
        btn_scop.configure(bg=button_on)
        c0.itemconfig(i_power, fill=i_on)
    else:
        btn_scop.configure(bg=bg_button)
        c0.itemconfig(i_power, fill=i_off)
    return power_On

def btn_power1_click():
    global power1_On
    ser.write(b'1')
    power1_On = not power1_On
    if power1_On:
        c0.itemconfig(i_power1, fill=i_on)
        btn_power1.configure(bg=button_on)
    else:
        c0.itemconfig(i_power1, fill=i_off)
        btn_power1.configure(bg=bg_button)
    return power1_On

# изображения кнопок
img_open = PhotoImage(file='open_hat1.gif')
img_close = PhotoImage(file='close_hat1.gif')
img_run = PhotoImage(file='run.gif')
img_left = PhotoImage(file='left.gif')
img_right = PhotoImage(file='right.gif')
img_scop = PhotoImage(file='scop.gif')
img_power = PhotoImage(file='power.gif')
img_park = PhotoImage(file='park2.gif')
# размещение кнопок
btn_open = Button(window, image=img_open, command=btn_open_click, bg=bg_button).place(x=10, y=30, width = 48, height = 48)
btn_close = Button(window, image=img_close, command=btn_close_click,bg=bg_button).place(x=60, y=30, width = 48, height = 48)

btn_left = Button(window, image=img_left, command=btn_left_click, bg=bg_button).place(x=10, y=90, width = 48, height = 48)
btn_right = Button(window, image=img_right, command=btn_right_click, bg=bg_button).place(x=60, y=90, width = 48, height = 48)
btn_run = Button(window, image=img_run, command=btn_run_click,bg=bg_button)
btn_run.place(x=130, y=90, width = 48, height = 48)
if run_On:
    btn_run.configure(bg=button_on)
else:
    btn_run.configure(bg=bg_button)
btn_park = Button(window, text="P", font=("Arial 24 bold"), fg=symbol, command=btn_park_click, bg=bg_button).place(x=340, y=90, width = 48, height = 48)
btn_scop = Button(window, image=img_power, command=btn_scop_click, bg=bg_button)
btn_scop.place(x=10, y=150, width = 48, height = 48)
btn_power1 = Button(window, text=" #1 ", font=("Arial 14 bold"), fg=symbol, command=btn_power1_click, bg=bg_button)
btn_power1.place(x=10, y=204, width = 48, height = 24)

az_graph=az_relay+90-az

i_power = c0.create_oval(60, 185, 70, 195, fill=i_off, width=1)             #  индикатор питания
if power_On:
    btn_scop.configure(bg=button_on)
    c0.itemconfig(i_power, fill=i_on)
else:
    btn_scop.configure(bg=bg_button)
    c0.itemconfig(i_power, fill=i_off)

i_power1 = c0.create_oval(60, 215, 70, 225, fill=i_off, width=1)            #  индикатор питания №1
if power1_On:
    c0.itemconfig(i_power1, fill=i_on)
    btn_power1.configure(bg=button_on)
else:
    c0.itemconfig(i_power1, fill=i_off)
    btn_power1.configure(bg=bg_button)
    
# Изображение обсерватории и купола
c.create_polygon((10, 75), (10, 165), (75, 230), (165, 230), (230, 165), (230, 75), (165, 10), (75, 10), fill=bg_observ)    # контур обсерватории
c.create_oval(20, 20, 220, 220, fill=bg_dome, outline="black", width=1)                                                     # купол
sector = c.create_arc(28, 28, 212, 212, start=(az_graph-20), extent=40, style=ARC, width=12)                                # окно
if hat_Open:
    c.itemconfig(sector, outline=i_on)
else:
    c.itemconfig(sector, outline=i_off)
azimut_label = c.create_text(120, 120, text=(str(az)+chr(176)), fill="black", font="Arial 14")                              # текущий азимут
line_0 = c.create_line(120, 52, 120, 37, fill=i_off, width=3, arrow=LAST, arrowshape=(10, 10, 6))
if (abs(az - az_relay) <= 1):
    c.itemconfig(line_0, fill=i_on)
else:
    c.itemconfig(line_0, fill=bg_dome)
c.create_line(120, 37, 120, 25, width=1, fill="black")                                                                      # азимут датчика 0

# Метки направлений
c.create_text(120+int(cos(radians(az_relay-90))*108), 120-int(sin(radians(az_relay-90))*108), text="S", fill="white", font="Arial 12")      # S
c.create_text(120+int(cos(radians(az_relay+180))*108), 120-int(sin(radians(az_relay+180))*108), text="W", fill="white", font="Arial 12")    # W
c.create_text(120+int(cos(radians(az_relay+90))*108), 120-int(sin(radians(az_relay+90))*108), text="N", fill="white", font="Arial 12")      # N
c.create_text(120+int(cos(radians(az_relay))*108), 120-int(sin(radians(az_relay))*108), text="E", fill="white", font="Arial 12")            # E

window.mainloop()


