# for test cases without the OS update operation -- normal situation
# seed generation mode = dual-app

import subprocess
from datetime import datetime
import os
import csv
import time
import random

base_path="E:/CuPerFuzzer/normal-2/"
apk_base_path2 = "E:/CuPerFuzzer/apk-2/" # test apps for the dual-app mode

########################################
# select a seed randomly
def selectSeed():
    # randomly select a protection level
    protectionLevels = ['normal', 'dangerous', 'signature']
    pl = random.choice(protectionLevels)
    # randomly select a permission group
    permissionGroups = ['ACTIVITY_RECOGNITION', 'CALENDAR', 'CALL_LOG', 'CAMERA', 'CONTACTS', 'LOCATION', 'MICROPHONE',
                        'NULL', 'PHONE', 'SENSORS', 'SMS', 'STORAGE', 'UNDEFINED']
    pg = random.choice(permissionGroups)
    seed = ['TEST', pl, pg]
    return seed

###################################################
# test case construction
# mutation: change permission group or protection level or both or remove definition
# change the attribute [protectionLeve] randomly
def changePL(per):
    protectionLevels = ['normal', 'dangerous', 'signature']
    new_pls = protectionLevels
    new_pls.remove(per[1])
    new_pl = random.choice(new_pls)
    return new_pl

# change the attribute [permissionGroup] randomly
def changePG(per):
    permissionGroups = ['ACTIVITY_RECOGNITION', 'CALENDAR', 'CALL_LOG', 'CAMERA', 'CONTACTS', 'LOCATION', 'MICROPHONE',
                        'NULL', 'PHONE', 'SENSORS', 'SMS', 'STORAGE', 'UNDEFINED']
    new_pgs = permissionGroups
    new_pgs.remove(per[2])
    new_pg = random.choice(new_pgs)
    return new_pg

# old_app -> new_app
def generateTestApp(old_app, per_name):
    # remove definition or change attributes
    if old_app == ['NULL', 'NULL', 'NULL']:
        # add some attributes
        pl = random.choice(['normal', 'dangerous', 'signature'])
        pg = random.choice(['ACTIVITY_RECOGNITION', 'CALENDAR', 'CALL_LOG', 'CAMERA', 'CONTACTS', 'LOCATION', 'MICROPHONE',
                        'NULL', 'PHONE', 'SENSORS', 'SMS', 'STORAGE', 'UNDEFINED'])
        return [per_name, pl, pg]
    changeOPs = ['pl', 'pg', 'both', 'remove']
    changeOP = random.choice(changeOPs)
    new_pl = changePL(old_app)
    new_pg = changePG(old_app)
    if changeOP == 'pl':
        new_app = [old_app[0], new_pl, old_app[2]]
    elif changeOP == 'pg':
        new_app = [old_app[0], old_app[1], new_pg]
    elif changeOP == 'both':
        new_app = [old_app[0], new_pl, new_pg]
    elif changeOP == 'remove':
        new_app = ['NULL', 'NULL', 'NULL']
    return new_app

# generate operation sequence
# 1-installation, 2-uninstallation, 3-OS update, 4-reboot
# rules: 1-meaningful uninstallation, 2-discontinuous reboots,
# 3-only one OS update, 4-existential test app (for single-app mode)
def isMeetRules(op_seq, op, app_num):
    if op == '2':
        if app_num == 0: # meaningless uninstallation
            return False
    if op == '4':
        if op_seq[-1] == '4': # continuous reboots
            return False
    return True

# build an operation sequence
def generateOPSeq():
    op_seq = ['1']
    app_num = 1
    op_num = random.randint(1, 5) + 1 # 1 means the first installation of the seed app
    while (len(op_seq) != op_num):
        # generate a new operation
        ops = ['1', '2', '4']
        op = random.choice(ops)
        new_ops = ops
        # rule 1, 2
        while True:
            if isMeetRules(op_seq, op, app_num) == True:
                op_seq.append(op)
                if op == '1':
                    app_num = 1
                elif op == '2':
                    app_num = 0
                break
            new_ops.remove(op)
            op = random.choice(new_ops)
    return op_seq

# generate test apps
def generateInstallApkComb(op_seq, seed):
    install_app_num = op_seq.count('1')
    install_app_comb = [seed]
    while (len(install_app_comb) != install_app_num):
        old_app = install_app_comb[-1]
        new_app = generateTestApp(old_app, seed[0])
        install_app_comb.append(new_app)
    install_apk_comb = []
    for install_app in install_app_comb:
        install_apk = '-'.join(install_app)+'.apk'
        install_apk_comb.append(install_apk)
    return install_apk_comb

