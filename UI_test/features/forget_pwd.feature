Feature: forget_pwd

Scenario: 默认界面
Given I go to "http://127.0.0.1:5000/"
Given I click "登录"
When I click ".....忘记密码？"
Then I should see "获取验证码"
Then I press "获取验证码"

Scenario: 获取验证码
Given I go to "http://127.0.0.1:5000/"
Given I click "登录"
When I click ".....忘记密码？"
And I fill in "邮箱" with "358693294@qq.com"
Then I press "获取验证码"
Then I should see "Not exist!" 

Scenario: 确定
Given I go to "http://127.0.0.1:5000/"
Given I click "登录"
When I click ".....忘记密码？"
And I fill the 3 input with "358693294@qq.com"
And I fill in "验证码" with "123"
Then I press "确定"
Then I should see "Not exist!" 
