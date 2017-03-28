Feature: 模拟用户加入队伍或创建队伍等操作

Scenario: 添加基本数据
Given there is a user in database with "test","358693294@qq.com","12345678ASD"
Given there is a user in database with "test1","11111111@qq.com","12345678ASD"
Given there is a user in database with "test2","22222222@qq.com","12345678ASD"
Given there is a admin in database with "admin","admin"

Scenario: 注册队伍_notconfirm
Given I login with "test","12345678ASD"
When I register a team with "test","hust","True"
Then I should see "Please confirm your email."
Then I logout

Scenario: 注册队伍_success
Given I login with "test","12345678ASD"
Given I confirm my email
When I register a team with "test","hust","True"
Then I should see "The request has send to admin."
Then I logout

Scenario: 注册队伍_重名
Given I login with "test1","12345678ASD"
Given I confirm my email
When I register a team with "test","hust","True"
Then I should see "The team name has been used."
Then I logout

Scenario: 注册队伍_队伍名为空
Given I login with "test1","12345678ASD"
When I register a team with "","hust","True"
Then I should see "wrong team name format!"
Then I logout

Scenario: 注册队伍_test1
Given I login with "test1","12345678ASD"
Given I confirm my email
When I register a team with "test1","hust","True"
Then I should see "The request has send to admin."
Then I logout

Scenario: test队伍通过管理员审核
Given team agreed with "test"

Scenario: 加入队伍_notconfirm
Given I login with "test2","12345678ASD"
When I add a team with "test2"
Then I should see "Please confirm your email."
Then I logout

Scenario: 加入队伍_notexist
Given I login with "test2","12345678ASD"
Given I confirm my email
When I add a team with "test2"
Then I should see "team name do not exist!"
Then I logout

Scenario: 加入队伍_notagreed
Given I login with "test2","12345678ASD"
When I add a team with "test1"
Then I should see "The team has not be agreed by admin.Please wait,or join another team!"
Then I logout

Scenario: 加入队伍_success
Given I login with "test2","12345678ASD"
When I add a team with "test"
Then I should see "The request has sent to leader!"
Then I logout

Scenario: 队长同意加入队伍
Given I login with "test","12345678ASD"
When I agree "test2" join the team
Then I should see "agree"

Scenario: test1队伍通过管理员审核
Given team agreed with "test1"

Scenario: 修改队伍_nothingchanged
Given I login with "test","12345678ASD"
Given I confirm my email
When I modify my team with "test","hust","True"
Then I should see "nothing changed!"
Then I logout

Scenario: 修改队伍_wrong_name
Given I login with "test","12345678ASD"
Given I confirm my email
When I modify my team with "","hust","True"
Then I should see "wrong team name format!"
Then I logout

Scenario: 修改队伍_重名
Given I login with "test","12345678ASD"
Given I confirm my email
When I modify my team with "test1","hust","True"
Then I should see "The team name has been used."
Then I logout

Scenario: 修改队伍_success
Given I login with "test","12345678ASD"
Given I confirm my email
When I modify my team with "tes","hust","True"
Then I should see "change successfully."
Then I logout

Scenario: 删除数据库内容
Given I delete the database