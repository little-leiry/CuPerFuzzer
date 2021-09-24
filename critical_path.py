import copy
import random
import csv
import time
import os
import subprocess
from operator import itemgetter

base_path = "E:/CuPerFuzzer/critical_path/"
apk_base_path1 = "E:/CuPerFuzzer/apk-1/"
apk_base_path2 = "E:/CuPerFuzzer/apk-2/"
android_9_path = "C:/Users/leiry/Desktop/walleye9"
android_10_path = "C:/Users/leiry/Desktop/walleye10"

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

def upgrade(device_id):
    # set the temporary environment variable
    os.environ['ANDROID_PRODUCT_OUT']=android_10_path # Android 10
    cmd_reboot='adb -s '+device_id+' reboot bootloader' # enter the fastboot mode
    cmd_flash='fastboot -s '+device_id+' flashall' # flash the image (not wipe the data)
    try:
        print('----------------------------------')
        print('Upgrade system...')
        subprocess.run(args=cmd_reboot,shell=True,check=True)
        subprocess.run(cmd_flash, shell=True, check=True)
        time.sleep(45) # wait for rebooting
        return 0
    except Exception as e:
        print('Upgrading error:',e)
        return -1

def downgrade(device_id):
    os.environ['ANDROID_PRODUCT_OUT']=android_9_path # Android 9
    cmd_bootloader='adb -s '+device_id+' reboot bootloader' # enter the fastboot mode
    cmd_flash='fastboot -s '+device_id+' -w flashall' # flash the image (wipe the data)
    try:
        print('----------------------------------')
        print('Downgrade system...')
        subprocess.run(args=cmd_bootloader,shell=True,check=True)
        subprocess.run(cmd_flash, shell=True, check=True)
        time.sleep(69) # wait for rebooting
        return 0
    except Exception as e:
        print('Downgrading error:',e)
        return -1

def flash_fastboot(device_id):
    os.environ['ANDROID_PRODUCT_OUT']=android_9_path # Android 9
    cmd_flash='fastboot -s '+device_id+' -w flashall' # flash the image (wipe the data)
    try:
        print('----------------------------------')
        print('Fastboot flash image...')
        subprocess.run(cmd_flash, shell=True, check=True)
        time.sleep(69) # wait for rebooting
        return 0
    except Exception as e:
        print('Flashing error:',e)
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
            print('Factory reset error,enter fastboot...')
            re=reset_fastboot(device_id)
            return re
        time.sleep(45)
        return 0
    except Exception as e:
        print("Factory reset error:", e)
        return -1

def simulateClick(packageName,device_id):
    cmd_open = 'adb -s ' + device_id + ' shell am start -n' + packageName + '/.MainActivity'
    cmd_click = 'adb -s ' + device_id + ' shell input tap 478 807'
    try:
        print('----------------------------------')
        print('Click to request permissions...')
        while True:
            # open the app
            re = subprocess.run(args=cmd_open, shell=True, stderr=subprocess.PIPE, encoding='gbk')
            err = re.stderr
            if 'Error type 3' not in err:
                print('Open app successfully.')
                time.sleep(1)
                # click
                subprocess.run(args=cmd_click, shell=True, check=True)
                print('Click successfully.')
                time.sleep(1.5)  # wait for granting all permissions
                return 0
            # open the app unsuccessfully, wait 1s, try again
            print('Open app unsuccessfully, try again.')
            time.sleep(1)
    except Exception as e:
        print("Clicking error:", e)
        return -1

def resetForUpgrade(device_id):
    re_reset = downgrade(device_id)
    if re_reset == -1:
        # the first downgrade failed
        while True:  # repeat until reset successfully
            time.sleep(20)  # make sure that the tested connection status is true
            re_con = testConnection(device_id)
            print('Connection status:', re_con)
            if re_con == 0:  # device does not enter the fastboot mode
                print('Device is on...')
                re_reset = downgrade(device_id)  # enter the fastboot mode and flash the image
            else:  # device has entered the fastboot mode
                print('Has been in fastboot mode...')
                re_reset = flash_fastboot(device_id)  # flash the image
            if re_reset != -1:
                break

def resetForNormal(device_id):
    re_reset = reset(device_id)
    if re_reset == -1:
        # the first factory reset failed
        while True:  # repeat until reset successfully
            time.sleep(20)  # make sure that the tested connection status is true
            re_con = testConnection(device_id)
            print('Connection status:', re_con)
            if re_con == 0:  # device does not enter the fastboot mode
                print('Enter fastboot reset...')
                re_reset = reset_fastboot(device_id)  # fastboot reset
            else:  # device has entered the fastboot mode
                print('Has been in fastboot mode...')
                re_reset = erase_fastboot(device_id)  # fastboot erase data
            if re_reset != -1:
                break

