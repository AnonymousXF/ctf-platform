Feature: tickets

Scenario: 默认页面
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
When I click "Tickets"
Then I should see "Trouble tickets"
Then I click "注销 (admin)"