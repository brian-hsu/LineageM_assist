from ModuleADB import ADB
from PIL import ImageGrab
from PIL import Image
import win32gui
from imagehash import phash
import imagehash
from ModuleMyLog import MyLOG
import os
import cv2
import numpy as np


class PIC:
    def __init__(self, path):
        self.ADB = ADB(path)
        # self.log = MyLOG(version_cycle='alpha', logger_name='LM').logger
        self.log = MyLOG(version_cycle='beta', logger_name='LM').logger
        smp_list = ['hp_bar_smp.png', 'kill_smp.png', 'red_water_smp.png', 'arrow_smp.png', 'bullet_smp.png']
        file_found = list()
        for i in range(len(smp_list)):
            if os.path.isfile(path + r'Sample/' + smp_list[i]):
                file_found.append(smp_list[i])
            else:
                file_found.append(False)
        self.log.debug(file_found)
        if False in file_found:
            print(u'在 %s 沒有找到 %s' % ((os.getcwd() + r'../Data/Sample'), smp_list))
            input('按 Enter 結束')
            exit(0)
        else:
            self.save_path = path
            self.sampleImage = {'hpBar': path + r'Sample/' + smp_list[0],
                                'kill': path + r'Sample/' + smp_list[1],
                                'redWater': path + r'Sample/' + smp_list[2],
                                'arrow': path + r'Sample/' + smp_list[3],
                                'bullet': path + r'Sample/' + smp_list[4]}
            self.log.debug(self.save_path)
            self.log.debug(self.sampleImage)

    def PIL_image_crop(self, name, screen, coordinate):
        # 裁切區域的 x 與 y 座標（左上角）
        x = int(coordinate['x'])
        y = int(coordinate['y'])
        # 裁切區域的長度與寬度
        w = int(coordinate['w'])
        h = int(coordinate['h'])
        # 裁切圖片 左起 右終
        PIL_crop = screen.crop([x, y, x + w, y + h])
        if name:
            PIL_crop.save(self.save_path + name + '_crop.png')
        return PIL_crop

    # my screen 1284 * 768
    def PIL_grab_image(self, hwnd, name=None, resize_w=1366, resize_h=768):
        self.log.debug(hwnd)
        resize = [resize_w, resize_h]
        # PIL 截圖 (windows api for py get bbox)
        PIL_image = ImageGrab.grab(bbox=win32gui.GetWindowRect(int(hwnd)))
        # PIL image resize
        PIL_image = PIL_image.resize(resize, Image.ANTIALIAS)

        if name:
            # PIL image save file
            PIL_image.save(self.save_path + name + '_screen.png')
        return PIL_image

    def cv_image_crop(self, screen, coordinate, name=None):
        # 裁切區域的 x 與 y 座標（左上角）
        x = int(coordinate['x'])
        y = int(coordinate['y'])
        # 裁切區域的長度與寬度
        w = int(coordinate['w'])
        h = int(coordinate['h'])
        # 裁切圖片 左起 右終
        cv_crop = screen[y:y+h, x:x+w]
        if name:
            (Image.fromarray(cv_crop)).save(self.save_path + name + '_NPcrop.png')
        return cv_crop

    def image_turn_cv(self, pil_image, name=None):
        open_cv_image = np.array(pil_image)
        # Convert RGB to BGR
        open_cv_image = open_cv_image[:, :, ::-1].copy()

        # open_cv_image = open_cv_image[:, :, ::-1].copy()
        # np_im = cv2.cvtColor(np_image, cv2.COLOR_BGR2BGRA)
        np_im = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2HSV)
        # np_im = cv2.cvtColor(np_image, cv2.COLOR_BGR2GRAY)

        if name:
            # 此為預設值，這種格式會讀取 RGB 三個 channels 的彩色圖片，而忽略透明度的 channel。
            # cv2.imwrite(self.save_path + name + '_CVscreen.png', cv2.IMREAD_COLOR)
            # 讀取圖片中所有的 channels，包含透明度的 channel。
            (Image.fromarray(np_im)).save(self.save_path + name + '_NPscreen.png')
        return np_im

    def hash_image_compare(self, img, sample_name, score_mode, opencv=None, my_hash_size=8):
        if opencv:
            img = Image.fromarray(img)
        hash_log = self.log.debug
        self.log.debug(self.sampleImage[sample_name])
        Sample_img = Image.open(self.sampleImage[sample_name])

        if score_mode == 'avgP':
            # use phash and average_hash sum
            pHash_sum = abs(imagehash.phash(Sample_img, hash_size=my_hash_size) - imagehash.phash(img, hash_size=my_hash_size))
            avgHash_sum = abs(imagehash.average_hash(Sample_img, hash_size=my_hash_size) - imagehash.average_hash(img, hash_size=my_hash_size))
            hash_log('pHash_sum : %s' % pHash_sum)
            hash_log('avgHash_sum : %s' % avgHash_sum)
            score = (pHash_sum * 2) + avgHash_sum
            hash_log(score)
            return score
        elif score_mode == 'P':
            score = abs(imagehash.phash(Sample_img) - imagehash.phash(img))
            hash_log('pHash_sum : %s' % score)
            hash_log(score)
            return score
        elif score_mode == 'avg':
            score = abs(imagehash.average_hash(Sample_img) - imagehash.average_hash(img))
            hash_log('avgHash_sum : %s' % score)
            hash_log(score)
            return score

    def detect_colors(self, hsv, low, up, name=None):
        lower = np.array(low)
        upper = np.array(up)
        # get mask
        mask = cv2.inRange(hsv, lower, upper)
        self.log.debug(mask)

        if name:
            (Image.fromarray(mask)).save(self.save_path + name + '_mask.png')
        return mask

    def white_count(self, mask, color_code):
        white_count = 0
        for np_list in mask:
            self.log.debug(np_list)
            for num in np_list:
                # self.log.info(num)
                if num == color_code:
                    white_count += 1
        self.log.debug(white_count)
        return white_count

