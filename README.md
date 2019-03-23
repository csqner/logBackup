# log backup 简介
### 索引
1. <a href=‘#1‘>项目说明</a> 
2. <a href=‘#2‘>框架说明</a> 
3. <a href='#3'>目录结构</a> 
4. <a href='#4'>其他</a> 
 ---
 
 
 ### 项目说明 <a name='1'></a> 
 日志备份项目针对集群中MySQL, PostgreSQL, MongoDB日志进行备份, 从数据库实例日志所在的主机copy到专门用于放置日志备份的目录。对于数据
 库集群，只备份客户实际使用的那台主机上的数据库实例日志
 > 1. MySQL 从/pacloud/mybackup/\<instance>/archlog/ 到 /pacloud/dbbackup/mongodb/\<instance>/dblog/\<datetime>/ 
 > 2. PostgreSQL 从/pacloud/pgbackup/\<instance>/archlog/ 到 /pacloud/dbbackup/mongodb/\<instance>/dblog/\<datetime>/ 
 > 3. MongoDB 从/pacloud/mgbackup/\<instance>/archlog/ 到 /pacloud/dbbackup/mongodb/\<instance>/dblog/\<datetime>/ 
 
 ### 框架说明 <a name='2'></a>
 flask + celery + sqlalchemy  
 celery beat 每隔n秒从数据库中获取active状态的调度信息，然后从中二次过滤出实践需要备份的调度   
 信息发起调度，每个instance产生一个异步任务，更新next—_run_time字段。  
 每隔instance异步任务会调salt接口查询增量的文件，然后通过celery work flows调下一个异步任务  
 备份增量文件
 > 1. flask 开发web api， 对外提供接口
 > 2. celery 做异步任务，主要开发实际备份及删除过期日志逻辑
 > 3. sqlalchemy 使用线程池方式，防止大量数据库session频繁建立及释放
 
 
 ### 目录说明 <a name='3'></a>
 log_backup项目目录下有以下文件
 > 1. bin/ 目录： 存放一些命令及脚本
 > 2. docs/ 目录： 存放说明及接口文档
 > 3. logBackup/ 目录： 主程序目录 
 >   1. celerySchedule/ 目录： celery相关，task：备份及删除的主要逻辑
 >   2. utils/ 目录： 工具
 >   3. webApp/ 目录： web api
 >   4. 其他文件...  ：配置文件，model，异常类
 > 4. test/ 目录： 单元测试代码
 > 5. README.md 本文件
 > 6. requirement.txxt :本项目依赖的库
 
 ### 其他 <a name='4'></a>
 暂无
    