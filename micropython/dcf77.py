import time
from micropython import const, alloc_emergency_exception_buf
from uctypes import addressof
from machine import Pin, PWM, Timer
import dst

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

led=Pin(2,Pin.OUT)
antena=Pin(15,Pin.OUT)
cw=PWM(antena,freq=100000,duty=0)
cw.deinit()
cw=PWM(antena,freq=77500,duty=0)

timer=Timer(3)

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

@micropython.viper
def second_tick(t):
  p=ptr8(addressof(second))
  m=ptr8(addressof(minute))
  if p[0]<59:
    led.on()
    cw.duty(128)
    time.sleep_ms(100+100*(m[p[0]]&1))
    cw.duty(512)
    led.off()
    p[0]+=1
  else:
    generate_time()
    generate_minute()
    print(minute)
    p[0]=0

def run():
  timer.init(mode=Timer.PERIODIC, period=1000, callback=second_tick)

#t=time.localtime()
#print(t)
#print(t[cyear],t[cmonth],t[cday],t[chour],t[cminute],t[csecond],t[cweekday])
generate_time()
generate_minute()
print(minute)
run()
