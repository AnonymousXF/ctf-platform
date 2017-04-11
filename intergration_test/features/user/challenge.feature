Feature: 模拟用户答题

Scenario: 添加基本数据
Given there is a challenge in database with "Challenge Test","Test","Test","100","Test","Test"
Given there is a user in database with "test","358693294@qq.com","12345678ASD"
Given I login with "358693294@qq.com","12345678ASD"
Given I confirm my email
Given I register a team with "test","hust","True"
Given team agreed with "test"
Then I logout

Scenario: 回答处于关闭状态的题目
Given I login with "358693294@qq.com","12345678ASD"
When I plan to answer a closed challenge with "test"
Then I should see "You cannot submit a flag for a disabled problem."
Then I logout

Scenario: 回答处于开启状态的题目_wrong
Given I login with "358693294@qq.com","12345678ASD"
When I plan to answer a challenge with "wrong"
Then I should see "Incorrect flag."
Then I logout

Scenario: 回答处于开启状态的题目_correct
Given I login with "358693294@qq.com","12345678ASD"
When I plan to answer a challenge with "test"
Then I should see ""Flag accepted!"
Then I logout

Scenario: 删除数据库内容
Given I delete the database