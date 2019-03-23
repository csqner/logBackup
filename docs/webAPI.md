# web api
### 版本
###### 接口
> /backup/log/api/v1/test

###### 接口功能
> 测试接口时候可用

###### 请求方式
> get方式
###### 请求参数
|参数|必选|类型|说明|
|:---|:---|:---|:---|
###### 返回参数
|参数|类型|说明| 
|:---|:---|:---|
|msg|dict|结果，status字段表示状态| 
|code|int|状态码|   
### 版本
###### 接口
>/backup/log/api/v1/version
###### 接口功能
> 查看api版本
###### 请求方式
>get 方式
###### 请求参数
|参数|必选|类型|说明|
|:---|:---|:---|:---|
###### 返回参数
|参数|类型|说明|
|:---|:---|:---|
|msg|dict|结果，version字段表示版本|
|code|int|状态码|


### 查看schedule
###### 接口
>/backup/log/api/v1/schedule/<entity_name>
###### 请求方式
> get 方式
###### 请求参数
|参数|必选|类型|说明|
|:---|:---|:---|:---|
###### 返回参数
|参数|类型|说明|
|:---|:---|:---|
|msg|list|结果，元素为dict<br>id_st_bk_dblog_schedule: schedule的id<br>id_st_backup_policy: policy的id<br>entity_name: 库名<br>logbk_interval_min: 备份间隔<br>schedule_status: schedule状态，active表示启用，expired表示停用<br>last_bkfile_mtime: 表示最后一个备份日志的修改时间<br>next_run_time: 此策略下次启动时间|
|code|int|状态码，200为成功，其他为异常|
### 新增schedule
###### 接口
>/backup/log/api/v1/schedule
###### 请求方式
> post 方式
###### 请求参数
|参数|必选|类型|说明|
|:---|:---|:---|:---|
|id_db_backup_policy|Y|int|policy id|
|logbk_interval_min|Y|int|间隔，分钟|
|schedule_status|Y|str|状态，‘active’为启用，‘expired'为禁用
|created_by|N|str|创建人|


###### 返回参数
|参数|类型|说明|
|:---|:---|:---|
|msg|dict|id_st_bk_dblog_schedule为schedule id|
|code|int|返回码

### 更新schedule
###### 接口
> /backup/log/api/v1/schedule
###### 请求方式
> put方式
###### 请求参数
|参数|必选|类型|说明|
|:---|:---|:---|:---|
|id_db_backup_policy|N|int|policy id|
|logbk_interval_min|N|int|间隔，分钟，**当id_db_backup_policy参数有数据时，此项必须不为空**|
|id_st_bk_dblog_schedule|N|int|schedule id|
|schedule_status|N|str|**当id_st_bk_dblog_schedule参数有数据时，此项必须不为空**|
|update_by|N|str|更新人|

###### 返回参数
|参数|类型|说明|
|:---|:---|:---|
|msg|str|结果|
|code|int|状态码，200为成功，其他为异常|