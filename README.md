# CuPerFuzzer

A black-box fuzzer to detect custom permission related privilege escalation vulnerabilities in Android. 

- Default running environment: `Windows 10`.
- Default test phone model: `Google Pixel 2`.
- Default test Android OS version: `Android 10`.

------

### **Test App Dataset**: 

- `apk-1`: test apps for the *single-app* mode (apps both declaring and requesting permissions).
- `apk-2`: test apps for the *dual-app* mode (apps only declaring permissions).
- `simulateclick.apk`: the app requesting permissions for the *dual-app* mode.
- `generate_apk.py`: generate test apps.
- `sim`: the test app template for the *single-app* mode and *dual-app* mode.
- `declared`: the test app template for the *dual-app* mode.

### **Fuzzing Test**:

- `normal-1.py`: generate and execute the test case **without the OS update operation** for the *single-app* mode.
- `normal-2.py`: generate and execute the test case **without the OS update operation** for the *dual-app* mode.
- `upgrade-1.py`: generate and execute the test case **containing the OS update operation** for the *single-app* mode.
- `upgrade-2.py`: generate and execute the test case **containing the OS update operation** for the *dual-app* mode.
- `critical_path.py`: extract critical paths from effective cases.

------

### **Running Environment Setup**:

- Install Python 3.8 ([https://www.python.org/](https://www.python.org/)).

- According to your phone model, compile two versions of Android OS images based on the source code of AOSP Android 9 and 10. Note that you should:

(1)  In `frameworks/base/packages/SettingsProvider/res/values/defaults.xml`, change the value of `def_screen_off_timeout` to **2147483646**, and change the value of `def_lockscreen_disabled` to **true**.

(2) In `/build/make/core/main.mk`, change the value of `ro.adb.secure`  to **0**.

(3) Build the image with the `userdebug` type option.

So that the compiled Android OS images can disable the screen lock, keep `adb` always open, and skip the `adb` authorization step.

References for building Android :

(1) [Establishing a Build Environment](https://source.android.com/setup/build/initializing)

(2) [Downloading the Source](https://source.android.com/setup/build/downloading)

(3) [Building Android](https://source.android.com/setup/build/building)

- Add the `platform-tools` (platform-tools_r30.0.3-windows/platform-tools) to your `PATH` environment variable and ensure that the `adb` and `fastboot` commands  can be executed successfully.

  <img src="https://github.com/little-leiry/CuPerFuzzer/blob/f8d909cc3bbded9eddb31c7c924db4118647e07f/adb.JPG" style="zoom:100%;" />	

  <img src="E:\CuPerFuzzer\fastboot.JPG" style="zoom:100%;" />	

You can download the latest `platform-tools` for Windows, Mac, or Linux at  [https://developer.android.com/studio/releases/platform-tools](https://developer.android.com/studio/releases/platform-tools).

- Install the latest `JDK` and add it to your `PATH` environment variable. Make sure that the `jarsigner` command can be executed successfully.![image-20210922191503642](C:\Users\leiry\AppData\Roaming\Typora\typora-user-images\image-20210922191503642.png)	

`JDk` download link: [Java Downloads | Oracle](https://www.oracle.com/java/technologies/downloads/)

------

**Notes**:

- Replace the paths referred to in these python files with your own paths.

- Replace the value of `device_id` in these  python files with your devices' IDs. Execute `adb devices` to get them.

  ![](E:\CuPerFuzzer\adb_device.JPG)	

- Adjust the `reset()` function in `normal-1.py` ,  `normal-2.py`, and `critical_path.py` based on the location of the button `Erase all data` of your test phone.

- Adjust the value of `sleep.wait` in these python files based on your test phone's response time, such as the reboot time.

