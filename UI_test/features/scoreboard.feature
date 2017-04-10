Feature: scoreboard

Scenario: 默认界面
Given I go to "http://127.0.0.1:5000"
Given I click "登录"
Given I fill in "用户名" with "test"
Given I fill in "密码" with "123456ASD"
Given I press "登录"
Then I click "排名"
Then I should see "队伍积分"
Then I click "注销"