# verification
def openFile(file_name):
    file_path=base_path+file_name
    f = open(file_path, 'r')
    file = f.readlines()
    f.close()
    return file

def getCusperProtSystem(file_name):
    file=openFile(file_name)
    for i in range(len(file)):
        if "permission:com.leiry.TEST" in file[i]:
            cp_prot=file[i+4].split()[0].split(':')[1]
            return cp_prot
    return 'null' # the permission definition is not in the system

def getCusperProtOwner(file_name):
    file=openFile(file_name)
    for i in range(len(file)):
        if "com.leiry.TEST: prot=" in file[i]:
            if "INSTALLED" in file[i]:
                cp_prot=file[i].split(':')[1].split(',')[0].split('=')[1]
                return cp_prot
    return 'null'

def getGrantedInstallPer(file_name):
    file=openFile(file_name)
    i=0
    install_granted = []
    while(i<len(file)):
        if file[i]=='    install permissions:\n':
            i=i+1
            while(i<len(file) and '    User 0:' not in file[i]):
                if "granted=true" in file[i]:
                    per=file[i].split(':')[0].split()[0]
                    install_granted.append(per)
                i=i+1
            return install_granted
        i=i+1
    return install_granted

def getGrantedRuntimePer(file_name):
    file=openFile(file_name)
    i=0
    runtime_granted = []
    while(i<len(file)):
        if file[i]=='      runtime permissions:\n':
            i=i+1
            while(i<len(file) and file[i]!='\n'):
                if "granted=true" in file[i]:
                    per=file[i].split(":")[0].split()[0]
                    runtime_granted.append(per)
                i=i+1
            return runtime_granted
        i=i+1
    return runtime_granted

# verify if the case is effective for single-app mode
def verifyCase1(packageName,device_id):
    #get the information of the app
    file_name="info.txt"
    cmd_dump="adb -s "+device_id+" shell dumpsys package "+packageName+" > "+base_path+file_name
    try:
        print('----------------------------------')
        print('Verify test case...')
        subprocess.run(args=cmd_dump,shell=True,check=True)
        install_granted=getGrantedInstallPer(file_name)
        runtime_granted=getGrantedRuntimePer(file_name)
    except Exception as e:
        print("Verification error:",e)
        return -1
    granted_per=[]
    for per in install_granted:
        if per != 'com.leiry.TEST': # normal/signature, granted automatically
            granted_per.append(per+'(signature)')
    for per in runtime_granted:
        granted_per.append(per+'(dangerous)')
    return granted_per

# verify if the case is effective for dual-app mode
def verifyCase2(declared_app,requested_app,device_id):
    # get the declared permissions' information in the system
    file_permission = "system.txt"
    cmd_system = "adb -s "+device_id+" shell pm list permissions -f -g > "+base_path+file_permission
    # get the information of the app
    file_declared = "declared.txt"
    file_requested = "requested.txt"
    cmd_dump_declared = "adb -s "+device_id+" shell dumpsys package "+declared_app+" > "+base_path+file_declared
    cmd_dump_requested = "adb -s " + device_id + " shell dumpsys package " + requested_app + " > " + base_path + file_requested
    try:
        print("----------------------------------")
        print("Verify test case...")
        # get requested app information
        subprocess.run(args=cmd_dump_requested,shell=True,check=True)
        install_granted=getGrantedInstallPer(file_requested)
        runtime_granted=getGrantedRuntimePer(file_requested)
        # get custom permission protection level
        try:
            subprocess.run(cmd_system, shell=True, check=True) # major way
            cusper_pl=getCusperProtSystem(file_permission)
        except:
            print("Get system permissions' info unsuccessfully, get app's info...")
            subprocess.run(cmd_dump_declared, shell=True, check=True) # alternative way
            cusper_pl=getCusperProtOwner(file_declared)
    except Exception as e:
        print("Verification error:",e)
        return -1
    granted_per=[]
    for per in install_granted:
        if per=="com.leiry.TEST":
            if cusper_pl!="signature": # only signature custom permission is valid
                continue
        granted_per.append(per+"(signature)")
    for per in runtime_granted:
        granted_per.append(per+"(dangerous)")
    return granted_per

