#encoding: utf-8
import os
import qis
import sys
import time
import ctypes
import shutil
import psutil
import common
import win32api
import selenium
import threading
import subprocess
from time import sleep
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import listdir
from os.path import isfile, isdir, join
from datetime import datetime
from multiprocessing import Process
from signal import signal
from signal import SIGTERM

'''
import telnetlib
import getpass
import re
import itertools as it
'''

qis_info = { 'http_username':'',
'http_password':'',
'ppp_username':'',
'ppp_password':'',
'staticip_dut_wan_ip':'',
'staticip_wan_server_ip':'',
'staticip_netmask':'',
'staticip_gateway':'',
'smart_connect_ssid':'',
'ssid_2g':'',
'ssid_5g':'',
'ssid_5g_2':'',
'ssid_6g':'',
'wifi_key':'',
}

version = "1.0.0.14"
location = "Taipei"
chariot_pair_no= "10"
dut_ip = "192.168.50.1"
http_username = "admin"
http_password = "asus#1234"
ppp_username = "asus"
ppp_password = "asus#1234"
fw_version = ""
dut_wan_ip = "192.168.2.10"
wan_1_dut_wan_ip = "192.168.2.10"
wan_pc_1_wan_server_ip = "192.168.101.11"
wan_pc_1_netmask = "255.255.255.0"
wan_pc_1_gateway = "192.168.101.11"
wan_pc_1_ppp_server_ip = '101.0.0.11'
wan_2_dut_wan_ip = "192.168.2.10"
wan_pc_2_wan_server_ip = "192.168.102.12"
wan_pc_2_netmask = "255.255.255.0"
wan_pc_2_gateway = "192.168.102.12"
wan_pc_2_ppp_server_ip = '102.0.0.11'
wan_3_dut_wan_ip = "192.168.2.10"
wan_pc_3_wan_server_ip = "192.168.103.13"
wan_pc_3_netmask = "255.255.255.0"
wan_pc_3_gateway = "192.168.103.13"
wan_pc_3_ppp_server_ip = '103.0.0.11'

all_port_no = 5
UI_lan_port_list = []
UI_wan_port_list = []
test_lan_port_list = []
connect_dict = {}
wan_type_list = ["","Static IP","PPPoE","PPTP","L2TP"]
#wan_type_list = ["","Static IP","PPPoE","","L2TP"]
function_list = ['Default','AiProtection','Adaptive_QoS','Traditional_QoS']
#function_list = ['Default','','','']
function = 'Default'
UI_start = 0
model_name = ''
test_time = '1'
run_chariot = '1'
specify_lan_port_test = 0
cur_directory = 'D:\Multi-port_V5'
#config_path = 'D:\Multi-port\Config'
TPT = []
now_time = ''
log_file = ''
result_file = ''
run_qis = 0
ping_lan_client_fail = 0
autorun_path = '\\autorun.txt'
sync_report = 0
asus_token="YWRtaW46YXN1cyMxMjM0"

#driver = webdriver.Chrome()
#http://router.asus.com/QIS_wizard.htm?flag=welcome
#dut_url = "http://www.asusrouter.com/"
dut_url = "http://192.168.50.1/"
qis_url = dut_url + "QIS_wizard.htm"
index_url = dut_url+"index.asp"
adv_wan_url = dut_url+ "Advanced_WAN_Content.asp"
adv_wan_port_url =  dut_url+ "Advanced_WANPort_Content.asp"
adv_sys_url =  dut_url+ "Advanced_System_Content.asp"
adv_fw_url =  dut_url+ "Advanced_FirmwareUpgrade_Content.asp"
analysis_url =  dut_url+ "Main_Analysis_Content.asp"
aiportection_url =  dut_url+ "AiProtection_HomeProtection.asp"
qos_url =dut_url+ "QoS_EZQoS.asp"
reset_default_url =  dut_url+ "Advanced_SettingBackup_Content.asp"
disable_redirect_url =  dut_url+ "Main_Login.asp?redirect=false"


def print_msg(msg):
    print(msg)
    l_file = open(log_file, "a")
    l_file.write(msg)
    l_file.write('\n')
    l_file.close()


def Get_Key_From_Value(d, val):
    #print('%s, %s' %(d, val))
    for key, value in d.items():
        #print('%s, %s' %(key, value))
        if value.upper().replace(' ','_').replace('-','_') == val.upper().replace(' ','_').replace('-','_'):
            return key


def Ping(address, retry, success):
    #print('ping ' + address + '=')
    #return True
    i = 0
    ok = 0
    if len(address) == 0:
        msg = 'No IP, stop ping\n'
        print_msg(msg)
    else:
        cmd = 'ping -n 1 ' + address
        print_msg(cmd)
        while (i < retry):
            try:
                output = subprocess.check_output(cmd)
                #print(output)
                if b'TTL=' in output:
                    ok += 1
                    msg="PING OK"
                    #print_msg(msg)
                else:
                    msg="FAIL"
                    print_msg(msg)
                if ok == success:
                    msg="Ping Success"
                    print_msg(msg)
                    return True
            except subprocess.CalledProcessError as e:
                code = e.returncode
                msg="Ping Error! Re-send again. [ERROR NO]: " + str(code)
                print_msg(msg)
            i += 1
            time.sleep(1)

    return False


def Ping_Lan_Client(client):
    return True
    global ping_lan_client_fail
    
    msg = 'Ping_Lan_Client - %s\n'%(client)
    print_msg(msg)
        
    client_ip = "192.168.50.11"
    if client == "LAN_PC_11":
        client_ip = "192.168.50.11"
    if client == "LAN_PC_12":
        client_ip = "192.168.50.12"
    if client == "LAN_PC_13":
        client_ip = "192.168.50.13"
    if client == "LAN_PC_14":
        client_ip = "192.168.50.14"
    if client == "WAN_PC_101":
        client_ip = "192.168.50.101"
    if client == "WAN_PC_102":
        client_ip = "192.168.50.102"
    if client == "WAN_PC_103":
        client_ip = "192.168.50.103"

    if client == "ALL_LAN":
        if ping_lan_client_fail:
            return False
        else:
            return True
        
    if Ping(client_ip, 30, 3):
        return True
    else:
        ping_lan_client_fail = 1
        return False


        
def query_chrome_driver_version():
    cmd = 'ChromeDriver -V'
    stdout, stderr = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True).communicate()
    stdoutput = stdout.decode()
    return stdoutput.split(' ')[1]

		
def browser_driver_version_check():
    chrome_driver_version = query_chrome_driver_version()
    print('Chrome driver version : << {} >>'.format(chrome_driver_version))

    try:
        browser = webdriver.Chrome()
    except selenium.common.exceptions.SessionNotCreatedException as e:
        err_msg = e.msg.split('\n')[1]
        print_msg(err_msg)
        version = e.msg.split('\n')[1].split('with')[0]
        print_msg(version)
        return version
    try:
        msg='Browser version : '+ browser.capabilities['version']
        print(msg)
    except KeyError:
        msg='Browser version : ' + browser.capabilities['browserVersion']
        print(msg)
        browser.quit()

    return 'OK'


def Update_Run_Qis(fun_qis, i):
    global run_qis
    
    if fun_qis.isChecked():
        run_qis = 1
    else:
        run_qis = 0
        
    print("qis= " + str(run_qis))
    
    
def Update_Function_List(fun_cb, i):
    global model_name
    global function_list
    global wan_type_list
    
    if fun_cb.isChecked():
        function_list[i] = fun_cb.text()
    else:
        function_list[i] = ''
        
    print(function_list)


def Update_Wantype_List(wantype, i):
    global model_name
    global function_list
    global wan_type_list
    
    if wantype.isChecked():
        wan_type_list[i] = wantype.text()
        '''
        if wantype.text() == "Dynamic IP":
            wan_type_list[i] = "DYNAMICIP"
        if wantype.text() == "Static IP":
            wan_type_list[i] = "STATICIP"
        if wantype.text() == "PPPoE":
            wan_type_list[i] = "PPPOE"
        '''
    else:
        wan_type_list[i] = ''
        
    print(wan_type_list)
    
    
