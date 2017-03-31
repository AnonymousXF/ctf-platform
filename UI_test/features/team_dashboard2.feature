Feature: team_manage

Scenario: 修改队伍
Given I go to "http://127.0.0.1:5000"
Given I click "登录"
Given I fill in "用户名" with "test"
Given I fill in "密码" with "123456ASD"
Given I press "登录"
When I click "编辑队伍信息"
Then I fill in "队伍名" with "123"
And I fill in "Affiliation" with "hust"
And I press "修改队伍"
Then I should see "nothing changed"
Then I click "注销"
Then I close browser