# execute the test case in single-app mode
def executeCase1(op_seq,install_apk_comb,device_id):
    app='com.leiry.simulateclick'
    app_id=0
    i=0
    #execute operations
    while(i<len(op_seq)):
        if op_seq[i]=='1':
            install_apk=apk_base_path1+install_apk_comb[app_id]
            re=install(install_apk,device_id)
            app_id = app_id + 1
        elif op_seq[i]=='2':
            re=uninstall(app,device_id)
        elif op_seq[i]=='3':
            re=upgrade(device_id)
        elif op_seq[i] == '4':
            re=reboot(device_id)
        if re!=-1: # the last operation is successful, then next
            i=i+1
        else:
            return -1
    #request permissions by simulating the click of a button
    click_result=simulateClick(app,device_id)
    if click_result==-1:
        return -1
    # verify if it is an effective case
    granted_per=verifyCase1(app,device_id)
    if granted_per == -1:
        return -1
    if len(granted_per) != 0:
        effective = ','.join(granted_per)
    else:
        effective = 'no'
    print('Granted permissions:', effective)
    return effective

#execute the test case in dual-app mode
def executeCase2(op_seq,install_apk_comb,device_id):
    declared_app = "com.leiry.declared"
    requested_app = "com.leiry.simulateclick"
    requested_apk = "E:/CuPerFuzzer/simulateClick.apk"
    app_id = 0
    i = 0
    # execute operations
    while (i < len(op_seq)):
        if op_seq[i] == '1':
            install_apk = apk_base_path2 + install_apk_comb[app_id]
            re = install(install_apk, device_id)
            app_id = app_id + 1
            # install the requested app at the beginning
            # install the declared app first and then the requested app
            if re != -1 and i == 0:
                re = install(requested_apk, device_id)
        elif op_seq[i] == '2':
            re = uninstall(declared_app, device_id)
        elif op_seq[i] == '3':
            re = upgrade(device_id)
        elif op_seq[i] == '4':
            re = reboot(device_id)
        if re != -1:  # the last operation is successful, then next
            i = i + 1
        else:
            return -1
    # request permissions by simulating the click of a button
    click_result = simulateClick(requested_app, device_id)
    if click_result == -1:
        return -1
    # verify if it is an effective case
    granted_per = verifyCase2(declared_app, requested_app, device_id)
    if granted_per == -1:
        return -1
    if len(granted_per) != 0:
        effective = ','.join(granted_per)
    else:
        effective = 'no'
    return effective

def storeCSV(store_name,info):
    store_path=base_path+store_name
    f=open(store_path,'a',newline='')
    writer=csv.writer(f)
    writer.writerow(info)
    f.close()

# 1-installation, 2-uninstallation, 3-OS update, 4-reboot
# rules: 1-the first operation is installation
# 2-meaningful uninstallation, 3-discontinuous reboots,
# 4-existential test app (for single-app mode)
def isMeaningfulCase(op_seq, seed_mode):
    if op_seq[0] != '1': # rule 1
        return False
    app_num = 0
    for i in range(len(op_seq)):
        if op_seq[i] == '1':
            app_num = 1
        elif op_seq[i] == '2': # rule 2
            if app_num == 0:
                return False
            app_num = 0
        elif op_seq[i] == '4': # rule 3
            if i+1 < len(op_seq):
                if op_seq[i+1] == '4':
                    return False
    if app_num == 0 and seed_mode == 'single-app': # rule 4
        return False
    return True

def getEffectiveCases(file_name):
    file_path = base_path +file_name
    file = csv.reader(open(file_path))
    effective_cases = []
    for item in file:
        if 'op_sequence' in item:
            continue
        effective_cases.append(item)
    return effective_cases

# Classify test cases
def classification(cases):
    classes = {}
    for case in cases:
        granted_permission = case[3]
        if classes.get(granted_permission) == None:
            classes[granted_permission]=[case]
        else:
            classes[granted_permission].append(case)
    return classes

# Find critical path
def candidateCases(_class):
    candidate_cases = []
    shortest_op_len = _class[0][1]
    for case in _class:
        op_len = case[1]
        if (op_len == shortest_op_len):
            candidate_cases.append(case)
        else:
            break
    return candidate_cases

