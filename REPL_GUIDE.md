# PyLisp REPL 使用指南

## 简介

PyLisp REPL (Read-Eval-Print Loop) 是一个交互式的 Lisp 解释器环境，允许你实时编写和测试 Lisp 代码。

## 启动 REPL

### 交互模式

```bash
python repl.py
```

### 调试模式

```bash
python repl.py -d
```

### 执行文件

```bash
python repl.py -f your_script.scm
```

## 基本使用

### 1. 简单算术运算

```scheme
pylisp> (+ 1 2)
3

pylisp> (* 3 4)
12

pylisp> (- 10 5)
5

pylisp> (/ 20 4)
5.0
```

### 2. 定义变量

```scheme
pylisp> (define x 42)
None

pylisp> x
42

pylisp> (define name "Alice")
None

pylisp> name
"Alice"
```

### 3. 定义函数

```scheme
pylisp> (define (square n) (* n n))
None

pylisp> (square 5)
25

pylisp> (define (add a b) (+ a b))
None

pylisp> (add 10 20)
30
```

### 4. 多行输入

REPL 支持多行输入，会自动检测括号是否平衡：

```scheme
pylisp> (define (factorial n)
.......   (if (= n 0)
.......       1
.......       (* n (factorial (- n 1)))))
None

pylisp> (factorial 5)
120
```

### 5. 闭包

```scheme
pylisp> (define (make-adder n)
.......   (lambda (x) (+ x n)))
None

pylisp> (define add5 (make-adder 5))
None

pylisp> (add5 10)
15

pylisp> (add5 20)
25
```

### 6. 递归和尾调用优化

```scheme
pylisp> (define (sum from to)
.......   (begin
.......     (define (iter from to acc)
.......       (if (> from to)
.......           acc
.......           (iter (+ from 1) to (+ acc from))))
.......     (iter from to 0)))
None

pylisp> (sum 1 100)
5050

pylisp> (sum 1 10000)
50005000
```

### 7. 列表操作

```scheme
pylisp> (define mylist (cons 1 (cons 2 (cons 3 None))))
None

pylisp> (car mylist)
1

pylisp> (cdr mylist)
(2 3)

pylisp> (car (cdr mylist))
2
```

### 8. 条件表达式

```scheme
pylisp> (define (abs n)
.......   (if (< n 0)
.......       (- 0 n)
.......       n))
None

pylisp> (abs -5)
5

pylisp> (abs 10)
10
```

### 9. Let 绑定

```scheme
pylisp> (let ((x 10) (y 20))
.......   (+ x y))
30

pylisp> (define (circle-area r)
.......   (let ((pi 3.14159))
.......     (* pi r r)))
None

pylisp> (circle-area 5)
78.53975
```

## 特殊命令

在 REPL 中，你可以使用以下特殊命令：

- `:help` 或 `help` - 显示帮助信息
- `:quit` 或 `:exit` 或 `quit` 或 `exit` - 退出 REPL
- `:debug on` - 开启调试模式（显示虚拟机指令）
- `:debug off` - 关闭调试模式

示例：

```scheme
pylisp> :debug on
Debug mode enabled

pylisp> (+ 1 2)
OpLoadGlobal  1 # +
OpLoadConst 2 # 1
OpLoadConst 3 # 2
OpBinOp  +
OpPop 1
3

pylisp> :debug off
Debug mode disabled

pylisp> :quit
Bye!
```

## 内置函数

### 算术运算
- `+`, `-`, `*`, `/` - 基本运算
- `modulo`, `quotient`, `remainder` - 取模和整数除法

### 比较运算
- `=`, `>`, `<`, `<=`, `>=` - 比较运算符
- `not` - 逻辑非

### 列表操作
- `cons` - 构造列表
- `car` - 获取列表第一个元素
- `cdr` - 获取列表剩余部分
- `list` - 创建列表
- `length` - 获取列表长度

### 类型判断
- `null?` - 判断是否为空
- `pair?` - 判断是否为配对
- `number?` - 判断是否为数字
- `string?` - 判断是否为字符串

### 输入输出
- `display` - 打印输出
- `newline` - 输出换行

## 特殊形式

- `define` - 定义变量或函数
- `lambda` - 创建匿名函数
- `let` - 局部变量绑定
- `if` - 条件表达式
- `begin` - 顺序执行多个表达式
- `quote` 或 `` ` `` - 引用（暂不完全支持）

## 示例程序

### 斐波那契数列

```scheme
(define (fib n)
  (if (<= n 1)
      n
      (+ (fib (- n 1))
         (fib (- n 2)))))

(display (fib 10))  ; 输出 55
```

### 列表求和

```scheme
(define (sum-list lst)
  (if (null? lst)
      0
      (+ (car lst)
         (sum-list (cdr lst)))))

(define nums (list 1 2 3 4 5))
(display (sum-list nums))  ; 输出 15
```

### 快速排序（概念示例）

```scheme
(define (filter pred lst)
  (if (null? lst)
      None
      (if (pred (car lst))
          (cons (car lst) (filter pred (cdr lst)))
          (filter pred (cdr lst)))))
```

## 错误处理

当发生错误时，REPL 会显示错误信息但不会退出：

```scheme
pylisp> (+ 1 undefined-var)
Error: KeyError: 'undefined-var'

pylisp> (/ 1 0)
Error: ZeroDivisionError: division by zero

pylisp> (this is not valid lisp)
Error: ParseException: ...
```

在调试模式下，会显示完整的堆栈跟踪。

## 退出 REPL

你可以通过以下方式退出：

1. 输入 `:quit` 或 `:exit`
2. 输入 `quit` 或 `exit`
3. 按 `Ctrl+D` (Unix/Linux/Mac) 或 `Ctrl+Z` (Windows)
4. 按 `Ctrl+C` 两次

## 提示

1. **多行编辑**: REPL 会自动检测括号平衡，按回车后会继续等待输入直到表达式完整
2. **历史记录**: 使用上下箭头键可以浏览历史命令（如果终端支持）
3. **调试模式**: 使用 `:debug on` 可以查看编译后的虚拟机指令，有助于理解代码执行过程
4. **文件执行**: 对于较长的程序，建议保存为 `.scm` 文件后使用 `-f` 参数执行

## 已知限制

1. 不支持空列表字面量 `()`，请使用 `None` 代替
2. `quote` 和反引号语法支持有限
3. 暂不支持宏系统
4. 错误信息可能不够友好

## 反馈

如有问题或建议，请查看 README.md 或提交 issue。

享受 Lisp 编程的乐趣！
