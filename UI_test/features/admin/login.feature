Feature: login

Scenario: login null
Given I go to "http://127.0.0.1:5000/admin/"
Then I press "登录"
Then I should see "You have make a terrible mistake!"

Scenario: login correct 
Given I go to "http://127.0.0.1:5000/admin/"
When I fill in "用户名" with "admin"
And I fill in "密码" with "admin"
And I press "登录"
Then I should see "注销" within 2 second
Then I click "注销 (admin)"

