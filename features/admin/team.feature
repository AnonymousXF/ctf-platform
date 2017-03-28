Feature: 管理员对队伍的基本操作

Scenario: 添加基本数据
Given there is a admin in database with "admin","admin"
Given there is a challenge in database with "Challenge Test","Test","Test","100","Test","Test"
Given there is a user in database with "test","358693294@qq.com","12345678ASD"
Given I login with "test","12345678ASD"
Given I confirm my email
Given I register a team with "test","hust","True"
Given I logout
Given there is a user in database with "test1","1111111@qq.com","12345678ASD"
Given I login with "test1","12345678ASD"
Given I confirm my email
Given I register a team with "test1","hust","True"
Given I logout

Scenario: 同时点击同意与拒绝队伍申请
Given I login admin with "admin","admin"
When I agree and reject a team with "test"
Then I should see "You can only choose one!"
Then I admin logout

Scenario: 同意队伍申请
Given I login admin with "admin","admin"
When I agree a team with "test"
Then I should see "agree"
Then I admin logout

Scenario: 拒绝队伍申请
Given I login admin with "admin","admin"
When I reject a team with "test1"
Then I should see "reject"
Then I admin logout

Scenario: 查看队伍
Given I login admin with "admin","admin"
When I watch a team with "test"
Then I should see "计算分数" 
Then I admin logout

Scenario: 修改队伍_toggle_eligibility
Given I login admin with "admin","admin"
When I set toggle_eligibility of a team with "test"
Then I should see "Eligibility set to"
Then I admin logout

Scenario: 修改队伍_toggle_eligibility_lock
Given I login admin with "admin","admin"
When I set toggle_eligibility_lock of a team with "test"
Then I should see "Eligibility lock set to"
Then I admin logout

Scenario: 修改队伍_adjust_score
Given I login admin with "admin","admin"
When I adjust_score of a team with "test" to "10","just for test"
Then I should see "Score adjusted."
Then I admin logout