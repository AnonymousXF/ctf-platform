Feature: user_manage

Scenario: 修改用户信息
Given I go to "http://127.0.0.1:5000"
Given I click "登录"
Given I fill in "用户名" with "test"
Given I fill in "密码" with "123456ASD"
Given I press "登录"
Given I click id with "dropdown1"
Given I click "用户"
Then I fill in "用户名" with "test"
And I fill in "邮箱" with "358693294@qq.com"
And I press "修改信息"
Then I should see "nothing changed"
Then I click "注销"
Then I close browser