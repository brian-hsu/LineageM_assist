import subprocess
from ModuleMyLog import MyLOG
import re
from linecache import getline
import os


class ADB:
    def __init__(self, momo_path):
        # self.log = MyLOG(version_cycle='alpha', logger_name='LM').logger
        self.log = MyLOG(version_cycle='beta', logger_name='LM').logger
        # with open(momo_path + 'my_momo.txt', 'r', encoding='UTF-8') as momo_path:

        if os.path.isfile(momo_path + 'my_momo.txt') is False:
            print(u'在 %s 沒有找到 my_momo.txt' % (os.getcwd() + momo_path))
            input('按 Enter 結束')
            exit(0)
        else:
            self.momo = dict()
            self.momo["path"] = getline(momo_path + 'my_momo.txt', 3).strip().split('=')[1]
            self.momo["index"] = (getline(momo_path + 'my_momo.txt', 4).strip()).split('=')[1]

    def call_adb(self, device_name, detail_list):
        command = [self.momo["path"] + r'/adb.exe', '-s', device_name]
        for order in detail_list:
            command.append(order)

        self.log.debug(command)
        subprocess.Popen(command)

    def call_ld(self, detail_list):
        command = [self.momo["path"] + r'/ld.exe', '-s', self.momo["index"]]
        for order in detail_list:
            command.append(order)

        self.log.debug(command)
        subprocess.Popen(command)

    def call_ldconsole(self, detail_list):
        command = [self.momo["path"] + r'/ldconsole.exe']
        for order in detail_list:
            command.append(order)

        self.log.debug(command)
        output = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, encoding='GBK'
        )
        self.log.debug(output)
        end = []
        for line in output.stdout.readlines():
            self.log.debug(line)
            if '\n' in line:
                line = line.strip()
            end.append(line)

        self.log.debug(end)

        return end

    def momo_hwnd(self):
        get_momo_list = self.call_ldconsole(["list2"])
        momo_open_format = re.compile(r"%s,.*,\d+,(\d+),\d+,\d+,\d+" % self.momo['index'])

        for my_momo in get_momo_list:
            if bool(momo_open_format.search(my_momo)) is True:
                self.momo['hwnd'] = momo_open_format.search(my_momo).group(1)

        if 'hwnd' not in self.momo:
            print(u'my_momo.txt 中 select_momo: %s, 沒有此模擬器開啟或編號錯誤' % self.momo['index'])
            input('按 Enter 結束')
            exit(0)
        else:
            return self.momo['hwnd']

    def ld_touch(self, btn_position):
        touch_cmd = ["input", "tap"]

        for position in btn_position:
            touch_cmd.append(position)

        self.call_ld(touch_cmd)

    def ldconsole_downcpu(self):
        self.call_ldconsole(["downcpu", "--index", self.momo["index"], "--rate", "50"])
        self.log.info("set down_cpu rate 50")


if __name__ == "__main__":
    obj = ADB(momo_path=r'../Data/')
