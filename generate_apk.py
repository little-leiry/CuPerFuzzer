import shutil
import subprocess

base_path='E:/CuPerFuzzer/'
apk_template_path=base_path+'sim/'
xml_path=apk_template_path+'AndroidManifest.xml'
txt_path=apk_template_path+'AndroidManifest.txt'

def xml2txt():
    #rename to .txt
    new_path=xml_path.replace('xml','txt')
    shutil.move(xml_path, new_path)

def txt2xml():
    # rename to .xml
    new_path = txt_path.replace('txt', 'xml')
    shutil.move(txt_path, new_path)

def openTxt(file_path):
    f=open(file_path,'r')
    file=f.readlines()
    f.close()
    return file

def storeTxt(store_path,store_info):
    f=open(store_path,'w+')
    f.writelines(store_info)
    f.close()

def changeTxt(changed_info):
    infos=openTxt(txt_path)
    infos[1]=changed_info
    storeTxt(txt_path,infos)

def pack():
    cmd_pack='java -jar ' + base_path + 'apktool.jar b '+ apk_template_path
    subprocess.run(args=cmd_pack,shell=True,check=True)

def sign(apk_name):
    key_path=base_path + 'request.jks'
    apk_path=apk_template_path+'dist/simulateclick.apk'
    signed_apk_path=base_path+apk_name
    cmd_sign='jarsigner -verbose -keystore '+key_path+' -storepass 123456 -keypass 123456 -signedjar '+signed_apk_path+' '+apk_path+' key00'
    subprocess.run(args=cmd_sign,shell=True,check=True)

def main():
    apk_num=0
    pgs=['ACTIVITY_RECOGNITION', 'CALENDAR', 'CALL_LOG', 'CAMERA', 'CONTACTS', 'LOCATION', 'MICROPHONE',
     'NULL', 'PHONE', 'SENSORS', 'SMS', 'STORAGE', 'UNDEFINED']
    pls=['normal', 'dangerous', 'signature']
    names=['TEST', 'ACTIVITY_RECOGNITION', 'MANAGE_APPOPS']
    for name in names:
        if name=='TEST':
            per_name='com.leiry.TEST'
        else:
            per_name='android.permission.'+name
        for pl in pls:
            for pg in pgs:
                if pg=='NULL':
                    changed_info='    <permission android:name="'+per_name+'" android:protectionLevel="'+pl+'"'+'/>\n'
                    apk_name=name+'-'+pl+'-NULL.apk'
                else:
                    changed_info='    <permission android:name="'+per_name+'" android:permissionGroup="android.permission-group.'+pg+'" android:protectionLevel="'+pl+'"/>\n'
                    apk_name=name+'-'+pl+'-'+pg.split('.')[-1]+'.apk'
                apk_num+=1
                print("Build APK:", apk_name)
                try:
                    xml2txt()
                    changeTxt(changed_info)
                    txt2xml()
                    pack()
                    sign(apk_name)
                except Exception as e:
                    print('Error:', e)
                    break
                print('apk num:', apk_num)
    # build the app that does not declare a custom permission (i.e., remove the custom permission definition)
    apk_name = 'NULL-NULL-NULL.apk'
    changed_info = '\n'
    print("Build APK:", apk_name)
    try:
        xml2txt()
        changeTxt(changed_info)
        txt2xml()
        pack()
        sign(apk_name)
    except Exception as e:
        print('Error:', e)
    apk_num+=1
    print('apk num:', apk_num)

main()
