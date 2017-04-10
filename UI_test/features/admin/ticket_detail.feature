Feature: ticket_detail

Scenario: 关闭ticket
Given I go to "http://127.0.0.1:5000/admin"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
Given I click "Tickets"
Given I click "#1 test (123)"
When I check the checkbox which id is "resolved"
And I fill in "评论" with "test comment" 
And I wait some time
And I press "更新ticket"
Then I should see "Ticket closed"
Then I click "注销 (admin)"

Scenario: 开启ticket
Given I go to "http://127.0.0.1:5000/admin"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
Given I click "Tickets"
Given I click "#1 test (123)"
When I check the checkbox which id is "resolved"
And I fill in "评论" with "test comment" 
And I wait some time
And I press "更新ticket"
Then I should see "Ticket reopened"
Then I click "注销 (admin)"
Then I close browser