###################################################
# execute operations
def install(apk,device_id):
    cmd_install='adb -s '+device_id+' install '+apk
    try:
        print('----------------------------------')
        print('Install [',apk.split('/')[-1],']...')
        subprocess.run(args=cmd_install,shell=True,check=True)
        return 0
    except Exception as e:
        print('Installation error:',e)
        return -1

def uninstall(packageName,device_id):
    cmd_uninstall='adb -s '+device_id+' uninstall '+packageName
    try:
        print('----------------------------------')
        print('Uninstall [',packageName,']...')
        subprocess.run(args=cmd_uninstall,shell=True,check=True)
        return 0
    except Exception as e:
        print('Uninstallation error:',e)
        return -1

def reboot(device_id):
    cmd_reboot='adb -s '+device_id+' reboot'
    try:
        print('----------------------------------')
        print('Reboot device...')
        subprocess.run(cmd_reboot, shell=True, check=True)
        time.sleep(28) # wait for reboot
        return 0
    except Exception as e:
        print('Rebooting error:', e)
        return -1

def testConnection(device_id):
    cmd_dev='adb devices'
    print('----------------------------------')
    print('Test connection...')
    re=subprocess.Popen(cmd_dev,shell=True,stdout=subprocess.PIPE,encoding='gbk')
    dev_infos=re.stdout.readlines()
    for dev_info in dev_infos:
        if device_id in dev_info:
            return 0
    return -1

# alternative reset way
def reset_fastboot(device_id):
    cmd_bootloader='adb -s '+device_id+' reboot bootloader'
    cmd_reset='fastboot -s '+device_id+' -w'
    cmd_reboot='fastboot -s '+device_id+' reboot'
    try:
        print('----------------------------------')
        print('Fastboot reset...')
        subprocess.run(args=cmd_bootloader, shell=True, check=True)
        subprocess.run(args=cmd_reset, shell=True, check=True)
        subprocess.run(args=cmd_reboot, shell=True, check=True)
        time.sleep(30) # wait for rebooting
        return 0
    except Exception as e:
        print('Fastboot reset error:',e)
        return -1

def erase_fastboot(device_id):
    cmd_erase='fastboot -s '+device_id+' -w'
    cmd_reboot='fastboot -s '+device_id+' reboot'
    try:
        print('----------------------------------')
        print('Fastboot erase data...')
        subprocess.run(args=cmd_erase, shell=True, check=True)
        subprocess.run(args=cmd_reboot, shell=True, check=True)
        time.sleep(30) # wait for rebooting
        return 0
    except Exception as e:
        print('Fastboot erasing error:',e)
        return -1

# major reset way
#click the button "Erase all data" to achieve the factory reset
def reset(device_id):
    cmd_open='adb -s '+device_id+' shell am start -n com.android.settings/.Settings'
    cmd_swipe='adb -s '+device_id+' shell input swipe 240 865 370 202'
    cmd_system='adb -s '+device_id+' shell input tap 488 1688'
    cmd_adv='adb -s '+device_id+' shell input tap 456 1027'
    cmd_reset='adb -s '+device_id+' shell input tap 446 1016'
    cmd_erase='adb -s '+device_id+' shell input tap 539 567'
    cmd_confirm='adb -s '+device_id+' shell input tap 861 1692'
    cmd_reboot='adb -s '+device_id+' shell input tap 861 1692'
    try:
        print('----------------------------------')
        print('Factory reset...')
        subprocess.run(cmd_open, shell=True, check=True)
        time.sleep(0.3)
        subprocess.run(cmd_swipe, shell=True, check=True)
        time.sleep(0.7)
        subprocess.run(cmd_system, shell=True, check=True)
        subprocess.run(cmd_adv, shell=True, check=True)
        subprocess.run(cmd_reset, shell=True, check=True)
        subprocess.run(cmd_erase, shell=True, check=True)
        subprocess.run(cmd_confirm, shell=True, check=True)
        subprocess.run(cmd_reboot, shell=True, check=True)
        time.sleep(10)
        re=testConnection(device_id)
        print('Connection status:',re)
        if re==0: # not enter the reboot model
            print('Factory reset is unsuccessful,enter the fastboot mode...')
            re=reset_fastboot(device_id)
            return re
        time.sleep(45)
        return 0
    except Exception as e:
        print('Factory reset error:', e)
        return -1

