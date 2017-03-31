Feature: open_ticket

Scenario: 创建ticket
Given I go to "http://127.0.0.1:5000"
Given I click "登录"
Given I fill in "用户名" with "test"
Given I fill in "密码" with "123456ASD"
Given I press "登录"
Given I click "Tickets"
Given I click "创建一个新的ticket"
When I fill in "问题摘要" with "test"
And I fill in "问题描述" with "test"
And I press "新建ticket"
Then I should see "open"
Then I click "注销"
