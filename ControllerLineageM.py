from ModuleADB import ADB
from ModulePic import PIC
from ModuleMyLog import MyLOG
import threading
import time
from datetime import datetime
from linecache import getline
import os


class LM:
    def __init__(self, path):
        if os.path.isfile(path + 'my_momo.txt') is False:
            print(u'在 %s 沒有找到 my_momo.txt' % (os.getcwd() + path))
            input('按 Enter 結束')
            exit(0)
        else:
            self.path = path
            self.ADB = ADB(momo_path=path)
            # self.log = MyLOG(version_cycle='alpha', logger_name='LM').logger
            self.log = MyLOG(version_cycle='beta', logger_name='LM').logger

            self.rangedWeapon = int(getline(path + 'my_momo.txt', 5).strip().split('=')[1]) - 1
            self.killCheck = int(getline(path + 'my_momo.txt', 6).strip().split('=')[1])

            self.btn_map = {'F1': ['541', '635'], 'F2': ['623', '635'], 'F3': ['705', '635'], 'F4': ['787', '635'],
                       'F5': ['960', '635'], 'F6': ['1042', '635'], 'F7': ['1125', '635'], 'F8': ['1205', '635'],
                       'menu': ['1236', '43']}

            self.PIC = PIC(path=path)
            self.LM_screen_th = list()
            self.LM_screen_th_run = 0
            self.hwnd = self.ADB.momo_hwnd()
            self.LM_screen = None
            self.ADB.ldconsole_downcpu()


    def go_thread(self):
        self.LM_screen_th.append(threading.Thread(target=self.get_LM_screen, name='LM_screen'))
        self.LM_screen_th.append(threading.Thread(target=self.check_redwater, name='check_redwater'))
        self.LM_screen_th.append(threading.Thread(target=self.check_hp_bar, name='check_hp_bar'))
        if self.killCheck == 1:
            self.LM_screen_th.append(threading.Thread(target=self.check_kill, name='check_kill'))
        if self.rangedWeapon != -1:
            self.LM_screen_th.append(threading.Thread(target=self.check_ranged_weapon, name='check_ranged_weapon'))
        for thread in self.LM_screen_th:
            thread.start()
            time.sleep(2)

        self.log.info('run LM_screen_th done')

    def get_LM_screen(self):
        start_time = time.time()
        while self.LM_screen_th_run == 0:
            self.LM_screen = self.PIC.PIL_grab_image(hwnd=self.hwnd, name=None)
            time.sleep(1)
        stop_time = time.time()
        total_time = stop_time - start_time
        m, s = divmod(total_time, 60)
        h, m = divmod(m, 60)
        print(u"執行總時間為 %02d:%02d:%02d" % (h, m, s))

    def check_hp_bar(self):
        hp_bar = {'x': 80, 'y': 20, 'w': 214, 'h': 17}
        hp_bar_cvimg = self.PIC.image_turn_cv(self.LM_screen)
        crop = self.PIC.cv_image_crop(screen=hp_bar_cvimg, coordinate=hp_bar)
        # red_low = [0, 43, 46]
        red_low = [0, 225, 150]
        # red_up = [1, 255, 255]
        red_up = [0, 255, 255]
        mask = self.PIC.detect_colors(crop, red_low, red_up)
        first_white_count = self.PIC.white_count(mask, 255)
        limit_count = int(first_white_count * 0.55)
        self.log.info('limit_count: %s' % limit_count)
        while self.LM_screen_th_run == 0:
            hp_bar_cvimg = self.PIC.image_turn_cv(self.LM_screen)
            crop = self.PIC.cv_image_crop(screen=hp_bar_cvimg, coordinate=hp_bar)
            mask = self.PIC.detect_colors(crop, red_low, red_up)
            white_count = self.PIC.white_count(mask, 255)
            self.log.debug('white_count: %s' % white_count)
            if white_count <= limit_count:
                self.LM_screen.save(self.path + 'no_hp_%s.png' % (datetime.now().strftime('%Y-%m-%d_%H.%M.%S')))
                print(u'%s 快沒血了，回村(F8), 數值: %s' % (datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), white_count))
                self.log.info(u'%s 快沒血了，回村(F8), 數值: %s' % (datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), white_count))
                print(u'當下畫面為: no_hp_%s.png' % (datetime.now().strftime('%Y-%m-%d_%H.%M.%S')))
                self.log.info(u'當下畫面為: no_hp_%s.png' % (datetime.now().strftime('%Y-%m-%d_%H.%M.%S')))
                self.ADB.ld_touch(btn_position=self.btn_map['F8'])
                self.log.info(u'%s 快沒血了，回村(F8)' % (datetime.now().strftime('%Y-%m-%d_%H:%M:%S')))
                self.LM_screen_th_run = 1
            time.sleep(2.5)

    def check_redwater(self):
        while self.LM_screen_th_run == 0:
            red_water = {'x': 1181, 'y': 648, 'w': 55, 'h': 64}
            red_water_img = self.PIC.PIL_image_crop(screen=self.LM_screen, coordinate=red_water, name=None)
            score = self.PIC.hash_image_compare(img=red_water_img, sample_name='redWater', score_mode='avgP')
            self.log.debug('red: %s' % score)
            if score <= 16:
                print(u'%s 沒水了，回村(F8), 數值:%s' % (datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), score))
                self.log.info(u'%s 沒水了，回村(F8), 數值:%s' % (datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), score))
                self.ADB.ld_touch(btn_position=self.btn_map['F8'])
                self.log.info(u'%s 沒水了，回村(F8)' % (datetime.now().strftime('%Y-%m-%d_%H:%M:%S')))
                self.LM_screen_th_run = 1
            time.sleep(2)

    def check_ranged_weapon(self):
        score = [19, 20]
        cus_str = [u'沒有銀箭了，回村(F8)', u'沒有銀彈了，回村(F8)']
        sample = ['arrow', 'bullet']
        coordinate = [{'x': 1080, 'y': 643, 'w': 69, 'h': 68}, {'x': 1080, 'y': 643, 'w': 69, 'h': 68}]

        while self.LM_screen_th_run == 0:
            ranged_weapon_img = self.PIC.PIL_image_crop(screen=self.LM_screen, coordinate=coordinate[self.rangedWeapon], name=None)
            hash_score = self.PIC.hash_image_compare(img=ranged_weapon_img, sample_name=sample[self.rangedWeapon], score_mode='avgP')
            self.log.debug('hash_score: %s' % hash_score)
            if hash_score < score[self.rangedWeapon]:
                print(u'%s %s, 數值: %s' % (datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), cus_str[self.rangedWeapon], hash_score))
                self.log.info(u'%s %s, 數值: %s' % (datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), cus_str[self.rangedWeapon], hash_score))
                self.ADB.ld_touch(btn_position=self.btn_map['F8'])
                self.log.info(u'%s %s' % (datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), cus_str[self.rangedWeapon]))
                self.LM_screen_th_run = 1
            time.sleep(5)

    def check_kill(self):
        kill_wait = 16
        count = 0
        while self.LM_screen_th_run == 0:
            # kill = {'x': 1181, 'y': 357, 'w': 13, 'h': 8}
            # kill = {'x': 1182, 'y': 358, 'w': 12, 'h': 7}
            kill = {'x': 1258, 'y': 383, 'w': 31, 'h': 7}
            kill_img = self.PIC.PIL_image_crop(screen=self.LM_screen, coordinate=kill, name=None)
            score = self.PIC.hash_image_compare(img=kill_img, sample_name='kill', score_mode='avg')

            if score > 20:
                print(u'檢查打怪(kill): %s 沒有打到怪，順飛(F1), 目前數值: %s' % (datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), score))
                self.log.info(u'檢查打怪(kill): %s 沒有打到怪，順飛(F1), 目前數值: %s' % (datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), score))
                self.ADB.ld_touch(btn_position=self.btn_map['F1'])
                count += 1
                print(u'檢查打怪(kill): %s秒後檢查' % (kill_wait * 2))
                print('----------------')
                time.sleep(kill_wait * 2)
            else:
                print(u'檢查打怪(kill): %s秒後檢查, 目前數值: %s' % (kill_wait, score))
                print('----------------')
                time.sleep(kill_wait)

        self.log.info(u'順飛了 %s 次' % count)




if __name__ == '__main__':
    obj = LM(path=r'../Data/')
    obj.go_thread()
    print('main done')
