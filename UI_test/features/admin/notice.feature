Feature: botice

Scenario: 默认页面
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
When I click "通知"
Then I should see "发布通知" within 2 second
Then I click "注销 (admin)"

Scenario: 发布通知
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
Given I click "通知"
Then I fill in "标题" with "test notice"
And I fill in "内容" with "test test test"
And I press "发布新通知"
Then I should see "Publish Success!"
Then I click "注销 (admin)"