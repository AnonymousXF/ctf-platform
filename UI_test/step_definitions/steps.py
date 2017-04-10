# -*- coding:utf-8 -*-
from lettuce import *  
from lettuce_webdriver.util import assert_false  
from lettuce_webdriver.util import AssertContextManager  
import time 

def input_frame(browser, attribute):
    xpath = "//input[@id='%s']" % attribute  
    elems = browser.find_elements_by_xpath(xpath)  
    return elems[0] if elems else False  

def click_button(browser,attribute):
    xpath = "//input[@id='%s']" % attribute
    elems = browser.find_elements_by_xpath(xpath)
    return elems[0] if elems else False
# open url
@step ('I go to \"(.*)\"')
def go_to(step,url):
    world.browser.get(url)

# # check keyword
# @step('Then I should see \"(.*)\" within 2 second')
# def then_i_should_see(step,keyword):
#     assert_equals(contains_content(world.browser, keyword))
@step('I check the checkbox which id is \"(.*)\"')
def click_input(step,id):
    cmd = "document.getElementById('"+id+"').click()"
    world.browser.execute_script(cmd)

@step("I click href with \"(.*)\"")
def click_id_with(step,number):
    world.browser.find_elements_by_xpath("//a")[int(number)-1].click()

@step("I click href with logout")
def click_with_logout(step):
    world.browser.find_elements_by_xpath("//p/a")[0].click()

@step('I fill the (.*) input with \"(.*)\"')
def fill_the_input(step,number,value):
    number = int(number)
    world.browser.find_elements_by_xpath("//input")[number-1].send_keys(value)

@step('I fill the (.*) input with number \"(.*)\"')
def fill_the_input(step,number,value):
    number = int(number)
    world.browser.find_elements_by_xpath("//input")[number-1].clear()
    world.browser.find_elements_by_xpath("//input")[number-1].send_keys(int(value))

@step('I wait some time')
def wait_some_time(step):
    time.sleep(30)

#关闭浏览器
@step('I close browser')
def close_browser(step):
    world.browser.quit()