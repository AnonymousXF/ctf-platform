Feature: Go to visit
    
Scenario: 默认路由
Given I go to "http://127.0.0.1:5000/"  
Then I should see "队伍积分" within 2 second

Scenario: 点击登录
Given I go to "http://127.0.0.1:5000/"
When I click "登录"
Then I should see "忘记密码" within 2 second

Scenario: 点击注册
Given I go to "http://127.0.0.1:5000/"
When I click "注册"
Then I should see "注册新用户" within 2 second

Scenario: 点击排名
Given I go to "http://127.0.0.1:5000/"
When I click "排名"
Then I should see "队伍积分" within 2 second


