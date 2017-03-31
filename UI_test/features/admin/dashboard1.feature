Feature: Dashboard1

Scenario: 默认界面
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
When I click "主页面"
Then I should see "队伍信息"
Then I click "注销 (admin)"

Scenario: team agree 
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
Then I check the checkbox which id is "a1"
Then I press "确定"
Then I should see "agree"
Then I click "注销 (admin)"