class MyWidget(QtWidgets.QWidget):
    global UI_start
    global model_name
    global chariot_pair
    global function_list
    global wan_type_list
    
    def __init__(self):
        super().__init__()
        '''
                #Chrome driver check
        if chrome_chk_ret != 'OK':
            #self.btn.setDisabled(True)
            
            self.mbox = QtWidgets.QMessageBox(self)
            warn_msg = chrome_chk_ret + '\nPlease go to \"https://chromedriver.chromium.org/\" & download new chromedriver.'
            self.mbox.information(self, 'info', warn_msg)
        else:
        '''
        self.setWindowTitle('Multi-port NAT Test %s'%(version))
        self.resize(470, 270)
        self.setUpdatesEnabled(True)
        self.ui()

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 128) 

    def ui(self):     

        # model name content
        self.label1 = QtWidgets.QLabel(self)
        self.label1.setText('Model:')
        self.label1.move(30, 20)
        self.box1 = QtWidgets.QComboBox(self)
        files = listdir(config_path)
        for f in files:
            fullpath = join(config_path, f)
            if isdir(fullpath):
                self.box1.addItem(f)
        self.box1.setGeometry(30, 48, 148, 25)

        # Chariot pair
        self.label2 = QtWidgets.QLabel(self)
        self.label2.setText('Cahriot pair:')
        self.label2.move(30, 80)
        self.box2 = QtWidgets.QComboBox(self)
        files = listdir(chariot_pair_path)
        for f in files:
            pairpath = join(chariot_pair_path, f)
            if isdir(pairpath):
                self.box2.addItem(f)
        self.box2.move(110, 80)

        #test time
        self.label3 = QtWidgets.QLabel(self)
        self.label3.setText('Run Chariot:')
        self.label3.move(30, 110)

        self.box3 = QtWidgets.QComboBox(self)
        for t in range(1,4,1):
            st = str(t)
            self.box3.addItem(str(t))
        self.box3.move(145, 110)

        #repeat time
        self.label4 = QtWidgets.QLabel(self)
        self.label4.setText('Repeat:')
        self.label4.move(30, 140)

        self.box4 = QtWidgets.QComboBox(self)
        for t in range(1,4,1):
            self.box4.addItem(str(t))
        self.box4.move(145, 140)

        #Run QIS
        self.fun_q = QtWidgets.QCheckBox(self)
        self.fun_q.move(30, 170)
        self.fun_q.setText('Run QIS')
        self.fun_q.setEnabled(False)
        self.fun_q.clicked.connect(lambda:Update_Run_Qis(self.fun_q, 0))

        #Specify LAN
        self.fun_hw = QtWidgets.QCheckBox(self)
        self.fun_hw.move(30, 200)
        self.fun_hw.setText('Specify LAN port test')
        self.fun_hw.setChecked(False)
        self.fun_hw.clicked.connect(self.Update_HW_Require)

        
        # function content
        self.label2 = QtWidgets.QLabel(self)
        self.label2.setText('Enable Function:')
        self.label2.move(210, 20)
        
        self.fun_a = QtWidgets.QCheckBox(self)
        self.fun_a.move(210, 50)
        self.fun_a.setText('Default')
        self.fun_a.setChecked(True)
        self.fun_a.clicked.connect(lambda:Update_Function_List(self.fun_a, 0))

        self.fun_b = QtWidgets.QCheckBox(self)
        self.fun_b.move(210, 80)
        self.fun_b.setText('AiProtection')
        self.fun_b.setChecked(True)
        self.fun_b.clicked.connect(lambda:Update_Function_List(self.fun_b, 1))
        
        self.fun_c = QtWidgets.QCheckBox(self)
        self.fun_c.move(210, 110)
        self.fun_c.setText('Adaptive_QoS')
        self.fun_c.setChecked(True)
        self.fun_c.clicked.connect(lambda:Update_Function_List(self.fun_c, 2))
        
        self.fun_d = QtWidgets.QCheckBox(self)
        self.fun_d.move(210, 140)
        self.fun_d.setText('Traditional_QoS')
        self.fun_d.setChecked(True)
        self.fun_d.clicked.connect(lambda:Update_Function_List(self.fun_d, 3))
        
        # wan type content
        self.label3 = QtWidgets.QLabel(self)
        self.label3.setText('Wan Type:')
        self.label3.move(350, 20)
        
        self.wantype_a = QtWidgets.QCheckBox(self)
        self.wantype_a.move(350, 50)
        self.wantype_a.setText('Automatic IP')
        #self.wantype_a.setChecked(True)
        self.wantype_a.clicked.connect(lambda:Update_Wantype_List(self.wantype_a, 0))
        
        self.wantype_b = QtWidgets.QCheckBox(self)
        self.wantype_b.move(350, 80)
        self.wantype_b.setText('Static IP')
        self.wantype_b.setChecked(True)
        self.wantype_b.clicked.connect(lambda:Update_Wantype_List(self.wantype_b, 1))
        
        self.wantype_c = QtWidgets.QCheckBox(self)
        self.wantype_c.move(350, 110)
        self.wantype_c.setText('PPPoE')
        self.wantype_c.setChecked(True)
        self.wantype_c.clicked.connect(lambda:Update_Wantype_List(self.wantype_c, 2))
        
        self.wantype_d = QtWidgets.QCheckBox(self)
        self.wantype_d.move(350, 140)
        self.wantype_d.setText('PPTP')
        self.wantype_d.setChecked(True)
        self.wantype_d.clicked.connect(lambda:Update_Wantype_List(self.wantype_d, 3))

        self.wantype_e = QtWidgets.QCheckBox(self)
        self.wantype_e.move(350, 170)
        self.wantype_e.setText('L2TP')
        self.wantype_e.setChecked(True)
        self.wantype_e.clicked.connect(lambda:Update_Wantype_List(self.wantype_e, 4))
        
        #start button
        self.btn = QtWidgets.QPushButton(self)
        self.btn.setText('Start')
        self.btn.move(350,230)
        self.btn.clicked.connect(self.ShowBtn)

    def ShowBtn(self):
        global UI_start
        self.btn.setDisabled(True)
        QApplication.processEvents()
        UI_start = 1
        Start_Test()
        self.btn.setDisabled(False)

    
    def Update_HW_Require(self):
        global specify_lan_port_test
        
        if self.fun_hw.isChecked():
            specify_lan_port_test = 1
            
            self.fun_b.setChecked(False)
            self.fun_c.setChecked(False)
            self.fun_d.setChecked(False)
        else:
            specify_lan_port_test = 0
            self.fun_b.setChecked(True)
            self.fun_c.setChecked(True)
            self.fun_d.setChecked(True)

        
def Run_Chariot(script_path):
    msg = 'Run: ' + script_path
    print_msg(msg)
    ret_tpt = 'N/A'
    #return 800

    chariot_path = cur_directory + "\\Chariot"
    os.chdir(chariot_path)
    try:
        os.remove("Chariot_RESULT.tst")
    except:
        msg = "No Chariot_RESULT.tst"
        print_msg(msg)
    try:
        os.remove("Chariot_RESULT.txt")
    except:
        msg = "No Chariot_RESULT.txt"
        print_msg(msg)
    '''
    try:
        os.remove("runtst.log")
    except:
        msg = "No runtst.log"
        print_msg(msg)
    '''

    for retry in range(3):
        print(">>> Run_Chariot Go: %d"%(retry))
        # create  thread
        print_msg("Fork Run_Tst_Thread")
        t1 = threading.Thread(target=Run_Tst_Thread, args=(script_path,))

        print_msg("Fork Check_Runtst_Thread")
        t2 = threading.Thread(target=Check_Runtst_Thread, args=())
        #print_msg("t1 start")
        t1.start()
        #print_msg("t2 start")
        t2.start()
        #print_msg("t1 join")
        t1.join()
        #print_msg("t2 join")
        t2.join()
        
        if not os.path.isfile('Chariot_RESULT.tst'):
            msg = '[Fail] runtst ' + script_path + ' Chariot_RESULT.tst'
            print_msg(msg)
            print_msg("Chariot_RESULT.TST Error!")
            continue
        str = os.popen('fmttst Chariot_RESULT.tst Chariot_RESULT.txt -c -q').read()
        if not os.path.isfile('Chariot_RESULT.txt'):
            msg = '[Fail] fmttst Chariot_RESULT.tst Chariot_RESULT.txt -c -q'
            print_msg(msg)
            print_msg("Chariot_RESULT.TXT Error!")
            continue
        
        file = open('Chariot_RESULT.txt', 'r')
        ret_str = file.read()
        file.close()

        ret_str = ret_str[:ret_str.find('TRANSACTION RATE')]
        ret_str = ret_str[ret_str.find('Totals:') + 7:].strip()
        #print('ret_str:')
        #print(ret_str +"\n")
        ret_str = ret_str.split(' ')[0].strip()
        ret_str = ret_str.replace(',', '')
        
        if 'SUMMARY' in ret_str:
            msg = "Run Charoit Error, try again."
            print_msg(msg)
        else:
            ret_tpt =  ret_str
            msg = 'ret_tpt: ' + ret_str
            print_msg(msg)
            break

    print("Finish Run_Chariot.")
        
    os.chdir(cur_directory)
    sleep(5)
    
    return ret_tpt


def Run_Tst_Thread(script_path):
    print_msg(">>> Run_Tst_Thread: call popen to runtst.")
    cmd = 'runtst ' + script_path + ' Chariot_RESULT.tst'
    print_msg(cmd)
    str = os.popen(cmd).read()
    print(">>> Run_Tst_Thread: runtst stoped.")
    

def Check_Runtst_Thread():
    leave = 0
    check_time = 0
    find_runtst = 0
    print_msg(">>> Check_Runtst_Task: wait 2 min & kill runtst.exe.")

    while 1:
        sleep(5)
        check_time += 1
        find_runtst = 0
        for proc in psutil.process_iter():
        # check whether the process name matches
            if proc.name() == "runtst.exe":
                find_runtst = 1
                print('check time: %d, runtst.exe is working...'%(check_time*5))
                if check_time * 5 == 120:
                    print_msg('>>> Check_Runtst_Task: runtst.exe is working for 2 min!')
                    proc.kill()
                    print_msg(">>> Check_Runtst_Task: Find & kill runtst.exe!")
                    leave = 1
                    
        if leave == 1 or find_runtst == 0:
            print_msg('>>> Check_Runtst_Task: Check_Runtst_Thread LEAVE')
            break
        
    
def Run_Chariot_Avg(script_path):
    ret = ''
    na = 0
    tpt = 0
    tpt_sum = 0
    test = 0
    
    msg = "Run_Chariot_Avg: run_chariot = " +run_chariot
    print_msg(msg) 
    while test < int(run_chariot):   
        ret = Run_Chariot(script_path)
        if ret == 'N/A':
          na += 1  
        else:
            tpt = float(ret)
            tpt_sum = tpt_sum + tpt
            
        test += 1

    if na == int(run_chariot):
        msg = "Run_Chariot_Avg: N/A"
        print_msg(msg)
        ret = 'N/A'
    else:
        tpt_avg = tpt_sum/(test - na)
        ret = '%.3f'%(tpt_avg)
        msg = "Run_Chariot_Avg: test= %d, na= %d, tpt_avg= %s" %(test, na, tpt_avg)
        print_msg(msg)

    return ret


