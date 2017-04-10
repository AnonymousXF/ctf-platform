Feature: Dashboard2

Scenario: 默认界面
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
When I click "主页面"
Then I should see "队伍信息"
Then I click "注销 (admin)"

Scenario: 管理team
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
When I click "123"
Then I should see "队伍名称"
Then I click "注销 (admin)"