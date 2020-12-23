#!/usr/bin/ python
# -*- coding: utf-8 -*-
# Author YangHengyu
# creation date 2018-05-25

import codecs
import json
import random
import time
import os

import datetime

import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

import config

HERE = os.path.abspath(os.path.dirname(__file__))


class AutoLearn:
    def __init__(self, account, password, subject):
        self._name = "AutoLearn"
        self.browser = self.enable_flash()
        self.account = account
        self.password = password
        self.subject = subject

        self.learning_status = {}

    def go_login_page(self):
        browser = self.browser
        browser.get(config.START_URL)
        time.sleep(5)
        login_button = browser.find_element_by_class_name('top_bn01')
        login_button.click()
        time.sleep(2)

    def login(self):
        # found login elements
        input_username = self.browser.find_element_by_id("myusername")
        input_password = self.browser.find_element_by_id("mypassword")

        input_btn = self.browser.find_element_by_id("btnlogininput")

        time.sleep(1)
        input_username.click()
        input_username.clear()
        input_username.send_keys(self.account)

        input_password.click()
        input_password.clear()
        input_password.send_keys(self.password)

        time.sleep(1)
        input_btn.click()

        print '登录成功'

    def get_learning_status(self):
        self.learning_status[u'网上选课'] = 1

    def course_selection(self):
        go_course_center_btn = self.browser.find_element_by_xpath('//*[@id="ext-gen1140"]/div/a')
        on_search_subject = self.browser.find_element_by_id("txtkeyword")

        go_course_center_btn.click()
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.element_to_be_clickable((By.ID, "txtkeyword")))

        # 搜索对应科目的课程
        on_search_subject.click()
        on_search_subject.clear()
        on_search_subject.send_keys(self.subject)
        self.browser.find_element_by_name(u'确定').click()
        time.sleep(1)

    def courses_study(self):

        #self.browser.find_element_by_xpath('//*[@id="ext-gen1142"]/div/a').click()
        #self.browser.find_element_by_id('button-1034-btnInnerEl').click()

        browser = self.browser
        self.browser.get(config.STUDY_URL)
        time.sleep(1)

        list_handle = self.browser.current_window_handle

	#for index in range(len(study_btns)):
	#    study_btn = self.browser.find_elements_by_xpath('//*[@id="UpdatePanel1"]//td[4]/p[@class="xx_ben"]/a')[index]
	#    self.study_course_at(study_btn)

	try:
	    flag = 0
	    while flag > -1:
	        self.study_course_at(self.browser.find_element_by_xpath('//*[@id="UpdatePanel1"]//td[4]/p[@class="xx_ben"]/a'))
                # 切换回目录页面
                self.browser.switch_to.window(list_handle)
                self.browser.refresh()
                time.sleep(3)
	        flag += 1
        except NoSuchElementException as nsee:
            print '已经学完所有选择课程'
        except Exception as e:
            print '学习过程中出现异常: ', e
	finally:
	    print('auto learned ' + str(flag) + " courses")
	    self.browser.quit()
	    sys.exit(0)


    def study_course_at(self, study_btn):
	study_btn.click()

        # 切换到新页面
        self.browser.switch_to.window(self.browser.window_handles[1])
        try:
            WebDriverWait(self.browser, 10).until(EC.alert_is_present())
            time.sleep(1)
            self.browser.switch_to.alert.accept()
        except TimeoutException as e1:
            print '等待alert超时', e1
        except Exception as e:
            print '尝试等待并关闭alert异常', e

        # 如果页面正常加载完可以成功，但经常由于confirm将页面卡住
        #try:
        #    alert = self.browser.switch_to.alert
        #    print('取完了alert')
        #    time.sleep(1)
        #    alert.accept()
        #    print('关闭其他学习窗口提示')
        #except Exception as e:
        #    print '未找到弹窗，时间：', datetime.datetime.now(), e
        #    time.sleep(1)


        # 执行js使时间加速，2020-2021上起似乎添加了服务器验证，失效 
        #self.fast_forward_study_time()
        #while self.study_time() < 2700:
        #    time.sleep(62)
        #    try:
        #        self.browser.switch_to.alert.accept()
        #    except Exception as e:
        #        print '未找到学习过程弹窗，时间：', datetime.datetime.now(), e

        while self.study_time() < 2700:
            # 由于提交行为5分钟一次，所以5分钟查一次弹窗即可
            time.sleep(302)
            try:
                self.browser.switch_to.alert.accept()
                print '关闭学习过程弹窗，时间：', datetime.datetime.now()
            except Exception as e:
                print '未找到学习过程弹窗，时间：', datetime.datetime.now(), e

        time.sleep(1)
        self.write_comments()
        self.browser.close()
        time.sleep(2)

        #close_btn = self.browser.find_element_by_id("lhgdg_xbtn_lhgdgId")
        #close_btn.click()
        #time.sleep(3)	
        #self.browser.close();
        #time.sleep(2)

    def study_time(self):
        js = '''
        var time = alldatetime
        return time;
        '''
        return self.browser.execute_script(js)

    # 使用脚本加速时间
    def fast_forward_study_time(self):
        js = '''
        var speed = (function innerSpeed() {
            var b = $(window.document);
            if (Startime < 2700) {
                Startime += 300; 
                updata();
                setTimeout(function() {
                    innerSpeed();
                }, 60000);
            }
        });
        speed();
        '''
        self.browser.execute_script(js)
        #a.__doPostBack("lbtnStudentCourse", "") 
        # 写评论的逻辑，取element尚有问题
        #else {
        #        for (c = b.find("#UpdatePanel2").children("table").children("tbody").children("tr").eq(1).children("td").html(), d = 0; d < 24 / c.length; d++) c += c;
        #        b.find("#txtareainnertContents").val(c), b.find("#txtareaExperience").val(c), b.find("#btnaddRecord").click()
        #    }


    # 填写学习记录
    def write_comments(self):
        # 切换到弹窗iframe
        study_record_btn = self.browser.find_element_by_xpath('//*[@class="course-tab clearFix"]/div[2]')
        try:
            self.browser.switch_to.alert.accept()
        except Exception as e:
            print '点击评论按钮未找到学习过程弹窗，时间：', datetime.datetime.now(), e
        study_record_btn.click()
        time.sleep(1)

        content_point_area = self.browser.find_element_by_id('txtareainnertContents')
        experience_area = self.browser.find_element_by_id('txtareaExperience')

        content_point = self.gen_comments('content_point')
        experience = self.gen_comments('experience')

        try:
            self.browser.switch_to.alert.accept()
        except Exception as e:
            print '点击内容要点输入框未找到学习过程弹窗，时间：', datetime.datetime.now(), e
        content_point_area.click()
        content_point_area.clear()
        content_point_area.send_keys(content_point)
        time.sleep(2)

        try:
            self.browser.switch_to.alert.accept()
        except Exception as e:
            print '点击体会感悟输入框未找到学习过程弹窗，时间：', datetime.datetime.now(), e 
        experience_area.click()
        experience_area.clear()
        experience_area.send_keys(experience)
        time.sleep(2)

        try:
            self.browser.switch_to.alert.accept()
        except Exception as e:
            print '点击评论提交按钮时未找到学习过程弹窗，时间：', datetime.datetime.now(), e 
        self.browser.find_element_by_id('btnaddRecord').click()
        time.sleep(2)
        self.browser.switch_to.alert.accept()
	#self.browser.switch_to.parent_frame()

    def write_reading_notes(self):
        # current_handle = self.browser.current_window_handle
        #
        # for handle in self.browser.window_handles:
        #     if handle != current_handle:
        #         self.browser.switch_to.window(handle)

        # 点击读书评价
        self.browser.find_element_by_xpath('//*[@id="ext-gen1142"]/div/a').click()
        reading_note_frame = self.browser.find_element_by_id('fnode3')
        self.browser.switch_to.frame(reading_note_frame)
        # 点击新建
        self.browser.find_element_by_id('Paneldefault_panel_list_Grid_list_ctl00_CreatReadAss_btn-btnInnerEl').click()

    @staticmethod
    def enable_flash():
        # 设置默认启用flash
        chrome_options = Options()
        prefs = {
            "profile.managed_default_content_settings.images": 1,
            "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
            "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1,
        }

        chrome_options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(chrome_options=chrome_options)

        return driver

    @staticmethod
    def gen_comments(comment_type='experience'):
        file_name = HERE + '/comments.json'
        try:
            with codecs.open(file_name, 'r', encoding='utf-8') as file:
                comments = json.loads(file.read())
        except Exception as e:
            print e
            raise

        comments_num = len(comments[comment_type])
        print comments_num
        i = random.randint(0, comments_num-1)

        return comments[comment_type][i]


if __name__ == '__main__':
    auto_learn = AutoLearn(config.USER_NAME, config.PASSWORD, config.SUBJECT)
    auto_learn.go_login_page()
    auto_learn.login()
    time.sleep(2)
    auto_learn.courses_study()
    # auto_learn.write_comments()