def Run_Nat_Test(wan_type, current_wan_port, current_port_no):
    msg = "\nRun_Nat_Test: %s %s %d" %(wan_type, current_wan_port, current_port_no)
    print_msg(msg)
    global result_file
    #global TPT

    tpt_count = 0
    ping_dut = ',Pass'
    ping_wan = ',Pass'
    pc_to_wan = ',Pass'
    wan_server_ip = '192.168.101.101'
    TPT = ['N/A','N/A','N/A']

    wan_pc = Get_Key_From_Value(connect_dict, current_wan_port)
    print_msg(wan_pc)
    
    if current_port_no == 1:
        script_folder = "WAN_1"
        if "IP" in wan_type:
            wan_server_ip = wan_pc_1_wan_server_ip
        else:
            wan_server_ip = wan_pc_1_ppp_server_ip
    if current_port_no == 2:
        script_folder = "WAN_2"
        if "IP" in wan_type:
            wan_server_ip = wan_pc_2_wan_server_ip
        else:
            wan_server_ip = wan_pc_2_ppp_server_ip
    if current_port_no == 3:
        script_folder = "WAN_3"
        if "IP" in wan_type:
            wan_server_ip = wan_pc_3_wan_server_ip
        else:
            wan_server_ip = wan_pc_3_ppp_server_ip

    if not Ping(dut_ip, 60, 5):
        ping_dut = ',Fail'
        msg = 'Can not ping DUT - %s'%(dut_ip)
        print_msg(msg)
        return

    msg = "script_folder = %s" %(script_folder)
    print_msg(msg)

    ping_wan_retry = 0
    while(1):
        if DUT_Ping_Wan(driver, wan_server_ip):
            break
        
        if ping_wan_retry == 0:
            ping_wan_retry = 1
            print_msg("Ping WAN fail. Reboot DUT & try again.")
            common.Reboot_DUT(dut_ip, asus_token)
            sleep(180)
            continue
                
        ping_wan = ",Fail"
        msg = 'DUT can not ping WAN - %s'%(wan_server_ip)
        print_msg(msg)

    for retry in range(3):

        if not Ping(wan_server_ip, 60, 5):
            pc_to_wan = ',Fail'
            msg = 'Test PC can not ping DUT - %s, wait 1 min & retry = %d.'%(wan_server_ip, retry)
            print_msg(msg)
            sleep(60)
        else:
            pc_to_wan = ',Pass'
            break
        


    # Copy ALLLAN test case
    print_msg("Copy ALLLAN test case")
    wan_no = 0
    for wan_port in UI_wan_port_list:
        wan_no += 1
        wanfolder = wan_port.replace(" ", "_").replace("/","_")
        src_dir = cur_directory + '\\Config\\' + model_name + '\\all_lan_to_wan_' + chariot_pair + '\\' + wanfolder
        dst_wan_folder = "WAN_" + str(wan_no)
        dst_dir = cur_directory + '\\Chariot\\' + chariot_pair + '\\' + dst_wan_folder
        print_msg(src_dir)
        print_msg(dst_dir)
        
        files=os.listdir(src_dir)
        for fname in files:
            shutil.copy2(os.path.join(src_dir,fname), dst_dir)
    
    # Run WAN <-> LAN test case
    print_msg("Run WAN <-> LAN test case")
    lan_2p5g_no = 0
    lan_10g_no = 0
    lan_no = 0
    ch_lan_port = ''
    chariot_pair_no = chariot_pair.replace('_pair', '')

    for lan_port in test_lan_port_list:
        
        ret_file = open( result_file, 'a')
        print_msg("Run WAN <-> %s test case"%(lan_port))

        if "ALL_LAN" == lan_port:
            lan_pc = lan_port
        else:
            upper_lan_port = lan_port.upper().replace(' ','_').replace('-','_')
            lan_pc = Get_Key_From_Value(connect_dict, lan_port)

        print_msg("LAN_PC= %s" %(lan_pc))

        ret_file.write('Chariot,' + chariot_pair_no + ',' + version + ',' + model_name + ',' + fw_version + ',' + function + ',' + current_wan_port + ',' + lan_port + ',' + wan_type + ping_dut + ping_wan + pc_to_wan)

        if ping_dut == ',Fail' or ping_wan == ",Fail":
            ret_file.write(',N/A,N/A,N/A')
        else:
            if not Ping_Lan_Client(lan_pc):
                msg = 'Can not ping lan client - %s'%(lan_pc)
                print_msg(msg)
                ret_file.write(',Ping ' + lan_port + ' Fail!')
            else: 
                tpt_count = 0

                if "IP" in wan_type:
                    chariot_script_path = '.\\' + chariot_pair + '\\' + script_folder + '\\IP_' + lan_pc + '_TO_' + wan_pc +'.tst'
                    throughput = Run_Chariot_Avg(chariot_script_path)
                    print('throughput = %s\n'%(throughput))
                    TPT[tpt_count] = throughput
                    tpt_count += 1
                    chariot_script_path = '.\\' + chariot_pair + '\\' + script_folder + '\\IP_' + wan_pc +'_TO_' + lan_pc + '.tst'
                    throughput = Run_Chariot_Avg(chariot_script_path)
                    print('throughput = %s\n'%(throughput))
                    TPT[tpt_count] = throughput
                    tpt_count += 1
                    chariot_script_path = '.\\' + chariot_pair + '\\' + script_folder + '\\IP_' + lan_pc + '_' + wan_pc +'_BID.tst'
                    throughput = Run_Chariot_Avg(chariot_script_path)
                    print('throughput = %s\n'%(throughput))
                    TPT[tpt_count] = throughput
                    tpt_count += 1
                else:
                    chariot_script_path = '.\\' + chariot_pair + '\\' + script_folder + '\\PPP_' + lan_pc + '_TO_' + wan_pc +'.tst'
                    throughput = Run_Chariot_Avg(chariot_script_path)
                    print('throughput = %s\n'%(throughput))
                    TPT[tpt_count] = throughput
                    tpt_count += 1
                    chariot_script_path = '.\\' + chariot_pair + '\\' + script_folder + '\\PPP_' + wan_pc +'_TO_' + lan_pc + '.tst'
                    throughput = Run_Chariot_Avg(chariot_script_path)
                    print('throughput = %s\n'%(throughput))
                    TPT[tpt_count] = throughput
                    tpt_count += 1
                    chariot_script_path = '.\\' + chariot_pair + '\\' + script_folder + '\\PPP_' + lan_pc + '_' + wan_pc +'_BID.tst'
                    throughput = Run_Chariot_Avg(chariot_script_path)
                    print('throughput = %s\n'%(throughput))
                    TPT[tpt_count] = throughput
                    tpt_count += 1    
               
                for i in range(len(TPT)):
                    msg = "i= %d : %s" %(i,TPT[i])
                    print_msg(msg)
                    ret_file.write(',' + TPT[i])

        ret_file.write('\n')
        ret_file.close()
        
    # Run WAN <-> EXT WANLAN test case
    print_msg("Run WAN <-> EXT WANLAN test case")
    ext_wan_count = 0
    for ext_wan in UI_wan_port_list:
        ext_wan_count += 1

        msg = "Wan No ? Wan Count = %d ? %d" %(current_port_no, ext_wan_count)
        print_msg(msg)

        if ext_wan_count == current_port_no:
            print_msg("# wan_count == wan_no # Skip this case.")
            continue

        ext_wanlan_pc = Get_Key_From_Value(connect_dict, ext_wan)

        msg = "Run WAN <-> %s TEST" %(ext_wanlan_pc)
        print_msg(msg)
        ret_file = open( result_file, 'a')

        ret_file.write('Chariot,' + chariot_pair_no + ',' + version + ',' + model_name + ',' + fw_version + ',' + function + ',' + current_wan_port + ',' + ext_wan + ',' + wan_type + ping_dut + ping_wan + pc_to_wan)

        if ping_dut == ',Fail' or ping_wan == ",Fail":
            ret_file.write(',N/A,N/A,N/A')
        else:        
            if not Ping_Lan_Client(ext_wanlan_pc):
                msg = 'Can not ping lan client - %s'%(lan_port)
                print_msg(msg)
                ret_file.write(',Ping ' + lan_port + ' Fail!')
            else:
                
                tpt_count = 0
                if "IP" in wan_type:
                    chariot_script_path = '.\\' + chariot_pair + '\\' + script_folder + '\\IP_' + ext_wanlan_pc + '_TO_' + wan_pc +'.tst'
                    throughput = Run_Chariot_Avg(chariot_script_path)
                    print('throughput = %s\n'%(throughput))
                    TPT[tpt_count] = throughput
                    tpt_count += 1
                    chariot_script_path = '.\\' + chariot_pair + '\\' + script_folder + '\\IP_' + wan_pc +'_TO_' + ext_wanlan_pc + '.tst'
                    throughput = Run_Chariot_Avg(chariot_script_path)
                    print('throughput = %s\n'%(throughput))
                    TPT[tpt_count] = throughput
                    tpt_count += 1
                    chariot_script_path = '.\\' + chariot_pair + '\\' + script_folder + '\\IP_' + ext_wanlan_pc + '_' + wan_pc +'_BID.tst'
                    throughput = Run_Chariot_Avg(chariot_script_path)
                    print('throughput = %s\n'%(throughput))
                    TPT[tpt_count] = throughput
                    tpt_count += 1
                else:
                    chariot_script_path = '.\\' + chariot_pair + '\\' + script_folder + '\\PPP_' + ext_wanlan_pc + '_TO_' + wan_pc +'.tst'
                    throughput = Run_Chariot_Avg(chariot_script_path)
                    print('throughput = %s\n'%(throughput))
                    TPT[tpt_count] = throughput
                    tpt_count += 1
                    chariot_script_path = '.\\' + chariot_pair + '\\' + script_folder + '\\PPP_' + wan_pc +'_TO_' + ext_wanlan_pc + '.tst'
                    throughput = Run_Chariot_Avg(chariot_script_path)
                    print('throughput = %s\n'%(throughput))
                    TPT[tpt_count] = throughput
                    tpt_count += 1
                    chariot_script_path = '.\\' + chariot_pair + '\\' + script_folder + '\\PPP_' + ext_wanlan_pc + '_' + wan_pc +'_BID.tst'
                    throughput = Run_Chariot_Avg(chariot_script_path)
                    print('throughput = %s\n'%(throughput))
                    TPT[tpt_count] = throughput
                    tpt_count += 1    

                for i in range(len(TPT)):
                    msg = "i= %d : %s" %(i,TPT[i])
                    print_msg(msg)
                    ret_file.write(',' + TPT[i])

        ret_file.write('\n')
        
        ret_file.close()



