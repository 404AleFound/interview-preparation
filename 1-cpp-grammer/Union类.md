# Union：一种节省空间的类

union是一种特殊的类。一个Union可以有多个数据成员，但是在任意时刻只有一个数据成员可以有指。

当我们给union的某个成员赋值之后，该union的其他成员就编程未定义的状态了。

分配给union对象的存储空间至少要容纳它的最大的数据成员

## 定义union

```C++
union Token {
    char cval;
    int ival;
    double dval;
};
// union关键字，union类名，union数据成员声明
```

## 使用union

## 匿名union

