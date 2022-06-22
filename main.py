import json
import requests
from requests.exceptions import Timeout
from requests.structures import CaseInsensitiveDict
import subprocess
import time
import os
import socket
import re
import netifaces

is_debug = False


class Logging:
    @staticmethod
    def error(message):
        print('\033[31m' + message + '\033[0m')

    @staticmethod
    def success(message):
        print('\033[32m' + message + '\033[0m')


class Api_exception(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


proxies = {
    'http': "127.0.0.1:8080"
}

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')


def req(method, url, header=None):
    if header is None:
        header = CaseInsensitiveDict()
    header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'

    if method == 'get':
        response = requests.get(url, headers=header,
                                proxies=proxies) if is_debug else requests.get(
            url, headers=header, timeout=5)
    elif method == 'post':
        response = ''
        pass
        # result = requests.post(url, data=change_to, headers=headers,
        #                         proxies=proxies) if is_debug else requests.post(
        #     url, data=change_to, headers=headers)
    # except requests.exceptions.ConnectionError:
    #     Logging.error("Process couldn't complete")
    #     Logging.error("Please check your internet connection")
    # except Exception as ex:
    #     print(type(ex))
    #     print(ex)
    # else:
    if response.status_code == 200:
        return response.json()
    else:
        Logging.error("Not found 404")


def banner():
    clear()
    print('''\n\n
    ▀█▀ █░█ █▀▀   █▄▄ █▀█ █▀█ ▄▀█ █▀▄   █▀▀ ▀▄▀ █▀█ █▀▀ █▀█ ▀█▀
    ░█░ █▀█ ██▄   █▄█ █▀▄ █▄█ █▀█ █▄▀   ██▄ █░█ █▀▀ ██▄ █▀▄ ░█░  From Ajtech
    \t\tFor Born Network Engineers 
    \n\tDeveloper : Ajmal CP \t  Version : 1.0.3 \t Release Date : 13-06-2022''')
    print('\n')


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
    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    banner()
    try:
        while True:
            print('\n')
            devip = str(input("Enter ONT IP [192.168.1.1]: ")) or '192.168.1.1'
            if not pattern.search(devip):
                Logging.error('Please provide valid ip address')
                continue
            try:
                s = socket.socket()
                s.settimeout(3)
                s.connect((devip, 80))
                dev_mac = getDevMac(devip)
                # uname = str(input("Enter Device Username [admin]: ")) or 'admin'
                # pwd = str(input("Enter password [Default] : ")) or dev_mac
                uname = 'admin'
                pwd = dev_mac
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
                    if str(input("Press any key for try again or [0] Back  : ")) == "0":
                        break
                    else:
                        continue
                except Timeout:
                    Logging.error("Timeout. Couldn't connect to device")
                    if str(input("Press any key for try again or [0] Back  : ")) == "0":
                        break
                    else:
                        continue
                except TimeoutError:
                    Logging.error(f"Couldn't connect to {devip}. Please connect to a network")
                    if str(input("Press any key for try again or [0] Back  : ")) == "0":
                        break
                    else:
                        continue
                except Exception as ex:
                    Logging.error(f"Couldn't connect to {devip}. Please connect to a network")
                    if str(input("Press any key for try again or [0] Back  : ")) == "0":
                        break
                    else:
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
    except KeyboardInterrupt:
        pass


def getGatewayMac():
    banner()
    print('Gateway MAC Address')
    print('---------------------')
    print('')
    try:
        gateways = netifaces.gateways()
        default_gateway = gateways['default'][netifaces.AF_INET][0]
        gateway_mac = getDevMac(default_gateway)
    except IndexError:
        Logging.error("Request couldn't complete")
        Logging.error("There are no default gateway yet")

    except Exception as ex:
        # print(ex)
        # print(type(ex))
        Logging.error("Something went wrong")
    else:
        Logging.success(f'Default Gateway MAC : {gateway_mac}')
        Logging.success(f'Default Gateway     : {default_gateway}')
    print('\n')
    try:
        while input("Press Enter to Back"):
            break
    except KeyboardInterrupt:
        pass


def get_pub_ip():
    banner()
    print('Public IP Address & Information')
    print('-------------------------------')
    print('')

    try:
       api_server = 'http://ip-api.com/json/'
       result = req(method='get', url=api_server)

       if result['status'] == "success":
           Logging.success(f"PUBLIC IPV4 : {result['query']}")
           Logging.success(f'ISP: {result["isp"] if result["isp"] != "" else None}')
           Logging.success(f'AS: {result["as"] if result["as"] != "" else None}')
           Logging.success(f'CITY: {result["city"] if result["city"] != "" else None}')
           Logging.success(f'REGION: {result["regionName"] if result["regionName"] != "" else None}')
           Logging.success(f'COUNTRY: {result["country"] if result["country"] != "" else None}')
           Logging.success(f'ZIP: {result["zip"] if result["zip"] != "" else None}')
       else:
           Logging.error("Something went wrong. Try again")
    except requests.exceptions.ConnectionError as ex:
        Logging.error("Process couldn't complete")
        Logging.error("Please check you internet connection")
    except Exception as ex:
        Logging.error("Process couldn't complete")
        Logging.error("Something went wrong")
        # print(ex)
        # print(type(ex))

    print('\n')
    try:
        while input("Press Enter to Back"):
            break
    except KeyboardInterrupt:
        pass


class Manu():

    @staticmethod
    def main_manu():

        manu_args = {
            '0': 'exit(0)',
            '1': f'getGatewayMac()',
            '2': f'get_pub_ip()',
            '3': f'modechanger()'
        }
        try:
            while True:
                try:
                    banner()
                    print('Main Manu')
                    print('---------')
                    print('')
                    print('''
[1] Display Gateway Mac     - Display gateway mac address
[2] What is my ip           - Display your public address
[3] Mode changer            - Genexis Platinum 4410 Pon Mode Change
[0] Exit                    - Exit
                            ''')

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
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    Manu.main_manu()
