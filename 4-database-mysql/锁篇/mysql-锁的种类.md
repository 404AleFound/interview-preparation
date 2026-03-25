# 锁的种类
**目录**

- [全局锁](#全局锁)
- [表级锁](#表级锁)
    - [表锁](#表锁)
    - [元数据锁](#元数据锁)
    - [意向锁](#意向锁)
    - [AUTO-INC 锁](#auto-inc-锁)
- [行级锁](#行级锁)
    - [Record Lock](#record-lock)
    - [Gap Lock](#gap-lock)
    - [Next-key Lock](#next-key-lock)
    - [插入意向锁](#插入意向锁)


## 全局锁
### 全局锁的使用
```sql
flush tables with read lock
```
上述语句执行后，整个**数据库**就处于只读状态了，此时其他线程执行下述操作都会被阻塞：
- 对数据的增删改操作，比如 `insert`、`delete`、`update` 等语句。
- 对表结构的更改操作，比如 `alter table`、`drop table` 等语句。
如果要释放全局锁，使用下述语句：
```sql
unlock tables
```
## 表级锁
### 表锁
### 元数据锁
### 意向锁
### AUTO-INC 锁

## 行级锁
### Record Lock
### Gap Lock
### Next-key Lock
### 插入意向锁