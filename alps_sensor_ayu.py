# -*- coding: utf-8 -*- 
from bluepy.btle import Peripheral
import struct 
import bluepy.btle as btle
import binascii
import sys
import datetime
import os
import json
from ftplib import FTP
 
def s16(value):
    return -(value & 0b1000000000000000) | (value & 0b0111111111111111)

def on_connect(event_trigger, data):
    print('on_connect_function')


class NtfyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data): 
        # ... perhaps check cHandle
        # ... process 'data'
        cal = binascii.b2a_hex(data)
        #print(u'handleNotification : {0}-{1}:'.format(cHandle, cal))

        if int((cal[0:2]), 16) == 0xf3:
            Pressure = int((cal[6:8] + cal[4:6]), 16) * 860.0/65535 + 250	
            Humidity = 1.0 * (int((cal[10:12] + cal[8:10]), 16) - 896 )/64
            Temperature = 1.0*((int((cal[14:16] + cal[12:14]), 16) -2096)/50)
            UV = int((cal[18:20] + cal[16:18]), 16) / (100*0.388)
            AmbientLight = int((cal[22:24] + cal[20:22]), 16) / (0.05*0.928)
            print('Pressure:{0:.3f} Humidity:{1:.3f} Temperature:{2:.3f} '.format(Pressure, Humidity , Temperature))
            print('UV:{0:.3f} AmbientLight:{1:.3f} '.format(UV, AmbientLight))
            

            #localに保存
            min_now = datetime.datetime.now()
            min_now = min_now.strftime('%Y-%m-%d-%H-%M')
            hour_now = datetime.datetime.now()
            hour_now = hour_now.strftime('%Y-%m-%d-%H')
            min_dic = {}
            min_dic['Temperature'] = Temperature
            min_dic['Humidity'] = Humidity
            min_dic['Pressure'] = Pressure
            min_dic['UV'] = UV
            min_dic['AmbientLight'] = AmbientLight
            target_file = './data/' + alps.sensor_number + '/' + hour_now + '.json'

            if os.path.isfile(target_file):
                with open(target_file, 'r') as f:
                    read_json = json.load(f)
                    read_json[min_now] = min_dic
                with open(target_file, 'w') as f:
                    json.dump(read_json, f, indent = 2)

            else:
                new_dic = {}
                new_dic[min_now] = min_dic
                with open(target_file, 'w') as f:
                    json.dump(new_dic, f, indent = 2)
              
                #新しいファイルが作成されるときに前の時間のデータをQNAPに転送
                last_hour = (datetime.datetime.now() + datetime.timedelta(hours = -1)).strftime('%Y-%m-%d-%H')
                trans_file_path = './data/' + alps.sensor_number + '/' + last_hour + '.json'
                qnap_path = 'SmaAgri/Orchid/sonoda/' + alps.sensor_number + '/' + last_hour + '.json'

                ftp_qnap = FTP('10.26.0.1')
                ftp_qnap.set_pasv('true')
                ftp_qnap.login('ayu_ftp', 'WestO831')
                if os.path.isfile(trans_file_path):
                  with open(trans_file_path, 'rb') as f:
                    ftp_qnap.storlines('STOR /' + qnap_path, f)
                ftp_qnap.close()
              

class AlpsSensor(Peripheral):
    def __init__(self,addr, sensor_number):
        Peripheral.__init__(self,addr)
        self.result = 1
        self.address = addr
        self.sensor_number = sensor_number
 
def get_mac_address(sensor_number):
    with open('./sensors.txt') as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        mac_address = [line for line in lines if sensor_number in line][0][-17:]
    return mac_address
    

def main():
    print(alps.sensor_number)
    print(alps.address)
    alps.setDelegate(NtfyDelegate(btle.DefaultDelegate))
 
    #Hybrid MAG ACC8G　100ms　/ Other 1s
    alps.writeCharacteristic(0x0013, struct.pack('<bb', 0x01, 0x00), True)# Custom1 Notify Enable 
    alps.writeCharacteristic(0x0016, struct.pack('<bb', 0x01, 0x00), True)# Custom2 Notify Enable
     
    alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x2F, 0x03, 0x03), True)# (不揮発)保存内容の初期化
    alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x01, 0x03, 0x7C), True)# 気圧,温度,湿度,UV,照度を有効
    alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x04, 0x03, 0x00), True)# slowモード 
    alps.writeCharacteristic(0x0018, struct.pack('<bbbb', 0x05, 0x04, 0x3C, 0x00), True) # Slow 1sec (気圧,温度,湿度,UV,照度)     

    alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x2F, 0x03, 0x01), True)# 設定内容保存
    alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x20, 0x03, 0x01), True)# センサ計測開始
     
# Main loop --------
    while True:
        if alps.waitForNotifications(1.0):
            # handleNotification() was called
            continue

        print("Waiting...")
        # Perhaps do something else here
if __name__ == "__main__":
    alps = AlpsSensor(get_mac_address(sys.argv[1]), sys.argv[1])
    main()
