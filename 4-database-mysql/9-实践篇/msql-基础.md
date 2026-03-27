# mysql 基础

## 全表查询
```sql
select * from student;
```

## 选择查询
```sql
select name, age from student;
```

## 查询别名
```sql
select name as 学生姓名, age as 学生年龄 from student
```

```sql
select name, score, score * 2 as double_score from student
```
```sql
select name, score from student where name = '鱼皮'
```

```sql
select name, age, salary from employees where name != '小张';

select name, age, salary from employees where salary > 5500;

select name, age, salary from employees where age between 25 and 30;
```