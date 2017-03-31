Feature: challenge

Scenario: 默认页面
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
When I click "题目"
Then I should see "管理题目" within 2 second
Then I click "注销 (admin)"

Scenario: 管理题目_setFalse
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
Given I click "题目"
When I click "True"
Then I should see "Enabled set to False" within 2 second
Then I click "注销 (admin)"

Scenario: 管理题目_setTrue
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
Given I click "题目"
When I click "False"
Then I should see "Enabled set to True" within 2 second
Then I click "注销 (admin)"

Scenario: 管理虚拟机
Given I go to "http://127.0.0.1:5000/admin/"
Given I fill in "用户名" with "admin"
Given I fill in "密码" with "admin"
Given I press "登录"
Given I click "题目"
When I fill in "url" with "qemu+ssh://nana@127.0.0.1/system"
And I fill in "xml" with "/home/nana/ctf-platform/vmachine/"
And I press "连接服务器"
Then I should see "虚拟机名"
Then I click "注销 (admin)"