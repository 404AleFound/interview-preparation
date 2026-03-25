# expalin查询
## 目录

- [使用语法](#使用语法)
- [常见字段](#常见字段)
    - [`id` 字段](#id-字段)
    - [`select_type` 字段](#select_type-字段)
    - [`table` 字段](#table-字段)
    - [`type` 字段](#type-字段)
    - [`possible_key` 字段](#possible_key-字段)
    - [`key` 字段](#key-字段)
    - [`key_len` 字段](#key_len-字段)
    - [`ref` 字段](#ref-字段)
    - [`rows` 字段](#rows-字段)
    - [`filtered` 字段](#filtered-字段)
    - [`Extra` 字段](#extra-字段)
- [解析案例](#解析案例)


## 使用语法

```sql
EXPLAIN [EXTENDED] SELECT ...;
```
- `EXPLAIN` 用于分析 SQL 查询的执行计划，显示优化器如何执行语句。
- 可用于 `SELECT`、`DELETE`、`INSERT`、`REPLACE` 和 `UPDATE` 语句。
- 常用写法：
    - `EXPLAIN SELECT * FROM user WHERE id = 1;`
    - `EXPLAIN EXTENDED SELECT * FROM user WHERE age > 20;`
- MySQL 8.0 还支持 `EXPLAIN ANALYZE`，可显示实际执行过程和耗时。

**示例：**
```sql
EXPLAIN SELECT * FROM employees WHERE department_id = 2;
```

执行后会返回一张表，包含各字段的含义和执行细节。通过分析这些信息，可以优化 SQL 查询性能。
## 常见字段
### `id` 字段
`id` 字段用于标识 `EXPLAIN` 输出中每一行的查询序列号，表示查询中各个子查询或联合查询的执行顺序。`id` 值越大，优先级越高，越先被执行。

- 如果所有行的 `id` 相同，表示这些操作属于同一个查询块，通常是简单查询或没有子查询的情况。
- 如果存在不同的 `id`，则通常涉及子查询或联合查询，`id` 值大的子查询会优先执行，结果被 `id` 小的查询引用。

通过分析 `id` 字段，可以了解 SQL 执行的层次结构和各部分的执行顺序，有助于优化复杂查询。

### `select_type` 字段
`select_type` 字段用于描述每一行所代表的查询类型，反映了 SQL 语句中各个部分的作用。常见取值有：

- `SIMPLE`：简单查询，不包含子查询或 UNION。
- `PRIMARY`：最外层的 SELECT 查询。
- `SUBQUERY`：在 SELECT 或 WHERE 子句中包含的子查询。
- `DERIVED`：在 FROM 子句中出现的子查询（派生表）。
- `UNION`：UNION 语句中的第二个及后续 SELECT 查询。
- `UNION RESULT`：用于显示 UNION 合并结果的 SELECT。
- `DEPENDENT SUBQUERY`：依赖于外部查询的子查询。
- `DEPENDENT UNION`：依赖于外部查询的 UNION。

通过分析 `select_type` 字段，可以了解 SQL 查询的结构和复杂度，有助于定位性能瓶颈和优化查询逻辑。

### `table` 字段
`table` 字段显示当前执行计划行所涉及的表名或别名。对于简单查询，通常直接显示表名；对于子查询、派生表或临时表，可能显示为 `<derivedN>`、`<subqueryN>` 或 `<unionN>` 等特殊标识。

- 如果是普通表，显示表名或别名。
- 如果是子查询或派生表，显示 `<derivedN>`，其中 N 表示派生表的编号。
- 如果是 UNION 查询的结果，显示 `<unionN>` 或 `<unionM,N>`。

通过分析 `table` 字段，可以了解每一步操作针对的数据来源，有助于理解复杂查询的执行流程。

### `type` 字段
`type` 字段表示 MySQL 在执行查询时访问表的方式（即连接类型），反映了查询的效率。常见的取值有：

- `ALL`：全表扫描，性能最差。
- `index`：遍历索引，通常比全表扫描快。
- `range`：索引范围扫描，常见于范围查询（如 `BETWEEN`、`>`, `<`）。
- `ref`：使用非唯一索引或唯一前缀扫描，返回匹配某个值的所有行。
- `eq_ref`：唯一索引扫描，每次只返回一条记录，效率较高。
- `const` / `system`：表中最多只有一行匹配，效率最高。

一般来说，`const`、`eq_ref`、`ref`、`range` 的效率依次降低，`ALL` 最低。优化查询时应尽量避免出现 `ALL`。

### `possible_key` 字段
`possible_key` 字段显示 MySQL 查询优化器在执行查询时，可能会用到的索引列表。该字段的值基于查询条件和表结构推断，表示哪些索引可以用于优化本次查询，但实际使用的索引由 `key` 字段决定。

- 如果该字段为 `NULL`，说明没有可用的索引，可能需要考虑为相关字段添加索引。
- 如果有多个索引，说明优化器可以选择其中之一。

通过分析 `possible_key` 字段，可以判断索引设计是否合理，以及查询是否能够利用已有索引。

### `key` 字段
`key` 字段显示 MySQL 实际用于本次查询的索引名称。如果该字段为 `NULL`，表示查询未使用任何索引，通常意味着查询效率较低。实际使用的索引是从 `possible_key` 字段中选择的，具体选择由优化器根据成本估算决定。

- 如果 `key` 字段有值，说明查询已利用索引进行优化。
- 如果为 `NULL`，建议检查查询条件和表结构，考虑是否需要增加合适的索引。

通过分析 `key` 字段，可以判断查询是否真正利用了索引，从而进一步优化 SQL 性能。

### `key_len` 字段
`key_len` 字段表示 MySQL 查询执行过程中实际使用的索引长度（以字节为单位）。该值由表结构和查询条件共同决定，反映了索引中被用到的列的总长度。

- `key_len` 越短，说明用到的索引列越少，通常效率更高。
- 该字段的值可以帮助判断索引是否被完全利用（如联合索引是否用到了所有列）。

通过分析 `key_len`，可以优化索引设计，使查询尽可能利用索引的全部能力。

### `ref` 字段
`ref` 字段显示了与索引列进行比较的对象，通常是常量、表达式或其他表的列。它反映了索引查找时所用到的参考值来源。

- 如果为常量，表示用常量与索引列进行匹配。
- 如果为某个表的列，表示通过关联条件与该列进行匹配。
- 如果为 `NULL`，说明索引未被使用或无法通过索引查找。

通过分析 `ref` 字段，可以了解索引查找的具体方式，有助于判断关联条件和索引的匹配情况。

### `rows` 字段
`rows` 字段表示 MySQL 估算本次查询需要读取的行数。该值是基于表统计信息和查询条件计算得出的，反映了优化器预计需要扫描的数据量。

- `rows` 值越小，说明查询扫描的数据越少，效率越高。
- 该字段配合 `filtered` 字段，可以估算最终参与结果集的数据量。

通过分析 `rows` 字段，可以判断 SQL 查询的扫描范围，辅助定位性能瓶颈，优化表结构或查询条件。

### `filtered` 字段
`filtered` 字段表示 MySQL 估算的表中符合条件的行数所占的百分比。其值越高，说明过滤条件越有效，扫描的数据越少。通常配合 `rows` 字段一起理解，可以估算最终需要处理的数据量。

- 当 `filtered` 值为 100 时，表示所有行都满足条件。
- 当 `filtered` 值较低时，说明大部分数据被过滤掉了。

该字段有助于分析 SQL 查询的过滤效率，从而优化查询条件和索引设计。

### `Extra` 字段
`Extra` 字段显示了关于当前查询执行计划的额外信息，通常用于补充说明优化器在执行过程中采取的特殊操作。常见的取值有：

- `Using index`：仅通过索引即可获取所需数据，无需回表，效率较高。
- `Using where`：使用了 `WHERE` 条件进行过滤。
- `Using filesort`：需要额外排序操作，通常意味着未能利用索引排序，性能较低。
- `Using temporary`：需要使用临时表，常见于分组（`GROUP BY`）、排序等操作，可能影响性能。
- `Using join buffer`：使用了连接缓存，通常出现在无法通过索引完成关联时。
- `Impossible WHERE`：`WHERE` 条件永远不成立，不会返回任何结果。
- `Distinct`：使用了去重操作。
- `FirstMatch`、`LooseScan` 等：表示优化器采用了特定的优化策略。

通过分析 `Extra` 字段，可以进一步了解查询执行的细节，发现潜在的性能问题，并针对性地优化 SQL 语句。

## 解析案例
### 案例一：简单主键查询

```sql
EXPLAIN SELECT * FROM employees WHERE id = 1001;
```

| id | select_type | table     | type   | possible_keys | key     | key_len | ref   | rows | filtered | Extra       |
|----|-------------|-----------|--------|---------------|---------|---------|-------|------|----------|-------------|
| 1  | SIMPLE      | employees | const  | PRIMARY       | PRIMARY | 4       | const | 1    | 100.00   | NULL        |

**解析：**
- `type` 为 `const`，表示通过主键唯一定位一行，效率最高。
- `key` 使用了主键索引，查询性能优。

### 案例二：范围查询与索引使用

```sql
EXPLAIN SELECT * FROM employees WHERE age > 30 AND age < 40;
```

| id | select_type | table     | type  | possible_keys | key   | key_len | ref   | rows | filtered | Extra        |
|----|-------------|-----------|-------|---------------|-------|---------|-------|------|----------|--------------|
| 1  | SIMPLE      | employees | range | idx_age       | idx_age | 4     | NULL  | 50   | 100.00   | Using where  |

**解析：**
- `type` 为 `range`，使用了 `age` 字段的索引进行范围扫描。
- `Extra` 显示 `Using where`，表示还需通过条件过滤。

### 案例三：多表关联查询

```sql
EXPLAIN SELECT e.name, d.name FROM employees e JOIN departments d ON e.department_id = d.id WHERE d.location = '北京';
```

| id | select_type | table | type   | possible_keys | key         | key_len | ref           | rows | filtered | Extra        |
|----|-------------|-------|--------|---------------|-------------|---------|---------------|------|----------|--------------|
| 1  | SIMPLE      | d     | ref    | PRIMARY,location | location | 102     | const         | 2    | 100.00   | Using where  |
| 1  | SIMPLE      | e     | ref    | department_id | department_id | 4     | d.id          | 10   | 100.00   | NULL         |

**解析：**
- 先通过 `departments` 的 `location` 索引筛选，再通过 `department_id` 索引关联 `employees`。
- 两表均利用了索引，查询效率较高。

### 案例四：全表扫描

```sql
EXPLAIN SELECT * FROM employees WHERE salary > 10000;
```

| id | select_type | table     | type | possible_keys | key   | key_len | ref   | rows | filtered | Extra        |
|----|-------------|-----------|------|---------------|-------|---------|-------|------|----------|--------------|
| 1  | SIMPLE      | employees | ALL  | NULL          | NULL  | NULL    | NULL  | 500  | 50.00    | Using where  |

**解析：**
- `type` 为 `ALL`，表示全表扫描，没有可用索引。
- 建议为 `salary` 字段添加索引以优化查询。