def simulateClick(packageName,device_id):
    cmd_open = 'adb -s ' + device_id + ' shell am start -n' + packageName + '/.MainActivity'
    cmd_click = 'adb -s ' + device_id + ' shell input tap 478 807'
    try:
        print('----------------------------------')
        print('Click to request permissions...')
        for i in range(2):
            click_result = 'unsuccessful'
            # open the app
            re = subprocess.run(args=cmd_open, shell=True, stderr=subprocess.PIPE, encoding='gbk')
            err = re.stderr
            if 'Error type 3' not in err:
                print('Open app successfully.')
                time.sleep(1)
                # click
                subprocess.run(args=cmd_click, shell=True, check=True)
                click_result = 'successful'
                print('Click successfully.')
                time.sleep(1.5)  # waiting for granting all permissions
                return click_result
            print('Open app unsuccessfully!')
            if i == 0: # the first opening failed, wait 1s, try again
                time.sleep(1)
        return click_result
    except Exception as e:
        print('Clicking error:', e)
        return -1

###############################################
# verification
def openFile(file_name):
    file_path = base_path+file_name
    f = open(file_path, 'r')
    file = f.readlines()
    f.close()
    return file

# get the permission's protection level from the system
def getCusperProtSystem(file_name):
    file = openFile(file_name)
    for i in range(len(file)):
        if 'permission:com.leiry.TEST' in file[i]:
            cp_prot = file[i+4].split()[0].split(':')[1]
            return cp_prot
    return 'null' # the permission definition is not in the system

# get the permission's protection level from the owner app
def getCusperProtOwner(file_name):
    file = openFile(file_name)
    for i in range(len(file)):
        if 'com.leiry.TEST: prot=' in file[i]:
            if 'INSTALLED' in file[i]:
                cp_prot = file[i].split(':')[1].split(',')[0].split('=')[1]
                return cp_prot
    return 'null'

def getGrantedInstallPer(file_name):
    file = openFile(file_name)
    i = 0
    install_granted = []
    while(i<len(file)):
        if file[i] == '    install permissions:\n':
            i = i+1
            while(i<len(file) and '    User 0:' not in file[i]):
                if 'granted=true' in file[i]:
                    per = file[i].split(':')[0].split()[0]
                    install_granted.append(per)
                i = i+1
            return install_granted
        i = i+1
    return install_granted

def getGrantedRuntimePer(file_name):
    file = openFile(file_name)
    i = 0
    runtime_granted = []
    while(i<len(file)):
        if file[i] == '      runtime permissions:\n':
            i = i+1
            while(i<len(file) and file[i] != '\n'):
                if 'granted=true' in file[i]:
                    per = file[i].split(":")[0].split()[0]
                    runtime_granted.append(per)
                i = i+1
            return runtime_granted
        i = i+1
    return runtime_granted

# verify if the case is effective for dual-app mode
def verifyCase2(declared_app,requested_app,device_id):
    # get the declared permissions' information in the system
    file_permission = 'system.txt'
    cmd_system= 'adb -s '+device_id+' shell pm list permissions -f -g > '+base_path+file_permission
    # get the information of the app
    file_declared = 'declared.txt'
    file_requested = 'requested.txt'
    cmd_dump_declared = 'adb -s '+device_id+' shell dumpsys package '+declared_app+' > '+base_path+file_declared
    cmd_dump_requested = 'adb -s ' + device_id + ' shell dumpsys package ' + requested_app + ' > ' + base_path + file_requested
    try:
        print('----------------------------------')
        print('Verify test case...')
        # get requested app information
        subprocess.run(args=cmd_dump_requested,shell=True,check=True)
        install_granted = getGrantedInstallPer(file_requested)
        runtime_granted = getGrantedRuntimePer(file_requested)
        # get custom permission protection level
        try:
            subprocess.run(cmd_system, shell=True, check=True) # major way
            cusper_pl = getCusperProtSystem(file_permission)
            print('System cusper_pl:',cusper_pl)
        except:
            print("Get system permissions' info unsuccessfully, get app's info...")
            subprocess.run(cmd_dump_declared, shell=True, check=True) # alternative way
            cusper_pl = getCusperProtOwner(file_declared)
            print('Owner cusper_pl:',cusper_pl)
    except Exception as e:
        print('Verification error:',e)
        return -1
    granted_per = []
    for per in install_granted:
        if per == 'com.leiry.TEST':
            if cusper_pl != 'signature': # only signature custom permission is valid
                continue
        granted_per.append(per+'(signature)')
    for per in runtime_granted:
        granted_per.append(per+'(dangerous)')
    return granted_per

