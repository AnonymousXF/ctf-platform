Feature: register

Scenario: 默认界面
Given I go to "http://127.0.0.1:5000/"
Given I click "注册"
Then I should see "注册新用户"

Scenario: 注册
Given I go to "http://127.0.0.1:5000/"
Given I click "注册"
When I fill in "用户名" with "test"
When I fill in "邮箱" with "358693294@qq.com"
When I fill in "密码" with "123456ASD"
When I fill in "确认密码" with "123456ASD"
When I press "注册"
Then I should see "The name has been used" 

