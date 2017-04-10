Feature: 模拟管理员对虚拟机的一些基本操作

Scenario: 添加基本数据
Given there is a admin in database with "admin","admin"

Scenario: 默认界面
Given I login admin with "admin","admin"
When I watch the vmachine
Then I should see "连接服务器" 
Then I admin logout

Scenario: 连接远程虚拟机服务器
Given I login admin with "admin","admin"
When I connect with "qemu+ssh://127.0.0.1/system","/home/nana/ctf-platform/vmachine/"
Then I should see "虚拟机名" 
Then I admin logout

Scenario: 修改虚拟机基本信息_shutdown
Given I login admin with "admin","admin"
When I connect with "qemu+ssh://127.0.0.1/system","/home/nana/ctf-platform/vmachine/"
And I modify a vmachine with id "FreeDOS" with "1024","1","shutdown"
Then I should see "shutdown"
Then I admin logout

Scenario: 修改虚拟机基本信息_running
Given I login admin with "admin","admin"
When I connect with "qemu+ssh://127.0.0.1/system","/home/nana/ctf-platform/vmachine/"
And I modify a vmachine with id "FreeDOS" with "1024","1","running"
Then I should see "running"
Then I admin logout

Scenario: 修改虚拟机基本信息_suspend
Given I login admin with "admin","admin"
When I connect with "qemu+ssh://127.0.0.1/system","/home/nana/ctf-platform/vmachine/"
And I modify a vmachine with id "FreeDOS" with "1024","1","suspend"
Then I should see "suspend"
Then I admin logout

Scenario: 修改虚拟机基本信息_resume
Given I login admin with "admin","admin"
When I connect with "qemu+ssh://127.0.0.1/system","/home/nana/ctf-platform/vmachine/"
And I modify a vmachine with id "FreeDOS" with "1024","1","resume"
Then I should see "running"
Then I admin logout

Scenario: 修改虚拟机基本信息_memory_1023
Given I login admin with "admin","admin"
When I connect with "qemu+ssh://127.0.0.1/system","/home/nana/ctf-platform/vmachine/"
And I modify a vmachine with id "FreeDOS" with "1023","1","shutdown"
Then I should see "1023"
Then I admin logout

Scenario: 修改虚拟机基本信息_cpu_2
Given I login admin with "admin","admin"
When I connect with "qemu+ssh://127.0.0.1/system","/home/nana/ctf-platform/vmachine/"
And I modify a vmachine with id "FreeDOS" with "1024","2","shutdown"
Then I should see "2"
Then I admin logout
