Feature: 模拟用户的注册登录等操作

Scenario: 默认界面
Given I visit system
Then I should see "队伍积分"

Scenario: 注册成功
Given I fill the register information with "test","358693294@qq.com","12345678ASD","12345678ASD"
Then I should see "register successfully."
Then I logout

Scenario: 确认邮箱
Given I login with "358693294@qq.com","12345678ASD"
Then I confirm my email
Then I should see "confirmed!"
Then I logout

Scenario: 更新用户信息_nothing_changed
Given I login with "358693294@qq.com","12345678ASD"
Given I update my information with "test"
Then I should see "nothing changed"

Scenario: 更新用户信息_save_change
Given I login with "358693294@qq.com","12345678ASD"
Given I update my information with "tes"
Then I should see "save change."

Scenario: 删除数据库内容
Given I delete the database