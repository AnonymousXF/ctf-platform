Feature: 模拟管理员对ticket的一些基本操作

Scenario: 添加基本数据
Given there is a admin in database with "admin","admin"
Given there is a user in database with "test","358693294@qq.com","12345678ASD"
Given I login with "test","12345678ASD"
Given I confirm my email
Given I register a team with "test","hust","True"
Given I logout
Given I login admin with "admin","admin"
Given I agree a team with "test"
Given I admin logout
Given I login with "test","12345678ASD"
Then I create a ticket with "test ticket summary","test ticket description"
Then I logout

Scenario: 查看ticket
Given I login admin with "admin","admin"
When I watch a ticket with id "1"
Then I should see "Ticket #1" 
Then I admin logout

Scenario: 评论ticket
Given I login admin with "admin","admin"
When I comment a ticket with id "1" with "test"
Then I should see "Comment added."
Then I admin logout

Scenario: 关闭一个ticket
Given I login admin with "admin","admin"
When I close a ticket with id "1"
Then I should see "Ticket closed."
Then I admin logout