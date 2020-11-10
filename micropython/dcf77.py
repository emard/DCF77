from ntptime import settime
from micropython import const, alloc_emergency_exception_buf
from uctypes import addressof
from machine import Pin, Timer, I2C
from esp32 import RMT
from wifiman import get_connection
import time, dst
import ssd1306

cyear=const(0)
cmonth=const(1)
cday=const(2)
chour=const(3)
cminute=const(4)
csecond=const(5)
cweekday=const(6)
cdst=const(7)

# time Y-M-D h:m:s weekday dst
sendtime=bytearray(8)
# second counter 0-59
second=bytearray(1)
# TX bits for one minute
minute=bytearray(59)
# index for writing to minute[]
index=bytearray(1)
# 1-second timer
timer=Timer(3)

# last day NTP was set
ntpday=0

led=Pin(2,Pin.OUT)
antena=Pin(15,Pin.OUT)
ask=RMT(0,pin=antena,carrier_freq=0,clock_div=1) # 80 MHz
ask.loop(True)

i2c = I2C(scl=Pin(4), sda=Pin(5))
oled = ssd1306.SSD1306_I2C(128, 64, i2c, 0x3c)
oled.fill(0)
oled.text("DCF77", 0, 0)
oled.show()

weekdaystr = ["MO","TU","WE","TH","FR","SA","SU"]

# desired carrier frequency
freq=77500
# tuning paramters - adjust with scope
# coarse tuning, about 75 Hz per step
tuning_coarse=0
# fine tuning 0-16, about 5 Hz per step
tuning_fine=2

period=int(ask.source_freq())//freq-tuning_coarse
print("period", period)
# coarse tuned for 77.5 kHz
# power level 2 (50% DTC)
on2=period//2
off2=period-on2
# power level 1 (adjust 25% amplitude on scope)
on1=on2*13//100
off1=period-on1

# debug - no level change
#on1=on2
#off1=off2
#on2=on1
#off2=off1

def tuning(t):
  global pwr1, pwr2
  m=16 # levels of fine tuning
  pwr1=[]
  pwr2=[]
  for i in range(m):
    pwr1.append(off1)
    pwr1.append(on1)
    pwr2.append(off2)
    pwr2.append(on2)
  for i in range(t):
    pwr1[i*2]-=1
    pwr2[i*2]-=1
  # print tuning results, should be around 77500 for both
  print("tuning", int(ask.source_freq())*m//sum(pwr1), int(ask.source_freq())*m//sum(pwr2), "Hz")

# write n bits of val at ith position, LSB first
@micropython.viper
def to_binary(i:int, val:int, n:int):
  m=ptr8(addressof(minute))
  for j in range(n):
    m[i+j]=48+(val&1)
    val >>= 1

# write n bits of bcd starting from minute[i]
@micropython.viper
def bcd(val:int, n:int):
  x=ptr8(addressof(index))
  i=x[0]
  if n>4:
    to_binary(i,val%10,4)
    to_binary(i+4,val//10,n-4)
  else:
    to_binary(i,val,n)
  x[0]+=n

# write parity for previous n bits
@micropython.viper
def parity(n:int):
  x=ptr8(addressof(index))
  m=ptr8(addressof(minute))
  p=0
  j=x[0]-1
  for i in range(n):
    p^=m[j-i]
  m[x[0]]=48+(p&1)
  x[0]+=1

def generate_time():
  t=time.time()+60
  lt=dst.localtime(t)
  for i in range(7):
    sendtime[i]=lt[i]%100
  if dst.is_dst(t):
    sendtime[cdst]=1
  else:
    sendtime[cdst]=0

# convert timebcd to minute bits
@micropython.viper
def generate_minute():
  m=ptr8(addressof(minute))
  x=ptr8(addressof(index))
  for i in range(17):
    m[i]=48
  # skip first 17 bits
  x[0]=17
  #to_binary(0,0x55,8)
  if sendtime[cdst]:
    bcd(1,2)
  else:
    bcd(2,2)

  # start time code
  bcd(2,2)

  # minutes + parity
  bcd(sendtime[cminute],7)
  parity(7)
  
  # hours + parity bit
  bcd(sendtime[chour],6)
  parity(6)

  # day of month
  bcd(sendtime[cday],6)

  # day of week
  bcd(int(sendtime[cweekday])+1,3)
  
  # month
  bcd(sendtime[cmonth],5)
  
  # year (0-99) + parity for all 22 date bits
  bcd(sendtime[cyear],8)
  parity(22)

def set_ntp():
  global ntpday
  try:
    settime()
    ntpday=time.localtime()[cday]
  except:
    ntpday=0

def second_tick(t):
  #global pwr1, pwr2
  p=memoryview(second)
  m=memoryview(minute)
  xd=(p[0]%15)*8
  yd=(p[0]//15)*12+17
  if p[0]<59:
    if ntpday>0:
      bit=m[p[0]]&1
      led.on()
      ask.write_pulses(pwr1,start=0)
      time.sleep_ms(100*(bit+1))
      ask.write_pulses(pwr2,start=0)
      led.off()
      oled.text("%d"%bit,xd,yd)
      oled.hline(xd,yd+10,(bit+1),1)
      oled.hline(xd+bit+1,yd+8,7-bit,1)
    oled.show()
    p[0]+=1
  else:
    if ntpday==0 or (sendtime[cday]!=ntpday and sendtime[cminute]==30):
      set_ntp()
    if ntpday==0:
      ask.write_pulses([4000],start=0) # turn off transmitter
      get_connection() # if not connected, reconnect to internet
    generate_time()
    generate_minute()
    # every 10 minutes synchronize seconds
    if sendtime[cminute]%10==5:
      p[0]=sendtime[csecond]
    else:
      p[0]=0
    oled.hline(xd,yd+8,8,1)
    oled.show()
    oled.fill(0)
    oled.text("DST%d %02d:%02d NTP%d" %
      (sendtime[cdst],sendtime[chour],sendtime[cminute],ntpday),0,0)
    oled.text("20%02d-%02d-%02d %2s" %
      (sendtime[cyear],sendtime[cmonth],sendtime[cday],weekdaystr[sendtime[cweekday]]),0,8)

def run():
  timer.init(mode=Timer.PERIODIC, period=1000, callback=second_tick)

set_ntp()
tuning(tuning_fine)
generate_time()
generate_minute()
second[0]=sendtime[csecond]
print(minute)
run()