#############################################
# log
def storeCSV(store_name,info):
    store_path=base_path+store_name
    f=open(store_path,'a',newline='')
    writer=csv.writer(f)
    writer.writerow(info)
    f.close()

def storeTXT(store_name,info):
    store_path=base_path+store_name
    f=open(store_path,'a')
    f.write(info+'\n')
    f.close()

def storeTXTNew(store_name,infos):
    store_path=base_path+store_name
    f=open(store_path,'w')
    f.writelines(infos)
    f.close()

def log(file_name, case_id, seed, op_seq, install_apk_comb, start_time, end_time):
    try:
        storeTXT(file_name,"--------------------------------------------------------------------")
        storeTXT(file_name, "Case_id: " + str(case_id))
        storeTXT(file_name,"Seed: "+str(seed))
        storeTXT(file_name,"Op_seq: "+','.join(op_seq))
        storeTXT(file_name,"Install_apk_comb: "+','.join(install_apk_comb))
        spend_time=(end_time-start_time).seconds
        storeTXT(file_name,"Start_time: "+str(start_time))
        storeTXT(file_name, "End_time: " + str(end_time))
        storeTXT(file_name, "Spend_time: " + str(spend_time))
        storeTXT(file_name, "-------------------------------------------------------------------")
        return 0
    except Exception as e:
        print("Logging error:",e)
        return -1

def changeCaseNum(new_tested_case_num, new_effective_case_num, file_name):
    infos=openFile(file_name)
    infos[0]='tested_case_num:'+str(new_tested_case_num)+'\n'
    infos[1]='effective_case_num:'+str(new_effective_case_num)+'\n'
    storeTXTNew(file_name,infos)

def getCaseNum(file_name):
    if os.path.exists(base_path+file_name)==False:
        storeTXT(file_name, 'tested_case_num:0')
        storeTXT(file_name, 'effective_case_num:0')
    infos=openFile(file_name)
    tested_case_num=int(infos[0].split(':')[-1].split()[0])
    effective_case_num=int(infos[1].split(':')[-1].split()[0])
    print('Tested cases:',tested_case_num)
    print('Effective cases:', effective_case_num)
    return tested_case_num, effective_case_num

##############################################
# one test
def oneTestNormal2(op_seq,install_apk_comb,device_id,effective_case_num):
    declared_app = "com.leiry.declared"
    requested_app = "com.leiry.simulateclick"
    requested_apk = "E:/CuPerFuzzer/simulateClick.apk"
    app_id = 0
    i = 0
    # execute operations
    while(i<len(op_seq)):
        if op_seq[i] == '1':
            install_apk = apk_base_path2 + install_apk_comb[app_id]
            re = install(install_apk,device_id)
            app_id = app_id + 1
            # install the requested app at the beginning
            # install the declared app first and then the requested app
            if re != -1 and i == 0:
                re = install(requested_apk, device_id)
        elif op_seq[i] == '2':
            re = uninstall(declared_app,device_id)
        elif op_seq[i] == '4':
            re = reboot(device_id)
        if re != -1: # the last operation is executed successfully, then next
            i = i+1
        else:
            return -1
    #request permissions by simulating the click of a button
    click_result = simulateClick(requested_app,device_id)
    if click_result == -1:
        return -1
    # verify if it is an effective case
    granted_per = verifyCase2(declared_app, requested_app, device_id)
    if granted_per == -1:
        return -1
    print("Granted permissions' number:", len(granted_per))
    print("Granted permissions:", granted_per)
    if len(granted_per) != 0:
        effective_case_num+=1
        effective = ','.join(granted_per)
    else:
        effective = "no"
    store_info = [','.join(op_seq), len(op_seq), ','.join(install_apk_comb), effective, click_result, "dual-app"]
    storeCSV("normal-result-2.csv", store_info)
    return effective_case_num

