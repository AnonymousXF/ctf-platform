Feature: answer_challenge

Scenario: 默认界面
Given I go to "http://127.0.0.1:5000"
Given I click "登录"
Given I fill in "用户名" with "test"
Given I fill in "密码" with "123456ASD"
Given I press "登录"
Given I click "题目"
Then I should see "你正在代表队伍"
Then I click "注销"

Scenario: 如果队伍不正确, 你应该立即 注销
Given I go to "http://127.0.0.1:5000"
Given I click "登录"
Given I fill in "用户名" with "test"
Given I fill in "密码" with "123456ASD"
Given I press "登录"
Given I click "题目"
When I click href with logout
Then I should see "登录"

Scenario: 收起_展开所有题目
Given I go to "http://127.0.0.1:5000"
Given I click "登录"
Given I fill in "用户名" with "test"
Given I fill in "密码" with "123456ASD"
Given I press "登录"
Given I click "题目"
When I click "收起题目"
Then I should see "展开所有题目"
When I click "展开所有题目"
Then I should see "收起所有题目"
Then I click "注销"

Scenario: 查看解决了的队伍
Given I go to "http://127.0.0.1:5000"
Given I click "登录"
Given I fill in "用户名" with "test"
Given I fill in "密码" with "123456ASD"
Given I press "登录"
Given I click "题目"
Given I click "查看解决了的队伍"
Then I should see "<< 返回题目页面"
Then I click "注销"

Scenario: 提交flag
Given I go to "http://127.0.0.1:5000"
Given I click "登录"
Given I fill in "用户名" with "test"
Given I fill in "密码" with "123456ASD"
Given I press "登录"
Given I click "题目"
When I fill in "Flag" with "123"
And I press "提交"
Then I should see "你正在代表队伍"
Then I click "注销"