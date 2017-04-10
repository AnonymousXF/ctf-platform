Feature: team_add

Scenario: 加入队伍
Given I go to "http://127.0.0.1:5000"
Given I click "登录"
Given I fill in "用户名" with "test"
Given I fill in "密码" with "123456ASD"
Given I press "登录"
When I click "加入队伍"
Then I fill in "队伍名" with "123"
And I press "申请加入"
Then I should see "team name do not exist!"
Then I click "注销"

Scenario: 创建队伍,队伍名为123,队伍属于hust
Given I go to "http://127.0.0.1:5000"
Given I click "登录"
Given I fill in "用户名" with "test"
Given I fill in "密码" with "123456ASD"
Given I press "登录"
When I click "注册队伍"
Then I fill the 3 input with "123"
And I fill in "Affiliation" with "hust"
Then I check the checkbox which id is "team-eligibility"
Then I press "创建队伍"
Then I should see "The request has send to admin."
Then I close browser