##############################################
# tested case
def getTestedOPInfo(file):
    tested={}
    i=0
    while(i<len(file)):
        if 'Op_seq' in file[i]:
            op_seq=file[i].split(': ')[1].split()[0]
            if '--------------------------------------' in file[i+5]:
                apk_comb=file[i+1].split(': ')[1].split()[0].split(',')
                if tested.get(op_seq)==None:
                    tested[op_seq]=[apk_comb]
                else:
                    tested[op_seq].append(apk_comb)
        i=i+1
    return tested

################################################
# start fuzzing
def fuzzingNormal2():
    device_id = 'FA79K1A07801'
    print('Start testing...')
    start_time = datetime.now()
    print('Start time:', start_time)
    storeTXT('normal-log-2.txt', '\nstart time: ' + str(start_time))
    storeCSV('normal-result-2.csv',
             ['op_sequence', 'op_length', 'install_apk_combination', 'granted_permission', 'click_result',
              'seed_model'])
    # get tested cases' number and effective cases' number
    tested_case_num, effective_case_num = getCaseNum('normal2-case_num.txt')
    while True:
        # select a seed
        print('************************************')
        print('Select a seed...')
        seed = selectSeed()
        print(seed)
        # generate an operation sequence
        print('++++++++++++++++++++++++++++++++++++')
        print('Build an operation sequence...')
        op_seq = generateOPSeq()
        print(op_seq)
        # generate test apps
        print('+++++++++++++++++++++++++++++++++++++')
        print('Generate test apps...')
        install_apk_comb = generateInstallApkComb(op_seq, seed)
        print(install_apk_comb)
        # get tested cases
        log_file = openFile('normal-log-2.txt')
        tested = getTestedOPInfo(log_file)
        tested_apk_combs = tested.get(','.join(op_seq))
        if tested_apk_combs == None:
            tested_apk_combs = []
        if install_apk_comb in tested_apk_combs:
            print('Duplicated test case, build again...')
            continue
        # execute one test
        print('+++++++++++++++++++++++++++++++++++++')
        print('Execute a case...')
        while True:
            start_time = datetime.now()
            re_op = oneTestNormal2(op_seq, install_apk_comb, device_id, effective_case_num)
            if re_op != -1:
                effective_case_num = re_op
                break
            # reset to execute again
            print('----------------------------------')
            print('Execute unsuccessfully, reset to execute again...')
            re_reset = reset(device_id)
            if re_reset == -1:
                # the first factory reset failed
                while True:  # repeat until reset successfully
                    time.sleep(20) # make sure that the tested connection status is true
                    re_con = testConnection(device_id)
                    print('Connection status:', re_con)
                    if re_con == 0:  # device does not enter the fastboot mode
                        print('Enter the fastboot reset...')
                        re_reset = reset_fastboot(device_id)  # fastboot reset
                    else:  # device has entered the fastboot mode
                        print('Has been in the fastboot mode...')
                        re_reset = erase_fastboot(device_id)  # fastboot erase data
                    if re_reset != -1:
                        break
            print('Reset is complete.')
        # record tested cases' number, effective cases' number
        tested_case_num += 1
        print('++++++++++++++++++++++++++++++++++++')
        print('Successful tested cases:', tested_case_num)
        print('Effective cases:', effective_case_num)
        changeCaseNum(tested_case_num, effective_case_num, 'normal2-case_num.txt')
        # reset the test environment
        print('++++++++++++++++++++++++++++++++++++')
        print('Reset the device...')
        re_reset = reset(device_id)
        if re_reset == -1:
            time.sleep(2)  # the first factory reset failed, wait 2s, fastboot reset
            re_reset = reset_fastboot(device_id)
        end_time = datetime.now()
        print('-------------------------------')
        print('Record the case information...')
        while True:
            re_log = log('normal-log-2.txt', tested_case_num, seed, op_seq, install_apk_comb, start_time, end_time)
            if re_log != -1:  # make sure that log successfully
                print('Record successfully.')
                break
            print('Record unsuccessfully, try again...')
        while (re_reset == -1):  # both [factory reset] and [fastboot -w] are failed
            time.sleep(20)  # make sure that the tested connection status is true
            re_con = testConnection(device_id)
            print('Connection status:', re_con)
            if re_con == 0:  # device does not enter the fastboot mode
                print('Device is on...')
                re_reset = reset_fastboot(device_id)  # fastboot reset
            else:  # device has entered the fastboot mode
                print('Has been in the fastboot mode...')
                re_reset = erase_fastboot(device_id)  # fastboot erase data
        print('------------------------------')
        print('Reset is complete!')

fuzzingNormal2()
