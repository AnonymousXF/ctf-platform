Feature: login

Scenario: login null
Given I go to "http://127.0.0.1:5000/"
Given I click "登录"
Then I press "登录"
Then I should see "Not exist!"

Scenario: login correct 
Given I go to "http://127.0.0.1:5000/"
Given I click "登录"
When I fill in "邮箱" with "358693294@qq.com"
And I fill in "密码" with "3314518ASD"
And I press "登录"
Then I should see "nana" within 2 second
Then I click "注销"

