Feature: 模拟管理员开启关闭题目

Scenario: 添加基本数据
Given there is a admin in database with "admin","admin"
Given there is a challenge in database with "Challenge Test","Test","Test","100","Test","Test"

Scenario: 题目set_enable
Given I login admin with "admin","admin"
When I close a challenge with id "1"
Then I should see "Enabled set to"
Then I admin logout