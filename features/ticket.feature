Feature: 模拟用户ticket操作

Scenario: 添加基本数据
Given there is a user in database with "test","358693294@qq.com","12345678ASD"
Given I login with "test","12345678ASD"
Given I confirm my email
Given I register a team with "test","hust","True"
Given team agreed with "test"
Then I logout

Scenario: 默认ticket
Given I login with "test","12345678ASD"
When I plan to create a ticket
Then I should see "新建一个 Trouble Ticket"
Then I logout

Scenario: 创建一个ticket
Given I login with "test","12345678ASD"
When I create a ticket with "test ticket summary","test ticket description"
Then I should see "Ticket #1 opened."
Then I logout

Scenario: 查看一个ticket
Given I login with "test","12345678ASD"
When I open a ticket with id "1"
Then I should see "Ticket #1"
Then I logout

Scenario: 评论一个ticket
Given I login with "test","12345678ASD"
When I comment a ticket with id "1" with "test"
Then I should see "Comment added."
Then I logout

Scenario: 关闭一个ticket
Given I login with "test","12345678ASD"
When I close a ticket with id "1"
Then I should see "Ticket closed."
Then I logout