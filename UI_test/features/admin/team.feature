Feature: Team

Scenario: 查看team
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
When I click "123"
Then I should see "队伍名称"
Then I click "注销 (admin)"

Scenario: 管理team_Eligibility_set_to_False
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
Given I click "123"
When I click href with "13"
Then I should see "Eligibility set to False"
Then I click "注销 (admin)"

Scenario: 管理team_Eligibility_set_to_True
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
Given I click "123"
When I click href with "13"
Then I should see "Eligibility set to True"
Then I click "注销 (admin)"

Scenario: 管理team_Eligibility_lock_set_to_False
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
Given I click "123"
When I click href with "14"
Then I should see "Eligibility lock set to False"
Then I click "注销 (admin)"

Scenario: 管理team_Eligibility_lock_set_to_True
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
Given I click "123"
When I click href with "14"
Then I should see "Eligibility lock set to True"
Then I click "注销 (admin)"

Scenario: 分数调整
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
Given I click "123"
When I fill in "分值" with "100"
And I fill in "原因" with "test score adjust"
And I press "调整"
Then I should see "Score adjusted"
Then I click "注销 (admin)"