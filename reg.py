# coding=utf-8
import re
import winreg

def alter_reg(name,mode,location = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"):
    try:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, location, 0, access=winreg.KEY_WRITE)  # 写入模式
        except PermissionError as e:
            return "权限不足"

        if mode: #1 是gpu
            winreg.SetValueEx(key, "DeviceDesc", 0, winreg.REG_SZ, name.split('&&&&&')[0])
        else:
            winreg.SetValueEx(key, "ProcessorNameString", 0, winreg.REG_SZ, name)
        winreg.CloseKey(key)
        return "修改成功"

    except:
        return "未知错误"

def get_real_name(gpuNameDict):
    computerInfo = {}

    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
    value = winreg.QueryValueEx(key, "OldProcessorNameString")
    computerInfo['cpu'] = value[0]

    for i in range(len(gpuNameDict)):
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, gpuNameDict[i].split('&&&&&')[-1])
        value, type = winreg.QueryValueEx(key, "OldDeviceDesc")
        if ';' in value:
            value = value.split(';')[-1]

        computerInfo[i] = value + "&&&&&" + gpuNameDict[i].split('&&&&&')[-1]
        winreg.CloseKey(key)

    #AMD Ryzen 7 5800H with Radeon Graphics
    #NVIDIA GeForce RTX 3080 Laptop GPU;AMD Radeon(TM) Graphics

    return computerInfo

def searchReg(mode):
    location = [r"SYSTEM\CurrentControlSet\Enum\PCI",
                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"]
    if mode:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, location[mode])
            value = winreg.QueryValueEx(key , "ProcessorNameString")

            try:
                v= winreg.QueryValueEx(key, "OldProcessorNameString")
            except:
                try:
                    seriesNumKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                                  location[mode], 0,
                                                  access=winreg.KEY_WRITE)

                    winreg.SetValueEx(seriesNumKey, r"OldProcessorNameString", 0, winreg.REG_SZ, value[0].strip())
                    # winreg.SetValueEx(key, "ProcessorNameString", 0, winreg.REG_SZ, name)
                    winreg.CloseKey(seriesNumKey)
                except OSError:
                    return "创建键失败"
                winreg.CloseKey(key)
            winreg.CloseKey(key)
            return value[0].strip()

        except:
            return "获取失败"

    else:
        PCI = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,location[mode])

        item = 0
        gpuName = {}
        while True:
            try:
                VenName = winreg.EnumKey(PCI, item)
                item += 1
                VenKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, location[mode]+"\\"+VenName)
                seriesNum = winreg.EnumKey(VenKey,0)
                winreg.CloseKey(VenKey)

                seriesNumKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, location[mode]+"\\"+VenName + "\\" + seriesNum)


                try:
                    value = winreg.QueryValueEx(seriesNumKey, "DeviceDesc")

                    if re.findall('GeForce|radeon|Intel|gpu|RTX|GTX|quadro', value[0], re.IGNORECASE) and 'Wi-Fi' not in value[
                        0]:
                        num = int(winreg.QueryValueEx(seriesNumKey, "Driver")[0][-1])

                        gpuName[num] = value[0].strip() + "&&&&&" + location[mode] + "\\" + VenName + "\\" + seriesNum

                        try:
                            winreg.QueryValueEx(seriesNumKey, "OldDeviceDesc")
                        except:
                            try:
                                winreg.CloseKey(seriesNumKey)
                                seriesNumKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, location[mode]+"\\"+VenName + "\\" + seriesNum,0, access=winreg.KEY_WRITE)

                                winreg.SetValueEx(seriesNumKey, r"OldDeviceDesc", 0,winreg.REG_SZ, value[0])
                                # winreg.SetValueEx(key, "ProcessorNameString", 0, winreg.REG_SZ, name)
                            except OSError:
                                return "创建键失败"
                            winreg.CloseKey(seriesNumKey)

                except:
                    pass

            except:
                winreg.CloseKey(PCI)
                break

        return gpuName

def loadFile():
    configDict = {}
    for i in open('config.config','r',encoding='utf-8'):
        n = i.strip().split('=')
        configDict[n[0]] = n[1]
    return configDict

def saveFile(configDict):
    with open('config.config','w',encoding='utf-8') as f:
        for i in configDict:
            f.write(i + '=' + configDict[i] + '\n')

def isAdmin():
    txt = 1
    try:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", 0, access=winreg.KEY_WRITE)  # 写入模式
            txt = 0
        except PermissionError as e:
            txt =  1
    except:
        txt =  1

    try:
        winreg.CloseKey(key)
    except:
        pass

    return txt
# print(searchReg(0))