if __name__ == "__main__":
    obj = PIC(path=r'./Data/')
    my_hwnd = obj.ADB.momo_hwnd()
    red_water ={'x': 1181, 'y': 648, 'w': 55, 'h': 64}
    kill = {'x': 1258, 'y': 383, 'w': 31, 'h': 7}
    hp_bar = {'x': 85, 'y': 22, 'w': 204, 'h': 14}
    arrow = {'x': 1080, 'y': 643, 'w': 69, 'h': 68}
    bullet = {'x': 1080, 'y': 643, 'w': 69, 'h': 68}
    red_low = [0, 225, 150]
    red_up = [0, 255, 255]

    #'''
    lm = obj.PIL_grab_image(hwnd=my_hwnd, name='LM')
    crop = obj.PIL_image_crop(name='kill', screen=lm, coordinate=kill)
    result = obj.hash_image_compare(crop, 'kill', score_mode='avgP', my_hash_size=3)

    '''
    lm = obj.PIL_grab_image(hwnd=my_hwnd, name='LM_now')
    cv_lm = obj.image_turn_cv(lm, 'LM_cv2')
    crop = obj.cv_image_crop(name='hp_bar', screen=cv_lm, coordinate=hp_bar)
    detect_colors = obj.detect_colors(crop, red_low, red_up, 'hp')
    count = obj.white_count(detect_colors, 255)
    # detect_colors = obj.detect_colors(crop, [10,255,127], [0,43,46], 'hp')
    # crop = obj.PIL_image_crop(name='hp_bar', screen=lm, coordinate=hp_bar)
    #print(obj.hash_image_compare(crop,'hpBar', score_mode='avgP', opencv='on'))
    '''
    '''
    compare = []
    import time
    for i in range(0, 45):
        lm = obj.PIL_grab_image(hwnd=my_hwnd, name='LM')
        crop = obj.PIL_image_crop(name='red_water', screen=lm, coordinate=red_water)
        result = obj.hash_image_compare(crop, 'redWater', score_mode='avgP')
        compare.append(result)
        time.sleep(0.5)
    print('AVG: %s' % np.mean(compare))
    print('max: %s' % np.max(compare))
    print('min: %s' % np.min(compare))
    '''


