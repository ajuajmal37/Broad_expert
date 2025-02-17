import os
import socket
import sqlite3
import subprocess
import re
import time
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
import netifaces
import requests
from requests.exceptions import Timeout
from requests.structures import CaseInsensitiveDict
import speedtest

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')

is_debug = False

proxies = {
    'http': "127.0.0.1:8080"
}


class NoConnectionException(Exception):
    pass


class NoFound(Exception):
    pass


class Loader:

    def __init__(self, message):
        self.run_msg = message
        self.interval = 0.2
        self.is_done = False
        self._thread = Thread(target=self._loop, daemon=True)

    def _loop(self):
        animation = ["|", "/", "-", "\\"] if os.name == 'nt' else ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        for i in cycle(animation):
            if self.is_done:
                break
            print(f"\r\033[32m{self.run_msg} {i} \033[0m", flush=True, end="")
            time.sleep(self.interval)

    def start(self):
        self._thread.start()
        return self

    def stop(self, type='s', message=''):
        self.is_done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="", flush=True)
        if type == 's':
            print(f"\r\033[32m{message} \033[0m", flush=True)
        elif type == 'e':
            print(f"\r\033[31m{message} \033[0m", flush=True)

    def __exit__(self, exc_type, exc_value, tb):
        self.stop()


class Logging:
    @staticmethod
    def error(message):
        print('\033[31m' + message + '\033[0m')

    @staticmethod
    def success(message):
        print('\033[32m' + message + '\033[0m')


class Dbase:

    def __init__(self):
        self.__conn = sqlite3.connect('asset/broad_db.db')
        self.__query = None
        self.__attrs = None

    def select(self):
        try:
            __w = vars(self)['_Dbase__where']
            self.__query = f'SELECT {self.__attrs} FROM {self.table} WHERE {self.__where}'
        except:
            self.__query = f'SELECT {self.__attrs} FROM {self.table}'
        return self

    def where(self, col, opr, val):
        self.__where = f"{col} {opr} {val}"
        return self

    def get_one(self, *args):
        try:
            self.__attrs = '%s' % ','.join(map(str, args)) if len(args) != 0 else '*'
            self.select()
            cursor = self.__conn.cursor()
            cursor.execute(self.__query)
            records = cursor.fetchone()


        except sqlite3.OperationalError as ex:
            raise ex
        except sqlite3.NameError as ex:
            raise ex
        except sqlite3.ValueError as ex:
            raise ex
        except sqlite3.IOError as ex:
            raise ex
        else:
            cursor.close()
            return records


class Macvenders(Dbase):
    table = "macvendors"


class Utils:
    @staticmethod
    def banner():
        clear()
        print('''\n\n
        ▀█▀ █░█ █▀▀   █▄▄ █▀█ █▀█ ▄▀█ █▀▄   █▀▀ ▀▄▀ █▀█ █▀▀ █▀█ ▀█▀
        ░█░ █▀█ ██▄   █▄█ █▀▄ █▄█ █▀█ █▄▀   ██▄ █░█ █▀▀ ██▄ █▀▄ ░█░  From Ajtech
        \t\tFor Born Network Engineers 
        \n\tDeveloper : Ajmal CP \t  Version : 1.5.1.200722.2311''')
        print('\n')

    @staticmethod
    def ip_in():
        pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
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
                except TimeoutError:
                    Logging.error(f"Couldn't connect to {devip}. Device is offline")
                    continue
                except Exception as ex:
                    Logging.error(f"Couldn't connect to {devip}.  Device is offline")
                    continue
                else:
                    return devip

        except KeyboardInterrupt:
            pass

    @staticmethod
    def getDevMac(devip):
        try:
            if os.name == 'nt':
                arp = subprocess.run(['arp', '-a', devip], capture_output=True, shell=True)
                a = str(arp.stdout)
                mac = a.split('\\r')[3].split('     ')[2].split('-')
                mac_upper = "".join(mac).upper()
            else:
                arp = os.popen(f'arp -a {devip}').read()
                gateway = arp.split('\n')
                mac = gateway[0].split(' ')[3].split(':')
                mac_upper = "".join(mac).upper()


        except Exception:
            raise Exception("Couldn't find gateway address")
        else:
            if mac_upper is None:
                raise Exception("Couldn't connect to device. Please connect to a network")
            else:
                return mac_upper

    @staticmethod
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
            return response
        else:
            NoFound("Not found 404")


