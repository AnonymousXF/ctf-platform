Feature: challenge_solves

Scenario: 默认界面
Given I go to "http://127.0.0.1:5000"
Given I click "登录"
Given I fill in "用户名" with "test"
Given I fill in "密码" with "123456ASD"
Given I press "登录"
Given I click "题目"
When I click "查看解决了的队伍"
Then I should see "答出了"
Then I click "注销"

Scenario: 返回题目界面
Given I go to "http://127.0.0.1:5000"
Given I click "登录"
Given I fill in "用户名" with "test"
Given I fill in "密码" with "123456ASD"
Given I press "登录"
Given I click "题目"
Given I click "查看解决了的队伍"
When I click "<< 返回题目页面"
Then I should see "你正在代表队伍"
Then I click "注销"