def DUT_Ping_Wan(driver, wan_ip):
    msg = ("DUT_Ping_Wan: %s" %(wan_ip))
    print_msg(msg)
    #return True

    for i in range(5):
        try:
            driver.get(analysis_url)
            sleep(1)
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            sleep(30)

    driver.get(analysis_url)
    sleep(1)
    move = driver.find_element(By.TAG_NAME, 'body')
    move.send_keys(Keys.CONTROL + Keys.HOME)
    
    Try_Login(driver)
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print("Expert UI")
        driver.switch_to.frame(iframe)
        print("switch_to.frame")
    except:
        print("Normal/ROG UI")
        
    select = Select(driver.find_element("name", "cmdMethod"))
    try:
        select.select_by_value("ping")
    except:
        select.select_by_value("3")
    sleep(1)
    
    try:
        input1 = driver.find_element("xpath", "//*[@id=\"destIP\"]")
    except:
        input1 = driver.find_element("xpath", "//*[@name=\"destIP\"]")

    if input1:
        input1.clear()
        input1.send_keys(wan_ip)
        sleep(0.5)
        driver.find_element("xpath", "//*[@id=\"cmdBtn\"]").click()
        sleep(10)

        while(1):
            textarea = driver.find_element("xpath", "//*[@id=\"textarea\"]")
            #print("textarea= "+textarea.get_attribute("value"))
            if textarea.get_attribute("value") == "":
                #print("empty")
                sleep(5)
            else:
                break

        if "100% packet loss" in textarea.get_attribute("value"):
            print_msg("100% packet loss")
            print_msg("DUT ping WAN Fail.")
            return False
        else:
            print_msg("DUT ping WAN OK.")
            return True
    else:
        print_msg("Not find dest IP")


def Enable_EULA(dut_ip):
    msg = ('Enable_EULA')
    print_msg(msg)

    common.Get_Cookie(dut_ip, asus_token)
    command = "curl -A asusrouter-test-DUTUtil-111 -e " + dut_ip + " -b savecookie.txt -d \"{\\\"ASUS_privacy_policy\\\":\\\"1\\\"}\" http://" + dut_ip + "/set_ASUS_privacy_policy.cgi"
    result = common.Send_Curl_Command(command)
    if '200' in result:
        print("Got ASUS EULA")

    sleep(3)
    command = "curl -A asusrouter-test-DUTUtil-111 -e " + dut_ip + " -b savecookie.txt -d \"{\\\"TM_EULA\\\":\\\"1\\\"}\" http://" + dut_ip + "/set_TM_EULA.cgi"
    #print(command)
    result = common.Send_Curl_Command(command)
    #print(result)
    if '200' in result:
        print("Got TM EULA")



def Get_FW_Version(dut_ip, token):
    global fw_version
    msg = ("Get_FW_Version")
    print_msg(msg)
    
    fw_version = common.Get_Nvram(dut_ip, 'innerver', token)
    
    if fw_version == "":
        msg = ("No nvram: innerver. Try to combine fw_version.")
        print_msg(msg)
        firmver = common.Get_Nvram(dut_ip, 'firmver', token)
        buildno = common.Get_Nvram(dut_ip, 'buildno', token)
        extendno = common.Get_Nvram(dut_ip, 'extendno', token)
        fw_version = firmver +'.'+ buildno +'_'+ extendno
    
    print("FW VER=" + fw_version)

    