class Module():
    @staticmethod
    def getGatewayMac():
        Utils.banner()
        print('Gateway MAC Address')
        print('---------------------')
        print('')
        loader = Loader('Please wait ')
        loader.start()
        try:
            gateways = netifaces.gateways()
            if len(gateways['default']) == 0:
                raise Exception("Their is no default gateway configured yet")

            default_gateway = gateways['default'][netifaces.AF_INET][0]
            gateway_mac = Utils.getDevMac(default_gateway).strip()
            macvenders = Macvenders()
            vendor = macvenders.select().where('mac', '=', repr(gateway_mac[slice(6)])).get_one('vendor')
            if vendor:
                vendor = vendor[0].rstrip()
            else:
                vendor = ''

        except IndexError as ex:
            loader.stop()
            Logging.error("Request couldn't complete")
            Logging.error("There are no default gateway yet")
        except requests.exceptions.ProxyError:
            loader.stop()
            Logging.success(f'Default Gateway MAC : {gateway_mac}')
            Logging.success(f'Default Gateway     : {default_gateway}')
        except requests.exceptions.ConnectionError:
            loader.stop()
            Logging.success(f'Default Gateway MAC : {gateway_mac}')
            Logging.success(f'Default Gateway     : {default_gateway}')
        except NoFound:
            loader.stop()
            Logging.success(f'Default Gateway MAC : {gateway_mac}')
            Logging.success(f'Default Gateway     : {default_gateway}')
        except Exception as ex:
            loader.stop()
            # print(ex)
            # print(type(ex))
            Logging.error(str(ex))
        else:
            loader.stop()
            Logging.success(f'Default Gateway MAC : {gateway_mac}\t{vendor}')
            Logging.success(f'Default Gateway     : {default_gateway}')
        print('\n')
        try:
            while input("Press Enter to Back"):
                break
        except KeyboardInterrupt:
            pass

    @staticmethod
    def modechanger():
        try:
            devip = Utils.ip_in()
            uname = "admin"
            dev_mac = Utils.getDevMac(devip)
            pwd = dev_mac
            while True:
                Utils.banner()
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
        except Exception:
            pass

    @staticmethod
    def mtu_checker():
        Utils.banner()
        print('Find Perfect MTU Value')
        print('----------------------')
        print('')
        loader = Loader('Please wait ')
        loader.start()
        try:
            host = '8.8.8.8'
            if os.name == 'nt':
                res = os.system(f"ping  -n 1 {host} > NUL")
            else:
                res = os.system(f"ping  -c 1  {host}>/dev/null 2>&1")

            if res == 1:
                raise NoConnectionException("No internet connection")

            host = '8.8.8.8'
            base_mtu = 1200
            increment = 200

            while True:
                if base_mtu >= 1600:
                    raise Exception("Something went wrong")
                base_mtu += increment
                if os.name == 'nt':
                    res = os.system(f"ping -f -n 1 -l {str(base_mtu)} {host} > NUL")
                else:
                    res = os.system(f"ping -c 1 -M do -s  {str(base_mtu)}  {host}>/dev/null 2>&1")
                time.sleep(1)
                if res == 0:
                    continue
                else:

                    base_mtu -= increment
                    increment = round(increment / 2)
                    if increment < 1:
                        break



        except NoConnectionException as ex:
            loader.stop('e', "Process couldn't complete")
            Logging.error(str(ex))

        except Exception as ex:
            loader.stop('e', "Process couldn't complete")
            Logging.error("Something went wrong")
            # print(ex)
            # print(type(ex))

        else:
            loader.stop('s', f"Best MTU {base_mtu + 28}")
            print('\n')
        try:
            while input("Press Enter to Back"):
                break
        except KeyboardInterrupt:
            pass

    @staticmethod
    def get_pub_ip():
        Utils.banner()
        print('Public IP Address & Information')
        print('-------------------------------')
        print('')
        loader = Loader('Please wait ')
        loader.start()
        try:
            api_server = 'http://ip-api.com/json/'
            result = Utils.req(method='get', url=api_server).json()

        except requests.exceptions.ConnectionError as ex:
            loader.stop()
            Logging.error("Process couldn't complete")
            Logging.error("Please check you internet connection")
        except Exception as ex:
            loader.stop()
            Logging.error("Process couldn't complete")
            Logging.error("Something went wrong")
            # print(ex)
            # print(type(ex))
        else:
            loader.stop()
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

        print('\n')
        try:
            while input("Press Enter to Back"):
                break
        except KeyboardInterrupt:
            pass

    @staticmethod
    def speedtest():
        Utils.banner()
        print('Speed Test')
        print('----------')
        try:

            loader = Loader('Downloading  ')
            loader.start()
            sp = speedtest.Speedtest()
            download = sp.download()
            loader.stop('s', f'Download {download / 1048576:.2f} Mbps')
            loader = Loader("Uploading ")
            loader.start()
            upload = sp.upload()
            loader.stop('s', f'Upload {upload / 1048576:.2f} Mbps')
            loader = Loader("Result ")
            loader.start()
            result = sp.results

        except speedtest.ConfigRetrievalError:
            loader.stop('e', "Process couldn't complete")
            Logging.error("Please check you internet connection")

        except Exception as ex:
            loader.stop('e', "Process couldn't complete")
            Logging.error("Something went wrong")
            # print(ex)
            # print(type(ex))
        else:
            loader.stop('s', f"Server : {result.server['sponsor']} {result.server['name']} {result.server['country']}")
            Logging.success(f"Latency : {result.ping:.0f} ms")
            print('')
            Logging.success(f"IP : {result.client['ip']}")
            Logging.success(f"ISP : {result.client['isp']}")
        finally:
            print('\n')
            try:
                while input("Press Enter to Back"):
                    break
            except KeyboardInterrupt:
                pass

    @staticmethod
    def port_checker():
        pattern = re.compile(r'(\b25[0-5]|\b2[0-4]\d|\b[01]?\d\d?)(\.(25[0-5]|2[0-4]\d|[01]?\d\d?)){3}')
        port_pattern = re.compile(
            r'^((6553[0-5])|(655[0-2]\d)|(65[0-4]\d{2})|(6[0-4]\d{3})|([1-5]\d{4})|([0-5]{0,5})|(\d{1,4}))$')
        # domain_pattern = re.compile(r'^(([a-z\d]\-*[a-z\d]*){1,63}\.?){1,255}$')
        try:
            Utils.banner()
            while True:

                ip_and_port = str(input("Enter remote address:port : "))

                if not ip_and_port or ':' not in ip_and_port:
                    Logging.error('Please provide a destination ip and port correct format')
                    Logging.error('Example : 127.0.0.1:8080')
                    continue
                else:
                    dst_ip = ip_and_port.split(':')[0]
                    dst_port = ip_and_port.split(':')[1]

                    if not port_pattern.search(dst_port):
                        Logging.error('Invalid port number')
                        continue
                try:
                    loader = Loader("Please wait ")
                    loader.start()
                    s = socket.socket()
                    s.settimeout(5)
                    s.connect((dst_ip, int(dst_port)))
                    src_ip, src_port = s.getsockname()
                    rmt_ip, rmt_port = s.getpeername()
                    s.close()
                except TimeoutError:
                    loader.stop('e', f"Port {dst_port} is closed")
                    continue
                except ConnectionRefusedError:
                    loader.stop('e', f"Port {dst_port} is closed")
                except socket.gaierror:
                    loader.stop('e', "Invalid remote address")
                except Exception as ex:
                    # print(ex)
                    # print(type(ex))
                    loader.stop('e', "Process couldn't complete")
                    loader.stop('e', "Something went wrong")
                else:
                    loader.stop('s', f"Port {rmt_port} is open")
                    Logging.success(f"Source address  : {src_ip}")
                    Logging.success(f"Remote address  : {rmt_ip} {dst_ip if not pattern.search(dst_ip) else ''} ")

                print('')
                if str(input("Press any key for try again or [0] Back  : ")) == "0":
                    break
                else:
                    continue
        except KeyboardInterrupt:
            pass

    @staticmethod
    def mac_vendor_lookup():
        while True:
            Utils.banner()
            print('MAC Vendor Lookup')
            print('-----------------')
            print('')
            try:

                while True:
                    hex_re = re.compile(r'(?:[0-9a-fA-F]:?){6,12}')
                    cols = get_terminal_size((80, 20)).columns
                    mac = input("Enter MAC : ")
                    if ":" in mac:
                        mac = mac.replace(':', '')
                    elif '.' in mac:
                        mac = mac.replace('.', '')

                    if not len(mac) >= 6:
                        Logging.error('please provide minimum 6 characters')
                    elif not hex_re.search(mac):
                        Logging.error('Please provide a valid mac address')
                    else:
                        break

                loader = Loader('Please wait ')
                loader.start()

                mac = mac[0:6].upper()
                macvenders = Macvenders()
                vendor = macvenders.select().where('mac', 'LIKE', repr(mac)).get_one('vendor')
                del macvenders

                if vendor:
                    vendor = vendor[0].rstrip()
                else:
                    vendor = "Couldn't find vendor"

                loader.stop()
            except requests.exceptions.ProxyError:
                loader.stop('e', "Request couldn't complete")
            except requests.exceptions.ConnectionError as ex:
                loader.stop('e', "Please check your internet connection")
            except NoFound as ex:
                loader.stop('e', "Something went wrong")
            except Exception as ex:
                loader.stop('e', str(ex))
                # print(ex)
                # print(type(ex))
            else:
                loader.stop('s', f'{vendor}')
                # Logging.success()
            print('\n')
            try:
                if str(input("Press enter for try again or [0] Back")) == "0":
                    break
                else:
                    continue
            except KeyboardInterrupt:
                pass


class Manu():

    @staticmethod
    def main_manu():

        manu_args = {
            '0': 'exit(0)',
            '1': f'Module.getGatewayMac()',
            '2': f'Module.get_pub_ip()',
            '3': f'Module.modechanger()',
            '4': f'Module.mtu_checker()',
            '5': f'Module.speedtest()',
            '6': f'Module.port_checker()',
            '7': f'Module.mac_vendor_lookup()'
        }
        try:
            while True:
                try:
                    Utils.banner()
                    print('Main Manu')
                    print('---------')
                    print('')
                    print('''
[1] Display Gateway info    - Display gateway mac and ip address     
[2] What is my ip           - Display your public address
[3] Mode changer            - Genexis Platinum 4410 Pon Mode Change
[4] MTU Checker             - Find Perfect MTU Value 
[5] Speedtest               - Speedtest powerded by ookla
[6] Port Checker            - TCP Port checker
[7] MAC Vendor Lookup       - Mac address vendor lookup
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
                    # print(ex)
                    # print(type(ex))
                    Logging.error("Invalid Option. Please Choose a correct option")
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    Manu.main_manu()
