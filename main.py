import json
import requests
from requests.exceptions import Timeout
from requests.structures import CaseInsensitiveDict
import subprocess
import time
import os
import socket
import re

is_debug = False


class Logging:

    @staticmethod
    def error(message):
        print('\033[31m' + message + '\033[0m')

    @staticmethod
    def success(message):
        print('\033[32m' + message + '\033[0m')


proxies = {
    'http': "127.0.0.1:8080"
}

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')


def banner():
    clear()
    print('''\n\n
    ▀█▀ █░█ █▀▀   █▄▄ █▀█ █▀█ ▄▀█ █▀▄   █▀▀ ▀▄▀ █▀█ █▀▀ █▀█ ▀█▀
    ░█░ █▀█ ██▄   █▄█ █▀▄ █▄█ █▀█ █▄▀   ██▄ █░█ █▀▀ ██▄ █▀▄ ░█░  From Ajtech
    \t\tFor Born Network Engineers 
    \n\tDeveloper : Ajmal CP \t  Version : 1.0.2 \t Release Date : 11-06-2022''')
    try:
        Logging.success(f"\tConnected to {devip}")
        print("")
    except:
        pass


def getDevMac(devip):
    arp = subprocess.run(['arp', '-a', devip], capture_output=True, shell=True)
    a = str(arp.stdout)
    mac = a.split('\\r')[3].split('     ')[2].split('-')
    mac_upper = "".join(mac).upper()
    if mac_upper is None:
        raise Exception("Couldn't connect to device. Please connect to a network")
    else:
        return mac_upper


def modechanger():
    while True:
        banner()
        print('Genexis Platinum 4410 Pon Mode Change')
        print('---------------------------------------')
        print('')
        print('[1] Gpon')
        print('[2] Epon')
        print('')
        print('[0] Back')
        print('\n')
        mode_id = str(input('Choose [Back] : ')) or str(0)
        print('')
        if mode_id == '0':
            break


        modes = {
            '1': 'GPON',
            '2': 'EPON',
        }
        mode = modes.get(mode_id)
        change_to = CaseInsensitiveDict()
        if mode == "EPON":
            change_to = 'modeval=EPON&modetype=2&wantype=2&transMode=PON&rebootToChangeMode=Yes&restoreFlag=1&setmode_flag=1&mode_flag=0'

        elif mode == "GPON":
            change_to = 'modeval=GPON&modetype=1&wantype=1&transMode=PON&rebootToChangeMode=Yes&restoreFlag=1&setmode_flag=1&mode_flag=0'


        if change_to != None:
            try:
                sid = requests.get(f"http://{devip}", timeout=5).cookies['SESSIONID']
                dev_conf = {'IP': devip, 'MAC': dev_mac, 'SESSIONID': sid, 'USERID': uname, 'PASSWORD': pwd}
                url = f'http://{dev_conf["IP"]}/cgi-bin/setmode.asp'
                headers = CaseInsensitiveDict()
                headers[
                    'Cookie'] = f"SESSIONID={dev_conf['SESSIONID']};UID={dev_conf['USERID']};PSW={dev_conf['PASSWORD']}"
                setmode = requests.post(url, data=change_to, headers=headers,
                                        proxies=proxies) if is_debug else requests.post(
                    url, data=change_to, headers=headers)
            except KeyError:
                Logging.error('Device Not Support')
                Logging.error('Make sure the device is GENEXIS Platinum 4410')
                continue
            except Timeout:
                Logging.error("Timeout. Couldn't connect to device")
                continue
            except TimeoutError:
                Logging.error(f"Couldn't connect to {devip}. Please connect to a network")
                continue
            except Exception as ex:
                Logging.error(f"Couldn't connect to {devip}. Please connect to a network")
                continue
            else:
                if setmode.status_code == 200:
                    Logging.success("Operation Success")
                    Logging.success(f"Current mode set to  {mode}")
                    Logging.success("Device Rebooting........")
                else:
                    Logging.error("Something went worng.Please try again")

                print('')
                if str(input("Press any key for try again or [0] Back  : ")) == "0":
                    break
                else:
                    continue



def getGatewayMac(ip):
    banner()
    print('Gateway MAC Address')
    print('---------------------')
    print('')
    gateway_mac = getDevMac(ip)
    print(f'Gateway MAC : {gateway_mac}')
    print('\n')
    while input("Press Enter to Back"):
        break


class Manu():

    @staticmethod
    def main_manu():

        manu_args = {
            '0': 'exit(0)',
            '1': f'modechanger()',
            '2': f'getGatewayMac(devip)'
        }
        while True:
            try:
                banner()
                print('Main Manu')
                print('----------------------------')
                print('')
                print('[1] Mode Changer\t#Genexis Platinum 4410 Pon Mode Change')
                print('[2] Get Gateway Mac\t#Get gateway mac address')
                print('[0] Exit')
                print('\n')
                arg = str(input('Choose : '))
                if not arg:
                    continue
                if arg == '0':
                    break
                else:
                    eval(manu_args.get(arg))
            except Exception as ex:
                print(ex)
                Logging.error("Invalid Option. Please Choose a correct option")


if __name__ == "__main__":

    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    banner()
    while True:
        print('\n')
        devip = str(input("Enter Device IP [192.168.1.1]: ")) or '192.168.1.1'
        if not pattern.search(devip):
            Logging.error('Please provide valid ip address')
            continue
        try:
            s = socket.socket()
            s.settimeout(3)
            s.connect((devip, 80))
            dev_mac = getDevMac(devip)
            uname = str(input("Enter Device Username [admin]: ")) or 'admin'
            pwd = str(input("Enter password [Default] : ")) or dev_mac

        except KeyError:
            Logging.error('Device Not Support')
            Logging.error('Make sure the device is GENEXIS Platinum 4410')
            continue
        except Timeout:
            Logging.error("Timeout. Couldn't connect to device")
            continue
        except TimeoutError:
            Logging.error(f"Couldn't connect to {devip}. Please connect to a network")
            continue
        except Exception as ex:
            Logging.error(f"Couldn't connect to {devip}. Please connect to a network")
            continue
        else:
            break

    Manu.main_manu()