def Reset_Default(driver):
    print_msg("Reset_Default")
    
    for i in range(5):
        try:
            driver.get(reset_default_url)
            sleep(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open reset_default_url OK")
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            sleep(30)
    
    Try_Login(driver)
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print_msg("Expert UI")
        driver.switch_to.frame(iframe)
    except:
        print_msg("Normal/ROG UI")
        
    driver.find_element("xpath", "//input[@onclick=\"restoreRule('restore');\"]").click()  
    time.sleep(1)
    try:
        alert = driver.switch_to.alert    
        msg = ("alert:" + alert.text)
        print_msg(msg)
        alert.accept()
    except:
        print_msg("No alert")
    
    time.sleep(120)

        
def Disable_Redirect(driver):
    print("Disable_Redirect")

    for i in range(5):
        try:
            driver.get(disable_redirect_url)
            sleep(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open disable_redirect_url OK")
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            sleep(30)
            
    #sleep(1)
    #Try_Login(driver)
    #element1 = driver.find_element("xpath", "//*[@id=\"login_username\"]")
    
    try:
        element1 = driver.find_element("xpath", "//*[@id=\"login_username\"]")
        if element1:
            print_msg("Try to login")
            element1 = driver.find_element("xpath", "//*[@id=\"login_username\"]")
            element1.send_keys(http_username);
            element2 = driver.find_element("xpath", "//*[@name=\"login_passwd\"]")
            element2.send_keys(http_password);
            try:
                driver.find_element("xpath", "//div[@onclick=\"login();\"]").click()
            except:
                print_msg("Do not find login(); try to preLogin();")
                try:
                    driver.find_element("xpath", "//div[@onclick=\"preLogin();\"]").click()
                except:
                    print_msg("Can not find Login element!")
                
            sleep(3)
    except:
        print("Do not need login.")
        
    print("Disable OK")


    
def Enable_Telnet(driver):
    print_msg("Enable_Telnet")

    for i in range(5):
        try:
            driver.get(adv_sys_url)
            sleep(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open adv_sys_url OK")
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            sleep(30)
    
    Try_Login(driver)
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print_msg("Expert UI")
        driver.switch_to.frame(iframe)
    except:
        print_msg("Normal/ROG UI")
        
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print("Expert UI")
        driver.switch_to.frame(iframe)
        print("switch_to.frame")
    except:
        print("Normal/ROG UI")
        
    driver.find_element("xpath", "//*[@id=\"telnetd_sshd_table\"]/tbody/tr[1]/td/input[1]").click()
    driver.find_element("xpath", "//input[@onclick=\"applyRule();\"]").click()
    time.sleep(10)


def Enable_Aiportection(driver):
    print_msg("Enable_Aiportection.")
    for i in range(5):
        try:
            driver.get(aiportection_url)
            sleep(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open aiportection_url OK")
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            sleep(30)
    
    Try_Login(driver)
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print_msg("Expert UI")
        driver.switch_to.frame(iframe)
    except:
        print_msg("Normal/ROG UI")

    retry = 0
    while retry < 3:
        try:
            element = driver.find_element("xpath", "//*[@id=\"mals_shade\"]")
            style = element.get_attribute("style")
            print("------")
            print(style)
            print("------")
            break
        except:
            print_msg("Not find 'mals_shade', try again.")
            sleep(5)
            retry += 1

    if "none;" not in style:
        print("Try to click Enable")
        btn = driver.find_element("xpath", "//*[@id=\"iphone_switch\"]")
        btn.click()
        time.sleep(2)
        
        try:
            policy_model = driver.find_element("xpath", "//*[@id=\"policy_popup_modal\"]")
            print_msg("Find EULA field")
            sleep(1)
            policy_model2 = driver.find_element(By.CSS_SELECTOR, "div[class='modal-footer']")
            print_msg("Find footer")
            sleep(1)
            btn = policy_model.find_element(By.CSS_SELECTOR, ".btn.btn-primary.agree")
            print_msg("Find EULA BUTTON")
        except:
            print_msg("Not find EULA apply button.")
        print_msg("Enable_Aiportection done.")
    else:
        print("Already enable")
    


def Disable_Aiportection(driver):
    print_msg("Disable_Aiportection.")
    for i in range(5):
        try:
            driver.get(aiportection_url)
            sleep(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open aiportection_url OK")
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            sleep(30)
            
    Try_Login(driver)
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print_msg("Expert UI")
        driver.switch_to.frame(iframe)
    except:
        print_msg("Normal/ROG UI")
        
    retry = 0
    while retry < 3:
        try:
            element = driver.find_element("xpath", "//*[@id=\"mals_shade\"]")
            style = element.get_attribute("style")
            print("------")
            print(style)
            print("------")
            break
        except:
            print_msg("Not find 'mals_shade', try again.")
            sleep(5)
            retry += 1

    if "none" in style:
        driver.find_element("xpath", "//*[@id=\"iphone_switch\"]").click()      
        time.sleep(5)
        print_msg("Disable_Aiportection done.")
    

def Enable_QoS(driver, qos_type):
    msg = ("Enable_QoS: %s" %(qos_type))
    print_msg(msg)
    for i in range(5):
        try:
            driver.get(qos_url)
            sleep(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open qos_url OK")
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            sleep(30)
    
    Try_Login(driver)
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print_msg("Expert UI")
        driver.switch_to.frame(iframe)
    except:
        print_msg("Normal/ROG UI")

    # Check if QoS has been enabled or not. If enabled, don't click again.
    try:
        element = driver.find_element("xpath", "//*[@id=\"iphone_switch\"]")
        element.click()        
        time.sleep(3)
        print_msg("Click 'Enable QoS' to ON!")
    except:
        print_msg("Do not find QoS switch")

    if qos_type == "Adaptive_QoS":
        try:
            driver.find_element("xpath", "//*[@id=\"int_type\"]").click()
            time.sleep(3)

            try:
                btn = driver.find_element("xpath", "//*[@id=\"Web_act\"]")
                print_msg("\"Web accelerate\" has been enabled.")
            except:
                print_msg("pass")
                time.sleep(1)

            try:
                btn = driver.find_element("xpath", "//*[@id=\"Web\"]")
                btn.click()
                print_msg("Click \"Web accelerate\".")
                time.sleep(1)
            except:
                print_msg("Do not find @id=\"Web\"")
                

            try:
                driver.find_element("xpath", "//div[@onclick=\"submitQoS();\"]").click()
                time.sleep(1)
            except:
                print_msg("Do not find submitQoS()")

            time.sleep(30)
        except:
            msg = ("Do not find Adaptive_QoS button!")
            print_msg(msg)

    if qos_type == "Traditional_QoS":
        driver.find_element("xpath", "//*[@id=\"trad_type\"]").click()
        element = driver.find_element("xpath", "//*[@id=\"obw\"]")
        element.clear()
        element.send_keys("12000")
        element = driver.find_element("xpath", "//*[@id=\"ibw\"]")
        element.clear()
        element.send_keys("12000")
        sleep(1)
        driver.find_element("xpath", "//div[@onclick=\"submitQoS();\"]").click()
        try:
            alert = driver.switch_to.alert    
            msg = ("alert:" + alert.text)
            print_msg(msg)
            alert.accept()
        except:
            print_msg("No alert")
        time.sleep(120)

    msg = ("Enable_QoS: %s done." %(qos_type))
    print_msg(msg)

 
def Disable_QoS(driver):
    for i in range(5):
        try:
            driver.get(qos_url)
            sleep(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open qos_url OK")
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            sleep(30)

    Try_Login(driver)
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print_msg("Expert UI")
        driver.switch_to.frame(iframe)
    except:
        print_msg("Normal/ROG UI")
    try:
        element = driver.find_element("xpath", "//*[@id=\"int_type\"]")
        time.sleep(1)
        msg = ("QoS had been enabled!")
        print_msg(msg)
        element = driver.find_element("xpath", "//*[@id=\"iphone_switch\"]")
        element.click()
        time.sleep(1)
        driver.find_element("xpath", "//div[@onclick=\"submitQoS();\"]").click()
        time.sleep(20)
        print_msg("Disable_QoS done.")
    except:
        print_msg("QoS already disabled.")


def Set_DNS(webdriver):
        #DNS setting
        try:    
            element = webdriver.find_element("xpath", "//input[@onclick=\"Assign_DNS_service()\"]")
            element.click()
            sleep(0.5)
            print_msg("ROG UI")
            webdriver.find_element("xpath", "//*[@id=\"dns_manual\"]").click()
            element = webdriver.find_element("xpath", "//*[@id=\"edit_wan_dns1_x\"]")
            element.clear()
            # element.send_keys(wan_server_ip);
            element.send_keys("192.168.123.206");
            sleep(0.5)
            webdriver.find_element("xpath", "//input[@onclick=\"Update_DNS_service()\"]").click()
        except:
            print_msg("Normal UI")
            try:
                element = webdriver.find_element("xpath", "//input[@name=\"wan_dnsenable_x\" and @value=\"0\"]")
                element.click()
                sleep(0.5)
            except:
                print_msg("No wan_dnsenable_x radio")
            element = webdriver.find_element("xpath", "//input[@name=\"wan_dns1_x\"]")
            element.clear()
            # element.send_keys(wan_server_ip);
            element.send_keys("192.168.123.206");
            sleep(0.5)
        


def Get_Port_Info_From_File(dut_config_file):
    global UI_wan_port_list
    global UI_lan_port_list
    global test_lan_port_list
    
    print("Get_Port_Info_From_File: " + dut_config_file)
    f = open(dut_config_file)
    if f:
        lines = f.readlines()
        for line in lines:
            print(">"+line)
            strip_line = line.strip()
            print(">>>"+strip_line)
            if '=' not in strip_line:
                break
            var_split = strip_line.split('=')
            print("%s/%s/"%(var_split[0], var_split[1]))

            if "WAN_PC" in var_split[0] and var_split[1] != '':
                UI_wan_port_list.append(var_split[1])
                
            if "LAN_PC" in var_split[0] and var_split[1] != '':
                test_lan_port_list.append(var_split[1].upper().replace(' ','_').replace('-','_').replace('\n',''))
    
        print_msg("WAN PORT LIST:")
        for p in  UI_wan_port_list:
            print_msg(p)
        print_msg("LAN PORT LIST:")
        for p in  test_lan_port_list:
            print_msg(p)
        test_lan_port_list.append("ALL_LAN")
        return True
    else:
        return False
    
    
def Get_Dual_Wan_Port(driver, dut_config_file):
    global UI_wan_port_list
    global UI_lan_port_list
    global test_lan_port_list

    msg = ("> Get_Dual_Wan_Port <")
    print_msg(msg)

    if model_name == "BD4":
        UI_wan_port_list.append("WAN Auto Detection")
        test_lan_port_list.append("2.5G")
        print_msg("WAN PORT LIST:")
        for p in  UI_wan_port_list:
            print_msg(p)
        print_msg("LAN PORT LIST:")
        for p in  test_lan_port_list:
            print_msg(p)

        return
    
    for i in range(5):
        try:
            driver.get(adv_wan_port_url)
            sleep(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open adv_wan_port_url OK")
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            sleep(30)
    sleep(1)
    Try_Login(driver)

    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print_msg("Expert UI")
        driver.switch_to.frame(iframe)
    except:
        print_msg("Normal/ROG UI")

    try: #Find Second port to check enable Dual wan or not
        element = driver.find_element("name", "wans_second")
        if element.is_displayed():
            print_msg("See \'wans_second\', dual wan was enabled.")
        else:
            print_msg("Not see \'wans_second\', try enable dual wan.")
            #Enable Dual Wan
            element1 = driver.find_element("xpath", "//*[@id=\"ad_radio_dualwan_enable\"]")
            element1.click()
    except:
        print_msg("Not find \'wans_second\', try enable dual wan.")
        #Enable Dual Wan
        element1 = driver.find_element("xpath", "//*[@id=\"ad_radio_dualwan_enable\"]")
        element1.click()

    #Get Primary port
    select = Select(driver.find_element("name", "wans_primary"))
    sleep(1)
    ethernet_lan = 0
    for op in select.options:
        print(op.text)
        if op.text != "USB" and op.text != "Ethernet LAN" and op.text != "WAN Auto Detection":
            UI_wan_port_list.append(op.text)
        if op.text == "Ethernet LAN":
            ethernet_lan = 1

    if ethernet_lan: #Get LAN port info from UI
        print("Get LAN port info from UI")
        try: 
            select.select_by_visible_text(u"Ethernet LAN")
            sleep(0.5)
            select = Select(driver.find_element("name", "wans_lanport1"))
            sleep(1)
            for op in select.options:
                test_lan_port_list.append(op.text)
        except:
            print_msg("Can not select \"Ethernet LAN\"")

    else: #Get LAN port info from file
        print("Get LAN port info from file: " + dut_config_file)
        f = open(dut_config_file)
        lines = f.readlines()
        for line in lines:
            print(">"+line)
            strip_line = line.strip()
            print(">>>"+strip_line)
            if '=' not in strip_line:
                break
            var_split = strip_line.split('=')
            print("%s/%s/"%(var_split[0], var_split[1]))
                
            if "LAN_PC" in var_split[0] and var_split[1] != '':
                test_lan_port_list.append(var_split[1].upper().replace(' ','_').replace('-','_').replace('\n',''))

    print_msg("WAN PORT LIST:")
    for p in  UI_wan_port_list:
        print_msg(p)
    print_msg("LAN PORT LIST:")
    for p in  test_lan_port_list:
        print_msg(p)
    test_lan_port_list.append("ALL_LAN")
    
    #Click again to disable Dual Wan
    element1 = driver.find_element("xpath", "//*[@id=\"ad_radio_dualwan_enable\"]")
    element1.click()

    

def Set_Wan_Type(wan_type, wan_no):
    msg = ("Set_Wan_Type - TYPE= " +wan_type+ " WAN No.= "+str(wan_no))
    print_msg(msg)
    wan_server_ip = ""
    dut_wan_ip = ""
    netmask = ""
    gateway = ""
    ppp_server_ip = ""

    for i in range(5):
        try:
            driver.get(adv_wan_url)
            sleep(1)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            Try_Login(driver)
            break
        except:
            print_msg("Connection refuce, wait 30 sec & try ")
            sleep(30)

    print_msg("Check UI Ver.")
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print_msg("Expert UI")
        driver.switch_to.frame(iframe)
    except:
        print_msg("Normal/ROG UI")

    for i in range(5):
            
        try:
            select = Select(driver.find_element("name", "wan_proto"))
            sleep(1)
            break
        except:
            print_msg("Can not find select element: wan_proto")
            print_msg("Refresh, wait 15 sec & try again")
            driver.get(adv_wan_url)
            sleep(15)
        try:
            select.select_by_index(4)
            sleep(1)
            break
        except:
            print_msg("Can not select L2TP")
            print_msg("Refresh, wait 15 sec & try again")
            driver.get(adv_wan_url)
            sleep(15)

    if wan_no == 1:
        print_msg("WAN 1")
        dut_wan_ip = wan_1_dut_wan_ip
        wan_server_ip = wan_pc_1_wan_server_ip
        netmask = wan_pc_1_netmask
        gateway = wan_pc_1_gateway
        ppp_server_ip = wan_pc_1_ppp_server_ip

    if wan_no == 2:
        print_msg("WAN 2")
        dut_wan_ip = wan_2_dut_wan_ip
        wan_server_ip = wan_pc_2_wan_server_ip
        netmask = wan_pc_2_netmask
        gateway = wan_pc_2_gateway
        ppp_server_ip = wan_pc_2_ppp_server_ip

    if wan_no == 3:
        print_msg("WAN 3")
        dut_wan_ip = wan_3_dut_wan_ip
        wan_server_ip = wan_pc_3_wan_server_ip
        netmask = wan_pc_3_netmask
        gateway = wan_pc_3_gateway
        ppp_server_ip = wan_pc_3_ppp_server_ip

    msg = ("dut_wan_ip= "+dut_wan_ip)
    print_msg(msg)
    msg = ("wan_server_ip= "+wan_server_ip)
    print_msg(msg)
    msg = ("netmask= "+netmask)
    print_msg(msg)
    msg = ("ppp_server_ip= "+ppp_server_ip)
    print_msg(msg)
    
    if wan_type == "Automatic IP":
        print_msg(wan_type)
        select.select_by_index(0)
        sleep(1)
        #DNS setting
        try:    
            element = driver.find_element("xpath", "//input[@onclick=\"Assign_DNS_service()\"]")
            element.click()
            sleep(0.5)
            print_msg("Find Assign DNS button")
            driver.find_element("xpath", "//*[@id=\"dns_auto\"]").click()
            sleep(0.5)
            driver.find_element("xpath", "//input[@onclick=\"Update_DNS_service()\"]").click()
        except:
            print_msg("Normal DNS")
            element = driver.find_element("xpath", "//input[@name=\"wan_dnsenable_x\" and @value=\"0\"]")
            element.click()
            sleep(0.5)
            element = driver.find_element("xpath", "//input[@name=\"wan_dns1_x\"]")
            element.clear()
            element.send_keys(wan_server_ip);
        sleep(15)
        print_msg('Config WAN type = Automatic IP')
        
    if wan_type == "Static IP":
        print_msg(wan_type)
        select.select_by_index(1)
        sleep(2)
        #WAN IP setting
        try:
            element1 = driver.find_element("xpath", "//*[@id=\"wan_ipaddr_x\"]")
            element1.clear()
            element1.send_keys(dut_wan_ip);
        except:
            element1 = driver.find_element("xpath", "//input[@name=\"wan_ipaddr_x\"]")
            element1.clear()
            element1.send_keys(dut_wan_ip);            
        element2 = driver.find_element("xpath", "//input[@name=\"wan_netmask_x\"]") 
        element2.clear()
        element2.send_keys(netmask);
        try:
            element3 = driver.find_element("xpath", "//*[@id=\"wan_gateway_x\"]")
            element3.clear()
            element3.send_keys(gateway);
        except:
            element3 = driver.find_element("xpath", "//input[@name=\"wan_gateway_x\"]")
            element3.clear()
            element3.send_keys(gateway);
        sleep(1)    
        #DNS setting
        try:    
            element = driver.find_element("xpath", "//input[@onclick=\"Assign_DNS_service()\"]")
            element.click()
            print_msg("Find Assign DNS button")
            print_msg("sleep 3sec")
            sleep(3)
            
            manual_retry = 0
            while(1):
                try:
                    manual_btn = driver.find_element("xpath", "//*[@id=\"dns_manual\"]")
                    manual_btn.click()
                    print_msg("Find manual btn, break")
                    break
                except:
                    print_msg("can not find manual btn, try again")
                    manual_retry += 1
                    if manual_retry == 3:
                        print_msg("can not find manual btn 3 times, stop")
                        break
                
            sleep(1)
            print_msg("Click dns_manual")
            element = driver.find_element("xpath", "//*[@id=\"edit_wan_dns1_x\"]")
            element.clear()
            print_msg("Clean wan_dns1")
            sleep(1)
            element.send_keys("8.8.8.8");
            sleep(1)
            print_msg("key in 8.8.8.8")
            driver.find_element("xpath", "//input[@onclick=\"Update_DNS_service()\"]").click()
            print_msg("apply")
        except:
            print_msg("Normal DNS")
            try:
                element = driver.find_element("xpath", "//input[@name=\"wan_dnsenable_x\" and @value=\"0\"]")
                element.click()
                sleep(1)
            except:
                print_msg("No wan_dnsenable_x radio")
            element = driver.find_element("xpath", "//input[@name=\"wan_dns1_x\"]")
            element.clear()
            element.send_keys(wan_server_ip);
        sleep(15)
        print_msg('Config WAN type = Static IP')
        
    if wan_type == "PPPoE":
        print_msg(wan_type)
        select.select_by_index(2)
        sleep(1)
        print_msg('Config WAN type = PPPoE')
        #DNS setting
        try:    
            element = driver.find_element("xpath", "//input[@onclick=\"Assign_DNS_service()\"]")
            element.click()
            sleep(0.5)
            print_msg("Find Assign DNS button")
            driver.find_element("xpath", "//*[@id=\"dns_auto\"]").click()
            sleep(0.5)
            driver.find_element("xpath", "//input[@onclick=\"Update_DNS_service()\"]").click()
        except:
            print_msg("Nomal DNS")
            retry = 0
            while retry < 5:
                get_element = 0
                try: 
                    element = driver.find_element("xpath", "//input[@name=\"wan_dnsenable_x\" and @value=\"0\"]")
                    element.click()
                    sleep(0.5)
                    get_element += 1
                except:
                    print_msg("Not find wan_dnsenable_x")
                try:
                    element = driver.find_element("xpath", "//input[@name=\"wan_dns1_x\"]")
                    element.clear()
                    element.send_keys(wan_server_ip);
                    get_element += 1
                except:
                    print_msg("Not find wan_dns1_x")

                if get_element == 2:
                    print_msg("Config DNS OK.")
                    break
        sleep(15)

        #PPP username, password
        element1 = driver.find_element("xpath", "//input[@name=\"wan_pppoe_username\"]")
        element1.clear()
        element1.send_keys(ppp_username);
        element1 = driver.find_element("xpath", "//*[@id=\"wan_pppoe_passwd\"]")
        element1.clear()
        element1.send_keys(ppp_password);
        sleep(2)
        print_msg('Config WAN type = PPPoE')
        
    if wan_type == "PPTP" or wan_type == "L2TP":
        print_msg(wan_type)
        if wan_type == "PPTP":
            select.select_by_index(3)
            #print_msg('Config WAN type = PPTP')
        if wan_type == "L2TP":
            select.select_by_index(4)
            #print_msg('Config WAN type = L2TP')
        sleep(1)
        #WAN IP setting
        element = driver.find_element("xpath", "//input[@name=\"wan_dhcpenable_x\" and @value=\"0\"]")
        element.click()
        try:
            element1 = driver.find_element("xpath", "//*[@id=\"wan_ipaddr_x\"]")
            element1.clear()
            element1.send_keys(dut_wan_ip);
        except:
            element1 = driver.find_element("xpath", "//input[@name=\"wan_ipaddr_x\"]")
            element1.clear()
            element1.send_keys(dut_wan_ip);            
        element2 = driver.find_element("xpath", "//input[@name=\"wan_netmask_x\"]") 
        element2.clear()
        element2.send_keys(netmask);
        try:
            element3 = driver.find_element("xpath", "//*[@id=\"wan_gateway_x\"]")
            element3.clear()
            element3.send_keys(gateway);
        except:
            element3 = driver.find_element("xpath", "//input[@name=\"wan_gateway_x\"]")
            element3.clear()
            element3.send_keys(gateway);
        sleep(1)    
        #DNS setting
        try:    
            element = driver.find_element("xpath", "//input[@onclick=\"Assign_DNS_service()\"]")
            element.click()
            sleep(0.5)
            print_msg("Find Assign DNS button")
            driver.find_element("xpath", "//*[@id=\"dns_auto\"]").click()
            sleep(0.5)
            driver.find_element("xpath", "//input[@onclick=\"Update_DNS_service()\"]").click()
        except:
            print_msg("Normal DNS")
            retry = 0
            while retry < 5:
                get_element = 0
                try: 
                    element = driver.find_element("xpath", "//input[@name=\"wan_dnsenable_x\" and @value=\"0\"]")
                    element.click()
                    sleep(0.5)
                    get_element += 1
                except:
                    print_msg("Not find wan_dnsenable_x")
                try:
                    element = driver.find_element("xpath", "//input[@name=\"wan_dns1_x\"]")
                    element.clear()
                    element.send_keys(wan_server_ip);
                    get_element += 1
                except:
                    print_msg("Not find wan_dns1_x")

                if get_element == 2:
                    print_msg("Config DNS OK.")
                    break

        sleep(15)
        
        #PPP username, password
        element1 = driver.find_element("xpath", "//input[@name=\"wan_pppoe_username\"]")
        element1.clear()
        element1.send_keys(ppp_username);
        element1 = driver.find_element("xpath", "//*[@id=\"wan_pppoe_passwd\"]")
        element1.clear()
        element1.send_keys(ppp_password);
        element1 = driver.find_element("xpath", "//input[@name=\"wan_heartbeat_x\"]")
        element1.clear()
        element1.send_keys(wan_server_ip);
        sleep(2)
        print_msg('Config WAN type = ' + wan_type)

    apply_retry = 0
    while(1):
        try:
            btn = driver.find_element("xpath", "//input[@onclick=\"applyRule();\"]")
            print_msg("Find applyRule(); button")
            sleep(1)
            btn.click()
            print_msg("Click applyRule();")
            break
        except:
            print_msg('Cannot find "applyRule();" button. Try again.')
            apply_retry += 1
            sleep(3)
            
        if apply_retry == 3:
            print_msg('Retry 3 times. break.')
            break
        
    print_msg("Wait 30 sec for apply setting.\n")
    sleep(30)
    


def Set_Wan_Port(port):
    msg = ("\nSet_Wan_Port: " +port)
    print_msg(msg)
    
    for i in range(6):
        try:
            driver.get(adv_wan_port_url)
            sleep(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open adv_wan_port_url OK")            
            Try_Login(driver)
            
            try:
                iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
                print_msg("Expert UI")
                driver.switch_to.frame(iframe)
                print_msg("switch_to.frame")
            except:
                print_msg("Normal/ROG UI")

            try:
                select = Select(driver.find_element("name", "wans_primary"))
                sleep(1)
                print_msg("Find 'wans_primary'")
            except:
                print_msg("Can not find 'wans_primary' xpath retry")

            try:
                select.select_by_visible_text(port)
                sleep(1)
                print_msg("Select port OK")
            except:
                print_msg("select_by_visible_text Fail")

            try:
                driver.find_element("xpath", "//input[@onclick=\"applyRule()\"]").click()
                sleep(1)
                print_msg("applyRule OK")

                try:
                    alert = driver.switch_to.alert
                    print("alert:" + alert.text)
                    alert.accept()
                except:
                    print_msg("No alert")
                break                
            except:
                print_msg("applyRule Fail")
            
        except:
            print_msg("Connection refuce, wait 30 sec & try ")
            sleep(30)

    if i == 5:
        print_msg("Retry 5 times.")
        return False
        
    print_msg("Wait 240 for DUT reboot...")
    sleep(240)

    if not Ping(dut_ip, 300, 10):
        msg = 'Can not ping DUT - %s for 5 mins. Stop test'%(dut_ip)
        print_msg(msg)
    else:
        print_msg("ping 192.168.50.1 OK, keep test.")

    return True

    
    
def Try_Login(driver):
    print_msg("Try to login")
    try:
        element1 = driver.find_element("xpath", "//*[@id=\"login_username\"]")
        if element1:
            print_msg("Find login_username")
            element1 = driver.find_element("xpath", "//*[@id=\"login_username\"]")
            element1.send_keys(http_username);
            element2 = driver.find_element("xpath", "//*[@name=\"login_passwd\"]")
            element2.send_keys(http_password);
            try:
                driver.find_element("xpath", "//div[@onclick=\"login();\"]").click()
            except:
                print_msg("Do not find login(); try preLogin();")
                try:
                    driver.find_element("xpath", "//div[@onclick=\"preLogin();\"]").click()
                except:
                    print_msg("Can not find Login element!")
                
            sleep(3)
    except:
        print_msg("Do not need login.")
    
    #printf("OK")


def delete_folder_contents(folder_path):
    if os.path.isdir(folder_path):
        # Loop through all items in the directory
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            # If it's a directory, use rmtree to delete it
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            # If it's a file, use os.remove to delete it
            else:
                os.remove(item_path)
    else:
        print(f"The path {folder_path} is not a directory.")

        
def Run_QIS():
    print("Run QIS")
    qis_outputs_path = cur_directory + "\\AutoSetQIS\\outputs\\"
    qis_outputs_file = qis_outputs_path + "Set_QIS.txt"
    
    delete_folder_contents(qis_outputs_path)
    win32api.ShellExecute(0,"open","RunQIS.bat","", "", 1)
    check = 0
    while(check < 30):
        print("check: " + qis_outputs_file)
        if os.path.isfile(qis_outputs_file):
            f = open(qis_outputs_file)
            lines = f.readlines()
            if "PASS" in lines:
                return True
            else:
                return False
        else:
            print("wait 30 sec")
            time.sleep(30)
    print("Auto QIS has no result more tan 15 mins. Return False")
    return False


def Reset_CAP():
    msg=('Reset CAP - %s' % (cap_ip))
    print_msg(msg)
    
    if common.Get_Cookie(cap_ip, admin_token):
        command = 'curl -s -A "asusrouter-Windows-ATE-2.0.0.1" -e "%s" -b savecookie.txt -d "{\\\"action_mode\\\":\\\"Restore\\\"}" http://%s/applyapp.cgi' % (cap_ip, cap_ip)
        result = send_curl_command(command)
        msg=('Sleep 150 sec')
        print_msg(msg)
        time.sleep(150)
    else:
        print_msg("Reset CAP Fail!")
        

def Get_Value(f_lines, keyword):
    ret = ""
    
    for line in f_lines:
        if keyword in line:
            line_2 = line.replace('\n','')
            splitStr = line_2.split('=')
            ret = splitStr[1]
            break
    #print(ret)
    return ret


def Load_General_Config():

    global http_username
    global http_password
    global ppp_username
    global ppp_password    

    global wan_1_dut_wan_ip
    global wan_pc_1_wan_server_ip
    global wan_pc_1_netmask
    global wan_pc_1_gateway
    global wan_pc_1_ppp_server_ip
    global wan_2_dut_wan_ip
    global wan_pc_2_wan_server_ip
    global wan_pc_2_netmask
    global wan_pc_2_gateway
    global wan_pc_2_ppp_server_ip
    global wan_3_dut_wan_ip
    global wan_pc_3_wan_server_ip
    global wan_pc_3_netmask
    global wan_pc_3_gateway
    global wan_pc_3_ppp_server_ip


    f = open(dut_common_file)
    lines = f.readlines()
    location = Get_Value(lines, "LOCATION")
    http_username = Get_Value(lines, "HTTP_USERNAME")
    http_password = Get_Value(lines, "HTTP_PASSWORD")
    f.close()
    
    f = open(wan_setting_file)
    lines = f.readlines()
    ppp_username = Get_Value(lines, "PPP_USERNAME")
    ppp_password = Get_Value(lines, "PPP_PASSWORD")
    f.close()

    wan_1_dut_wan_ip = Get_Value(lines, "WAN_1_DUT_WAN_IP")
    wan_pc_1_wan_server_ip = Get_Value(lines, "WAN_PC_1_SERVER_IP")
    wan_pc_1_netmask = Get_Value(lines, "WAN_PC_1_NETMASK")
    wan_pc_1_gateway = Get_Value(lines, "WAN_PC_1_GATEWAY")
    wan_pc_1_ppp_server_ip = Get_Value(lines, "WAN_PC_1_PPP_SERVER_IP")
    
    wan_2_dut_wan_ip = Get_Value(lines, "WAN_2_DUT_WAN_IP")
    wan_pc_2_wan_server_ip = Get_Value(lines, "WAN_PC_2_SERVER_IP")
    wan_pc_2_netmask = Get_Value(lines, "WAN_PC_2_NETMASK")
    wan_pc_2_gateway = Get_Value(lines, "WAN_PC_2_GATEWAY")
    wan_pc_2_ppp_server_ip = Get_Value(lines, "WAN_PC_2_PPP_SERVER_IP")

    wan_3_dut_wan_ip = Get_Value(lines, "WAN_3_DUT_WAN_IP")
    wan_pc_3_wan_server_ip = Get_Value(lines, "WAN_PC_3_SERVER_IP")
    wan_pc_3_netmask = Get_Value(lines, "WAN_PC_3_NETMASK")
    wan_pc_3_gateway = Get_Value(lines, "WAN_PC_3_GATEWAY")
    wan_pc_3_ppp_server_ip = Get_Value(lines, "WAN_PC_3_PPP_SERVER_IP")
    
    f.close()
    
    
    
def Load_DUT_Config(dut_config_file):
    global dut_ip
    global lan_port_list
    global wan_port_list
    global all_port_no
    global connect_dict

    f = open(dut_config_file)
    lines = f.readlines()

    for line in lines:
        print(">"+line)
        print()
        if '=' not in line:
            break
        var_split = line.split('=')
        #print("%s/%s"%(var_split[0], var_split[1]))
        if var_split[0] == "DUT_IP":
            dut_ip = var_split[1].replace('\n','')
        else:
            connect_dict[var_split[0]] = var_split[1].upper().replace(' ','_').replace('-','_').replace('\n','')

    print(connect_dict)
    print("=========================")
    
def Start_Test():
    global driver
    global now_time
    global log_file
    global result_file
    global function
    global model_name
    global test_time
    global run_chariot
    global function_list
    global wan_type_list
    global run_qis
    global ping_lan_client_fail
    global report_path
    global chariot_pair   

    report_path = "D:\ASUSWebstorage\gitserv_asus_sync\Test_Report\Multiport_test"
    TPT = [['N/A']*3 for _ in range(5)]
    #print_msg(TPT)

    print("UI_start = %d"%(UI_start))

    if UI_start:
        model_name = Form.box1.currentText()
        chariot_pair = Form.box2.currentText()
        run_chariot = Form.box3.currentText()
        test_time = Form.box4.currentText()
    else:
        if os.path.isfile(auto_run_file):
            f = open(auto_dut_file)
            lines = f.readlines()
            #print(lines)
            model_name = Get_Value(lines, "MODEL_NAME")
            report_path = Get_Value(lines, "REPORT_PATH")
            chariot_pair = Get_Value(lines, "CHARIOT_PAIR")

    msg = "model_name: " + model_name
    print_msg(msg)    
    msg = "chariot_pair: " + chariot_pair
    print_msg(msg)

    config_file = config_path + model_name + '\\info.txt'
    specify_lan_port_file = config_path + model_name + '\\specify_lan_port_test.txt'
    
    try:
        os.remove(".\\Chariot\\runtst.log")    
    except:
        msg = "No runtst.log"
        print_msg(msg)
    try:
        os.remove(".\\Chariot\\CHARIOT.LOG")    
    except:
        msg = "No CHARIOT.LOG"
        #print_msg(msg)

    print_msg("\nSelect Function:")
    for func in function_list:
        print_msg(func)
    print_msg("\nSelect WAN type:")
    for wantype in wan_type_list:
        print_msg(wantype)

    Load_DUT_Config(config_file)
    #print(Get_Key_From_Value(connect_dict, "LAN4"))
    #print("==========")


    #Test code here
    #Enable_EULA(dut_ip)
    #Enable_QoS(driver, "Traditional_QoS")
    #return


    if run_qis:
        if not Ping(dut_ip, 300, 10):
            msg = 'Can not ping DUT - %s for 5 mins. Stop test'%(dut_ip)
            print_msg(msg)
            return
        else:
            print_msg("ping 192.168.50.1 OK, keep test.")
                    
            qis_config = 0
            while (qis_config < 3):
                if Run_QIS():
                    print_msg("Run QIS Pass")
                    break
                else:
                    print_msg("Run QIS Fail. Reset DUT & try again.")
                    qis_config += 1
                    Reset_CAP()

            if qis_config == 3:
                print_msg("DUT is not default & try to reset fail for 3 times. STOP TEST!!!")
                return
            
    title = "Tool, Pair, Tool version, Model, FW Version, Enable Function, WAN PORT, LAN PORT, WAN TYPE, Test PC ping DUT, DUT ping WAN PC, Test PC ping WAN PC, Uplink(mbps), Downlink(mbps), Bi-direction(mbps)\n"
    result_file = '%s\\Result\\%s_mulit_port_test_result_%s.csv' %(cur_directory, model_name, now_time)
    msg = ('Open: ' + result_file)
    print_msg(msg)
    ret_file = open( result_file, 'w')
    ret_file.write(title)
    ret_file.close()

    #Test code here
    #if not Ping(dut_ip, 180, 5):
    #    msg = 'Can not ping DUT - %s for 5 mins. Stop test'%(dut_ip)
    #    print_msg(msg)
    #    return
    #else:
    #    print_msg("ping 192.168.50.1 OK, keep test.")
    
    #print("nslookup asusrouter.com")
    #str1 = os.popen('nslookup asusrouter.com').read()
    #driver = webdriver.Chrome()

    Disable_Redirect(driver)
    Enable_EULA(dut_ip)
    Get_FW_Version(dut_ip, asus_token)

    if specify_lan_port_test:
        if not Get_Port_Info_From_File(specify_lan_port_file):
            print_msg("Do not find \"specify_lan_port_test.txt\". Stop test!")
            return 
    else:
        Get_Dual_Wan_Port(driver, config_file)   

    ch_lan_pc = ''
    ext_wanlan_pc = ''
    for lan_port in test_lan_port_list:

        #print_msg("----> %s "%(lan_port))
        upper_lan_port = lan_port.upper().replace(' ','_').replace('-','_')
        print_msg("----> %s "%(upper_lan_port))
        if "ALL_LAN" == lan_port:
            ch_lan_pc = lan_port
        else:
            ch_lan_pc = Get_Key_From_Value(connect_dict, upper_lan_port)

        print_msg("LAN_PC= %s"%(ch_lan_pc))

    for ext_wan in UI_wan_port_list:
        #print_msg("----> %s "%(ext_wan))
        upper_ext_wan = ext_wan.upper().replace(' ','_').replace('-','_')
        print_msg("----> %s "%(upper_ext_wan))
        ext_wanlan_pc = Get_Key_From_Value(connect_dict, upper_ext_wan)
        print_msg("WAN_PC= %s"%(ext_wanlan_pc))
        
    '''
    wan_no = 0
    for wan_port in UI_wan_port_list:
        wan_no += 1
        msg = ">>> %d: UI_wan_port: %s" %(wan_no, wan_port)
        print_msg(msg)
        #Set_Wan_Port(wan_port)
        #Set_Wan_Type(wantype, wan_no)
        Run_Nat_Test(wantype, wan_port, wan_no)
    return
    '''
    
    #sleep(10)
    #Enable_Telnet(driver)

    file = open(autorun_path, "w")
    file.write('Testing\n')
    file.close()

    test_run = 0
    while test_run < int(test_time):
        test_run += 1
        msg = ('\n--- Test Run: %d ---' %(test_run))
        print_msg(msg)
        
        for function in function_list:
            if function == '':
                continue

            msg = ('\n---%s---' %(function))
            print_msg(msg)
            ping_lan_client_fail = 0 #reset before test
            
            if not Ping(dut_ip, 300, 30):
                msg = 'Can not ping DUT - %s for 5 mins. Stop test'%(dut_ip)
                print_msg(msg)
                return
            else:
                print_msg("ping 192.168.50.1 OK, keep test.")

            Disable_Redirect(driver)
            
            if function == 'AiProtection':
                Enable_Aiportection(driver)
            elif function == 'Adaptive_QoS':
                Enable_QoS(driver, "Adaptive_QoS")
            elif function == 'Traditional_QoS':
                Enable_QoS(driver, "Traditional_QoS")

            sleep(30)
            Disable_Redirect(driver)

            wan_no = 0
            for wan_port in UI_wan_port_list:
                wan_no += 1
                
                msg = ">>> %d: UI_wan_port: %s" %(wan_no, wan_port)
                print_msg(msg)

                if not Ping(dut_ip, 300, 30):
                    msg = 'Can not ping DUT - %s for 5 mins. Stop test'%(dut_ip)
                    print_msg(msg)
                    return
                else:
                    print_msg("ping 192.168.50.1 OK, keep test.")

                retry = 0
                while retry < 5:
                    if Set_Wan_Port(wan_port):
                        break
                    else:
                        print_msg("Set_Wan_Port fail, wait 3 min & retry.")
                        sleep(180)
                        retry += 1
                
                for wantype in wan_type_list:
                    if wantype == "":
                        continue
                    msg = ("wan type: "+wantype)
                    print_msg(msg)
                    if not Ping(dut_ip, 300, 30):
                        msg = 'Can not ping DUT - %s for 5 mins. Stop test'%(dut_ip)
                        print_msg(msg)
                        return
                    else:
                        print_msg("ping 192.168.50.1 OK, keep test.")
                        
                    Set_Wan_Type(wantype, wan_no)
                    Run_Nat_Test(wantype, wan_port, wan_no)
                
            if function == 'AiProtection':
                Disable_Aiportection(driver)
            elif 'QoS' in function:
                Disable_QoS(driver)
            sleep(30)
    
    print_msg("Finish test.")
    driver.close()
    file = open(autorun_path, "w")
    file.write('idle\n')
    file.close()

    shutil.copy2(result_file, report_path)
        
    return

    
if __name__ == "__main__":
    now = datetime.now()
    now_time = now.strftime("%Y-%m-%d-%H-%M")
    cur_directory = os.getcwd()
    config_path = cur_directory + '\\Config\\'
    chariot_pair_path = cur_directory + '\\Chariot\\'
    log_file = cur_directory +'\\log\\' + now_time + '_process.log'
    qis_file = cur_directory + '\\Config\\qis_setting.txt'
    auto_run_file = cur_directory + '\\Config\\autorun.txt'
    auto_dut_file = cur_directory + '\\Config\\autotest_setting.txt'
    test_case_file = cur_directory + '\\Config\\Test_case.txt'
    f = cur_directory + '\\Config\\DUT_common_setting.txt'
    wan_setting_file = cur_directory + '\\Config\\WAN_server_setting.txt'
    print(log_file)
    print(now_time)
    Load_General_Config()
    autorun_path = config_path + '\\autorun.txt'

    chrome_chk_ret = browser_driver_version_check()

    if chrome_chk_ret != 'OK':
        chrome_driver_version = query_chrome_driver_version()
        warn_msg = ('Chromedriver version is %s' %(chrome_driver_version))
        print_msg(warn_msg)
        warn_msg = chrome_chk_ret + '\nPlease go to \"https://chromedriver.chromium.org/\" & download new chromedriver.'
        print_msg(warn_msg)
        sleep(15)
    else:
        driver = webdriver.Chrome()
        driver.maximize_window()
        app = QtWidgets.QApplication(sys.argv)
        Form = MyWidget()
        Form.show()
        
        file = open(autorun_path, "r")
        lines = file.readlines()
        file.close()
        print(lines)
        for line in lines:
            print (line)
            if "Run" in line:
                print('Run test by trigger.')
                Start_Test()
                os._exit(0)
            
        sys.exit(app.exec())
