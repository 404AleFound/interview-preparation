# redo log

## 什么是 redo log
redo log 是物理日志，记录了某一个数据页做了什么修改，每当执行一个事务就会产生这样的一条或者多条物理日志。

## 为什么需要 redo log
### 实现事务的持久化能力
Buffer Pool 是提高了读写效率没错，但是问题来了，Buffer Pool 是基于内存的，而内存总是不可靠，万一断电重启，还没来得及落盘的脏页数据就会丢失。

为了防止断电导致数据丢失的问题，当有一条记录需要更新的时候，InnoDB 引擎就会**先更新内存**（同时标记为脏页），然后**将本次对这个页的修改以 redo log 的形式记录下**来，这个时候更新就算完成了。

之后，InnoDB 引擎会在适当的时候，由后台线程将缓存在 Buffer Pool 的脏页刷新到磁盘里，这就是 WAL（Write-Ahead Logging） 技术

WAL 技术指的是：MySQL 的写操作并不是立刻写到磁盘上，而是先写日志，然后在合适的时间再写到磁盘上。



在事务提交时，只要将 redo log 持久化到磁盘即可，可以不需要等到将缓存在 Buffer Pool 里的脏页数据持久化到磁盘

当系统崩溃时，虽然脏页数据没有持久化，但是 redo log 已经持久化，接着 mysql 重启后，可以根据 redo log 的内容，将所有数据恢复到最新的状态。

## redo log 的写磁盘
可以看到上面内容主要将频繁对数据写磁盘的操作改变为持续对 redo log 写磁盘的操作。

由于写入 redo log 的方式使用了**追加操作**，所以磁盘操作是**顺序写**，而写入数据需要先找到写入位置，然后才写到磁盘，所以磁盘操作是**随机写**。

磁盘顺序写要比随机写高效的多，因此 redo log 写入磁盘的开销更小。


## redo log 是直接写入磁盘的吗？
redo log 不是直接写入磁盘的。执行一个事务的时候，产生的 redo log 不是直接写入磁盘的，因为这样会产生大量的 I/O 操作，而且磁盘的运行速度远慢于内存。

因此 redo log 也有自己的缓存：redo log buffer，每当产生一条 redo log 时，会先写入到 redo log buffer，后续在持久化到磁盘。

## redo log 刷盘的时机
缓存在 redo log buffer 里的 redo log 还是在内存中，其刷盘的时机如何？
- mysql 正常关闭时
- 当 redo log buffer 中记录的写入量大于 redo log buffer 内存空间的一半时，会触发落盘。
- InnoDB 的后台线程，每隔 1 秒，将 redo log buffer 持久化到硬盘。
- 每次事务提交时都将缓存在 redo log buffer 里的 redo log 直接持久化到磁盘

### `innodb_flush_log_at_trx_commit` 参数
单独执行

除此之外，InnoDB 还提供了另外两种策略，由`innodb_flush_log_at_trx_commit` 参数控制：
- 设置参数为 0 时：每次事务

## redo log 写满时

