import json
import requests
from requests.exceptions import Timeout
from requests.structures import CaseInsensitiveDict
import subprocess
import time
import os
import socket
import re

proxies = {
    'http' : "127.0.0.1:8080"
}


clear = lambda: os.system('cls' if os.name=='nt' else 'clear')

def banner():
    clear()
    print('''\n\n
    ▀█▀ █░█ █▀▀   █▄▄ █▀█ █▀█ ▄▀█ █▀▄   █▀▀ ▀▄▀ █▀█ █▀▀ █▀█ ▀█▀
    ░█░ █▀█ ██▄   █▄█ █▀▄ █▄█ █▀█ █▄▀   ██▄ █░█ █▀▀ ██▄ █▀▄ ░█░  From Ajtech
    \t\tFor Born Network Engineers 
    \n\tDeveloper : Ajmal CP \t  Version : 1.0.0b \t Release Date : 06-06-2022
    \n''')



def modechanger(dev_conf):
    banner()
    print('Genexis Platinum 4410 Pon Mode Change')
    print('---------------------------------------')
    print('')
    print('[0] EPON')
    print('[1] GPON')
    print('\n')
    mode_id = str(input('Choose [0 : EPON] :')) or str(0)
    modes = {
        '1' : 'GPON',
        '0' : 'EPON'
    }
    mode = modes.get(mode_id)
    change_to = CaseInsensitiveDict()
    if mode == "EPON":
        change_to = 'modeval=EPON&modetype=2&wantype=2&transMode=PON&rebootToChangeMode=Yes&restoreFlag=1&setmode_flag=1&mode_flag=0'

    elif mode == "GPON":
        change_to = 'modeval=GPON&modetype=1&wantype=1&transMode=PON&rebootToChangeMode=Yes&restoreFlag=1&setmode_flag=1&mode_flag=0'

    if change_to != None:
        url = f'http://{dev_conf["IP"]}/cgi-bin/setmode.asp'
        headers = CaseInsensitiveDict()
        headers['Cookie'] = f"SESSIONID={dev_conf['SESSIONID']};UID={dev_conf['USERID']};PSW={dev_conf['PASSWORD']}"
        setmode = requests.post(url, data=change_to, headers=headers, proxies=proxies)

        if setmode.status_code == 200:
            print('\033[32m' + "Operation Success" + '\033[0m')
            print('\033[32m' + f"Current Mode : {mode}" + '\033[0m')
            print('\033[32m' + "Device Rebooting........" + '\033[0m')
            time.sleep(5)
        else:
            print('\033[31m' + "Something went worng.Please try again" + '\033[0m')
            time.sleep(5)



def getDevMac(devip):
    arp = subprocess.run(['arp', '-a', devip], capture_output=True, shell=True)
    a = str(arp.stdout)
    mac = a.split('\\r')[3].split('     ')[2].split('-')
    mac_upper = "".join(mac).upper()
    if mac_upper is None:
        raise Exception("Couldn't connect to device. Please connect to a network")
    else:
        return mac_upper

class Manu():

    @staticmethod
    def main_manu():

        manu_args = {
            '0': 'exit(0)',
            '1': f'modechanger({dev_conf})'
        }
        while True:
            try:
                banner()
                print('Main Manu')
                print('----------------------------')
                print('')
                print('[1] Mode Changer\t#Genexis Platinum 4410 Pon Mode Change')
                print('[0] Exit')
                print('\n')
                arg = str(input('Choose : '))
                if not arg:
                    continue
                if arg == '0':
                    break
                else:
                    eval(manu_args.get(arg))
            except:
                print('\033[31m' + "Invalid Option. Please Choose a correct option" + '\033[0m')



if __name__ == "__main__":
    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    banner()
    while True:
        print('\n')
        devip = str(input("Enter Device IP [192.168.1.1]: ")) or '192.168.1.1'
        if not pattern.search(devip):
            print('\033[31m' + 'Please provide valid ip address' + '\033[0m')
            continue
        try:
            s = socket.socket()
            s.settimeout(3)
            s.connect((devip, 80))
            dev_mac = getDevMac(devip)
            uname = str(input("Enter Device Username [admin]: ")) or 'admin'
            pwd = str(input("Enter password [Default] : ")) or dev_mac
            sid = requests.get(f"http://{devip}", timeout=5).cookies['SESSIONID']
            dev_conf = {'IP': devip, 'MAC': dev_mac, 'SESSIONID': sid, 'USERID': uname, 'PASSWORD': pwd}
        except KeyError:
            print('\033[31m' + 'Device Not Support' + '\033[0m')
            print('\033[31m' + 'Make sure the device is GENEXIS Platinum 4410' + '\033[0m')
            continue
        except Timeout:
            print('\033[31m' + "Timeout. Couldn't connect to device" + '\033[0m')
            continue
        except TimeoutError:
            print('\033[31m' + f"Couldn't connect to {devip}. Please connect to a network" + '\033[0m')
            continue
        except Exception as ex:
            print('\033[31m' + f"Couldn't connect to {devip}. Please connect to a network" + '\033[0m')
            continue
        else:
            break

    Manu.main_manu()










