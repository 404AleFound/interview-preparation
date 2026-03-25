# ReadView 技术

## ReadView 的实现
### 四个字段
Read View 有四个重要的字段：`m_ids`，`min_trx_id`，`max_trx_id`，`creator_trx_id`：
- **`m_ids`**：指的是在创建 Read View 时，当前数据库中活跃事务的事务 id 列表，注意这是一个列表。“活跃事务”指的是，启动了但是还没提交的事务。
- **`min_trx_id`**：指在创建 Read View 的时候，当前数据库的活跃事务中事务 id 最小的事务，也就是 m_ids 的最小值。
- **`max_trx_id`**：指在创建 Read View 的时候，当前数据库应该给下一个事务的 id 的值，也就是全局事务中最大的事务 id 值 +1。
- **`creator_trx_id`**：指的是创建该 Read View 的事务的事务 id。

### 聚簇索引的隐藏列
对于使用 InnoDB 存储引擎的数据库表，它的聚簇索引记录中都包含下面两个隐藏列，`trx_id` 和 `roll_pointer`：
- `trx_id`：当一个事务对某条聚簇索引记录进行改动时，就会把该事务的 id 记录在 trx_id 隐藏列里。
- `roll_pointer`：每次对某条聚簇索引记录进行改动时，都会把旧版本的记录写入到 undo 日志中，然后这个隐藏列是一个指针，指向每一个旧版本记录，于是就可以通过它找到修改前的记录。

### 事务访问记录
一个事务去访问记录的时候，除了**自己的更新记录总是可见之外**，还有如下几种情况：
- **如果当前记录的 trx_idx 值小于 Read View 中的 min_trx_id 值**，表示这个版本的记录是在创建 Read View 前已经提交的事务生成的，所以该版本的记录对当前事务可见。
- **如果记录的 trx_idx 值大于等于 Read View 中的 max_trx_id 值**，表示这个版本的记录是在创建 Read View 后才启动的事务生成的，所以该版本的记录对当前事务不可见。
- **如果记录的 trx_idx 值在 Read View 的 min_trx_idx 和 max_trx_idx 之间**，需要判断 trx_id 是否在 m_ids 列表中：
    - **如果记录的 trx_id 在 m_ids 列表中**，表示生成该版本记录的活跃事务依然活跃着，所以该版本的记录对当前事务不可见。

    - **如果记录的 trx_id 不在 m_ids 列表中**，表示生成该版本记录的活跃事务已经被提交，所以该版本的记录对当前事务可见。

**案例**

假设当前数据库有如下事务状态：
```
Committed transactions:
    |__ T1 (trx_id=101)
    |__ T2 (trx_id=102)
    |__ T4 (trx_id=104)
Active uncommitted transactions:
    |__ T3 (trx_id=103)
    |__ T5 (trx_id=105)
新开启的事务:
    |__ T6 (trx_id=106)
```
此时，T6 创建 ReadView，快照如下：
```
T6 ReadView
|__ m_ids = [103, 105]      // 当前活跃未提交事务
|__ min_trx_id = 103        // m_ids 最小值
|__ max_trx_id = 107        // 下一个将分配的事务 id
|__ creator_trx_id = 106
```

T6 访问不同 trx_id 生成的记录时的可见性分析：

| 记录版本 trx_id | 判断过程 | 结果 |
|---|---|---|
| `101` | `101 < min_trx_id`                                            | 可见 |
| `102` | `102 < min_trx_id`                                            | 可见 |
| `103` | `103 >= min_trx_id` 且 `103 < max_trx_id`，且在 `m_ids`        | 不可见|
| `104` | `104 >= min_trx_id` 且 `104 < max_trx_id`，且不在 `m_ids`      | 可见 |
| `105` | `105 >= min_trx_id` 且 `105 < max_trx_id`，且在 `m_ids`        | 不可见|
| `106` | `106 >= max_trx_id`                                           |不可见|

**重点说明：**
- 104 虽然在区间 `[103, 107)`，但不在 m_ids，说明 T4 在 T6 创建 ReadView 时已经提交，所以对 T6 可见。
- 103、105 在 m_ids，说明这两个事务在 T6 创建 ReadView 时还未提交，对 T6 不可见。
- 101、102 更早已提交，直接可见。
- 106 及以后是 ReadView 创建后新事务，不可见。

这个例子体现了非连续 id、部分已提交、部分未提交的更普遍场景。

## 可重复读的原理
**可重复读隔离级别是事务启动时生成一个 Read View，然后整个事务期间都在用这个 Read View。**


## 读提交的原理
**读提交隔离级别是在每次读取数据时，都会生成一个新的 Read View。**