def isCriticalPath(op_seq, install_apk_comb, granted_permission, seed_mode):
    app_id = 0
    for i in range(len(op_seq)): # delete each op
        pruned_op_seq = copy.deepcopy(op_seq)
        pruned_install_apk_comb = copy.deepcopy(install_apk_comb)
        # if the deleted operation is installation, delete the corresponding apk
        if op_seq[i] == '1':
            del(pruned_install_apk_comb[app_id])
            app_id+=1
        del(pruned_op_seq[i])
        print('----------------------------------')
        print('Pruned case:', pruned_op_seq, ',', pruned_install_apk_comb)
        # execute the pruned case
        if isMeaningfulCase(pruned_op_seq, seed_mode) == True:
            print('Pruned case is meaningful, execute it.')
            device_id = 'FA79K1A07801'
            if '3' in op_seq:
                device_id = 'FA79C1A03664' # for upgrading
            while True:
                if seed_mode == 'single-app':
                    result = executeCase1(pruned_op_seq, pruned_install_apk_comb, device_id)
                elif seed_mode == 'dual-app':
                    result = executeCase2(pruned_op_seq, pruned_install_apk_comb, device_id)
                # reset the device
                if '3' in op_seq:
                    resetForUpgrade(device_id)
                else:
                    resetForNormal(device_id)
                if result != -1:
                    break
                print('Execute the pruned case unsuccessfully, try again...')
        else:
            print('Pruned case is not meaningful.')
            continue
        print('----------------------------------')
        if result == granted_permission: # same execution result
            print('Same execution result.')
            return False, pruned_op_seq, pruned_install_apk_comb
        else:
            print('Different execution result.')
    return True, op_seq, install_apk_comb

def extractCriticalPath(op_seq, install_apk_comb, granted_permission, seed_mode):
    if len(op_seq) > 2: # a test case has at least two operations
        re, op_seq, install_apk_comb = isCriticalPath(op_seq, install_apk_comb, granted_permission, seed_mode)
        while (re == False):
            re, op_seq, install_apk_comb = isCriticalPath(op_seq, install_apk_comb, granted_permission, seed_mode)
    return op_seq, install_apk_comb

# Delete duplicated cases
def isDuplicated(critical_path, op_seq):
    if ','.join(critical_path) in ','.join(op_seq): # the case absolutely contains critical path
        return True
    if len(critical_path) > len(op_seq): # case's operations should be more than that of critical path
        return False
    # the case should contain the critical path's operations
    for op_type in ['1', '2', '3', '4']:
        num_critical_path = critical_path.count(op_type)
        num_op_seq = op_seq.count(op_type)
        if num_op_seq < num_critical_path:
            return False
    # operations' relative positions should be the same
    i = 0
    while(i < len(op_seq)):
        if op_seq[i] == critical_path[0]:
            if i + len(critical_path) > len(op_seq):
                return False
            critical_path = critical_path[1:]
            if len(critical_path) == 0:
                return True
        i = i+1
    return False

def deleteDuplicatedCases(_class, critical_path, class_id):
    _class_0 = copy.deepcopy(_class)
    for case in _class_0:
        op_seq = case[0].split(',')
        if isDuplicated(critical_path, op_seq) == True:
            _class.remove(case)
            del(case[1]) # do not store the operation length
            del(case[3]) # do not store the click result
            case.append(','.join(critical_path))
            case.append(class_id)
            storeCSV('critical_path.csv', case)

def main():
    file_name = 'effective_case_1.csv'
    cases = getEffectiveCases(file_name)
    classes = classification(cases)
    class_id = 0
    info = ['op_sequence', 'install_apk_comb', 'granted_permission',
              'seed_mode', 'critical_path', 'class']
    storeCSV('critical_path.csv', info)
    for _class in classes.values():
        # sort effective cases by the length of operation sequence
        _class = sorted(_class, key=itemgetter(1), reverse=False)
        while len(_class) != 0:
            class_id += 1
            candidate_cases = candidateCases(_class)
            candidate_case = random.choice(candidate_cases)
            op_seq = candidate_case[0].split(',')
            install_apk_comb = candidate_case[2].split(',')
            granted_permission = candidate_case[3]
            seed_mode = candidate_case[-1]
            print('++++++++++++++++++++++++++++++++++++++++++++++++')
            print('Class:', class_id)
            print('Granted permissions:', granted_permission)
            print('Candidate case:', op_seq, ",", install_apk_comb)
            critical_path, install_apk_comb = extractCriticalPath(op_seq, install_apk_comb, granted_permission, seed_mode)
            print('----------------------------------')
            print('Critical path:', critical_path, ',', install_apk_comb)
            info = [','.join(critical_path), ','.join(install_apk_comb), granted_permission, seed_mode, '/', class_id]
            storeCSV('critical_path.csv', info)
            deleteDuplicatedCases(_class, critical_path, class_id)
    print('++++++++++++++++++++++++++++++++++++++++++++++++')
    print('Done.')

main()
