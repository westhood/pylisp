# pylisp: 一个简单的 Python Lisp 实现

## 描述 ##

PyList 中使用的语法类似于 [SICP](http://mitpress.mit.edu/sicp/) 中的 Scheme 语法。您可以将此项目视为学习 [SICP](http://mitpress.mit.edu/sicp/) 第 4 章和第 5 章后的练习。

## 示例 ##
1. 对整数求和的循环

    ```
    (define (sum from to)
    (begin
        (define (iter from to acc)
            (if (> from to)
                acc
                (iter (+ from 1) to (+ acc from))))
        (iter from to 0)))
    (display (sum 1 100000))
    ```
2. 创建一个闭包

    ```
    (define (mul x y) (* x y))
    (define (muln n) (lambda (x) (mul x n)))
    (define mul2 (muln 2))
    (define mul3 (muln 3))
    (assert (mul2 2) 4)
    (assert (mul3 3) 9)
    (assert (mul3 3.3) (* 3 3.3))
    ```

##完整功能##

* 基本的 Lisp 形式，如 `let`、`lambda`、`if`、`quote` 等。
* 源文件将被编译为虚拟机指令。指令尚无字节码格式。
* 指令将由基于堆栈的虚拟机执行。
* 词法作用域（又名闭包）。
* 尾调用优化。
* call/cc 的一个非常低效的实现（在 master 分支中已删除）


## 待办事项 ##

* 字节码格式。
* 像 Common Lisp 中的宏系统。
* RELP。
* 基于寄存器的虚拟机。
