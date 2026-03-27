[toc]

# 完美转发（Perfect Forwarding）介绍

> [!NOTE]
>
> **完美转发**
>
> * 什么是完美转发？
>   * 用于将函数模板中的参数**精确地传递**给另一个函数，无论参数是左值还是右值，类型修饰符（const、volatile等）都能被完整保留。
> * 为什么需要完美转发？
>   * 某些函数需要将其一个或多个实参连同类型不变地转发给其他函数，不想失去函数参数的“左值/右值”和“`const`/`const`”信息。
> * 如何实现完美转发?
>   * 万能引用和`std::forward`
> * `std::forward`机理深度解析
>   * <font color='red'>有点理解困难</font>

完美转发是C++11引入的一个特性，用于将函数模板中的参数**精确地传递**给另一个函数，无论参数是左值还是右值，类型修饰符（const、volatile等）都能被完整保留。

简而言之，完美转发允许你把函数模板参数的“值类别”（value category）和类型修饰符无损地传递下去。

## 为什么需要完美转发：保留类修饰符

某些函数需要将其一个或多个实参连同类型不变地转发给其他函数，不想失去函数参数的“左值/右值”和“`const`/`const`”信息。

- 直接传参有可能造成不必要的拷贝或移动。
- 如果只是使用普通引用或值传递，可能会破坏参数的原始类型和引用类别。
- 完美转发允许我们写出高效且类型安全的转发代码。

```C++
template <typename F, typename T1, typename T2>
void flip1(F f, T1 t1, T2 t2)
{
    f(t2, t1);
}
```

## 如何实现完美转发：右值引用和`std::forward`

利用 **模板类型参数推导**，结合 **右值引用** 和 **`std::forward`** ，实现完美转发。

**典型例子**

```c++
#include <iostream>
#include <utility>

void foo(int& x) {
    std::cout << "foo(int&): " << x << std::endl;
}

void foo(int&& x) {
    std::cout << "foo(int&&): " << x << std::endl;
}

template<typename T>
void perfectForward(T&& param) {
    // 完美转发
    foo(std::forward<T>(param));
}

int main() {
    int a = 10;
    perfectForward(a);      // 传递左值
    perfectForward(20);     // 传递右值
}
```

- `T&&` 在模板中是所谓的**转发引用**（又叫通用引用）。
- `std::forward<T>(param)` 会根据 `T` 推断的类型决定转发为左值引用还是右值引用。

## `std::forward`机理：万能引用

`std::forward` 是C++11引入的一个**完美转发辅助函数**，主要用于转发函数模板中的参数，**保持参数的值类别（左值或右值）不变**。

```C++
template<typename T>
void func(T&& param);
// 在这里虽然param是一个万能引用，可以绑定左值和右值
// 但是在`func`内部直接传给其他函数时，如果直接传`param`，编译器会将其与左值的版本匹配
// 无法和右值的重载函数匹配
```

`std::forward`的实现核心如下：

```C++
template<typename T>
T&& forward(std::remove_reference_t<T>& param) {
	return static_cast<T&&>(param);
}

// 传入int左值a，T被推断为左值的引用int&，函数返回int& &&，经过折叠变为int&
// 传入右值0，T被推断为
```

关键点介绍如下：

* `T&&`返回一个万能引用，而不是一个值，如果返回param对象，则相当于返回一个右值，那么这个函数就毫无意义了，所以需要`static_cast`类型转换为引用。
* 传入右值时T被推断为`int`，传入左值时T被推断为`int&`

<font color='red'>右值的引用类型是一个左值</font>