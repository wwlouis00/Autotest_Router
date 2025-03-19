import time
import json
import subprocess


def Ping(address, retry, success):
    #print('ping ' + address + '=')
    #return True
    i = 0
    ok = 0
    if len(address) == 0:
        msg = 'No IP, stop ping\n'
        print(msg)
    else:
        cmd = 'ping -n 1 ' + address
        print(cmd)
        while (i < retry):
            try:
                output = subprocess.check_output(cmd)
                #print(output)
                if b'TTL=' in output:
                    ok += 1
                    msg="PING OK"
                    print(msg)
                else:
                    msg="FAIL"
                    print(msg)
                if ok == success:
                    msg="Ping Success"
                    print(msg)
                    return True
            except subprocess.CalledProcessError as e:
                code = e.returncode
                msg="Ping Error! Re-send again. [ERROR NO]: " + str(code)
                print(msg)
            i += 1
            time.sleep(1)

    return False


def Get_Value(f_lines, keyword):
    #print(f_lines, keyword)
    ret = ""
    
    for line in f_lines:
        if keyword in line:
            line_2 = line.replace('\n','')
            splitStr = line_2.split('=')
            ret = splitStr[1]
            break
    #print(ret)
    return ret


def Send_Curl_Command(cmd):
    #print("SEND: ")
    #print(cmd)

    retry = 0
    while (retry < 3):
        try:
            output = subprocess.check_output(cmd)
            # print (output)
            # print ('\n')
            if type(output) == bytes:
                decode_output = output.decode()
            if type(output) == str:
                decode_output = output
            return decode_output
        except subprocess.CalledProcessError as e:
            code = e.returncode
            msg = ("Send CMD Error! Re-send again. [ERROR NO]: %d" % (code))
            print(msg)
            #time.sleep(5)
            retry += 1
    return 'send cmd fail'


def Get_Cookie(dut_ip, token):
    #print("get_cookie: %s %s" %(dut_ip, token))
    command = "curl -s -A asusrouter-test-DUTUtil-111 http://" + dut_ip + "/login.cgi?login_authorization=" + token + " -D savecookie.txt"
    result = Send_Curl_Command(command)

    if 'asus_token' in result:
        #print("Got it")
        return True

    #print("get_cookie fail")
    return False


def Upload_FW(dut_ip, fw_path):
    print("Upload_FW: %s %s" %(dut_ip, fw_path))
    
    command = 'curl -s -A "asusrouter-test-DUTUtil-111" -e "%s" -b savecookie.txt -F file=@"%s" http://%s/upgrade.cgi' %(dut_ip, fw_path, dut_ip)
    result = Send_Curl_Command(command)
    print (result)

    if 'reboot_needed_time' in result:
        msg=('Upload success. ')
        print(msg)
        return True
    else:
        print('Upload failed.')
        return False

        
def Get_Nvram(ip, nvram_var, token):
    print('Get %s nvram: %s' % (ip, nvram_var))
    for j in range(0, 3):
        if Get_Cookie(ip, token):
            command = 'curl -s -A "asusrouter-test-DUTUtil-111" -e "%s" -b savecookie.txt -d "hook=nvram_get(%s)" http://%s/appGet.cgi' % (ip, nvram_var, ip)
            result = Send_Curl_Command(command)
            print(result)
            
            pythondict = json.loads(result)
            if nvram_var in result:
                print (pythondict[nvram_var])
                return pythondict[nvram_var]

    return ''


def validate_ip(value):
    flag = False
    if ("." in value):
        elements_array = value.strip().split(".")
    else:
        elements_array = []
    if(len(elements_array) == 4):
        for i in elements_array:
            if (i.isnumeric() and int(i)>=0 and int(i)<=255):
                flag=True
            else:
                flag=False
                break
    return flag


def Reboot_DUT(dut_ip, token):
    if validate_ip(dut_ip):
        msg =("Reboot: %s" %(dut_ip))
        print(msg)
        for j in range(0, 4):
            command = "curl -s -A asusrouter-test-DUTUtil-111 http://" + dut_ip + "/login.cgi?login_authorization=" + token + " -D re_savecookie.txt"
            result = Send_Curl_Command(command)

            if 'asus_token' in result:
                #print("Got re cookie")
                command = "curl -s -A asusrouter-test-DUTUtil-111 -e " + dut_ip + " -b re_savecookie.txt -d \"{\\\"action_mode\\\":\\\"reboot\\\"}\" http://" + dut_ip + "/apply.cgi"
                result = Send_Curl_Command(command)
                #print(result)
                return 1
    
    return 0
