Feature: 模拟管理员的注册登录等操作

Scenario: 默认界面
Given I visit admin system
Then I should see "登录"

Scenario: 添加基本数据
Given there is a admin in database with "admin","admin"

Scenario: 登录
Given I login admin with "admin","admin"
Then I should see "待审核队伍"
Then I admin logout