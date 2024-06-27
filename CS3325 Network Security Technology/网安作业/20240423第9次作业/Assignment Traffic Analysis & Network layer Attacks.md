# Assignment: Traffic Analysis & Network layer Attacks

<center>被巨人城墙保护的小组<center>
[TOC]

## Task 1: Traffic Analysis

> Please use wireshark to perform a traffic analysis on sjtu and other subnets(cs, se, acem). Tell us your finding.

+ 确保自己电脑有网。打开Wireshark，选择WLAN。

<img src=".\wireshark.png" style="zoom:67%;" />

+ 可以捕获到公网上的流量数据。

<img src=".\wireshark-sjtu.png" style="zoom:67%;" />

+ 利用ping查看各网站ip

```
> ping www.sjtu.edu.cn
> ping www.cs.sjtu.edu.cn
> ping www.se.sjtu.edu.cn
> ping www.acem.sjtu.edu.cn
```

得到IP：

| 域名                 | IP             |
| -------------------- | -------------- |
| www.sjtu.edu.cn      | 202.120.2.119  |
| www.cs.sjtu.edu.cn   | 202.120.35.204 |
| www.se.sjtu.edu.cn   | 202.120.40.4   |
| www.acem.sjtu.edu.cn | 202.120.35.201 |

+ 利用wireshark过滤规则查看指定数据包。

```
ip.src==202.120.2.119
```

<img src=".\wireshark-sjtu-edu.png" style="zoom:67%;" />

```
ip.src==202.120.35.204
```

<img src=".\wireshark-cs-sjtu-edu.png" style="zoom:67%;" />

```
ip.src==202.120.40.4
```

<img src=".\wireshark-se-sjtu-edu.png" style="zoom:67%;" />

```
ip.src==202.120.35.201
```

<img src=".\wireshark-acem-sjtu-edu.png" style="zoom:67%;" />

+ 可知sjtu.edu.cn的网站都在202.120这一网段下。



## Task2: Network layer Attacks

> Please try to test at least three network layer attacks.
>
> + Wifi jamming attack
> + IP sproofing attack
> + Mac sproofing attack
> + DHCP sproofing attack
> + ...
>
> Note: please record the technical details and evidence.

### ARP欺骗攻击[^1]

ARP欺骗的原理基于地址解析协议（ARP）的工作方式。在TCP/IP网络中，当一个设备需要与另一个设备通信时，它首先需要知道对方的物理（MAC）地址。ARP协议通过将IP地址映射到MAC地址来解决这个问题。而攻击者欺骗靶机，将出口路由器映射到攻击者的MAC地址，靶机信任了攻击者，把访问外部网络的数据包错误的发送给了攻击机的MAC地址，导致靶机收不到外网返回的数据包，导致网络中断。

#### 实验环境

+ VMware Workstation

  + 攻击者：Kali Linux 2024

  + 靶机：Ubuntu 22.04 LTS

+ 两台虚拟机网卡都选择特定虚拟网络VMnet8，使得两者处于同一局域网下。

<img src=".\arp-kali.png" style="zoom:67%;" />

<img src=".\arp-target.png" style="zoom:67%;" />



#### 实验过程

+ 首先，检查靶机网络状态，正常。

<img src=".\arp-before.png" style="zoom:67%;" />

+ 查看靶机地址与网关等信息。

```shell
(ubuntu)$ ifconfig
(ubuntu)$ arp -a
```

靶机IP地址为`192.168.6.131`，MAC地址为`00:0c:29:2c:e1:85`。

默认网关为`192.168.6.2`，MAC地址为`00:50:56:fc:2c:03`。

<img src=".\arp-target-默认网关+映射.png" style="zoom:67%;" />

+ 攻击者扫描，查询是否与靶机处在同一网段。

```shell
(kali)$ arp-scan 192.168.6.1-192.168.6.254
```

<img src=".\arp-scan.png" style="zoom:67%;" />

+ 攻击者伪装成靶机网关，攻击开始。

```shell
(kali)$ sudo arpspoof -i eth0 -t 192.168.6.131 192.168.6.2
```

 `arpspoof`：ARP欺骗工具。会发送虚假的ARP应答来毒化目标主机的ARP缓存。

`-i eth0`：指定了要使用的网络接口。

`-t 192.168.6.131`：指定靶机的IP地址。

`192.168.6.2`: 第二个参数，表示攻击者想要将自己伪装成的IP地址。在本实验中，攻击者伪装成靶机的默认网关。

<img src=".\arp-attack.png" style="zoom:67%;" />

+ 再次查看靶机网关。

```shell
(ubuntu)$ arp -a
```

<img src=".\arp-after-映射.png" style="zoom:67%;" />

可以看到靶机网关的MAC地址发生了变化，变成了攻击者的MAC地址，ARP欺骗攻击成功。

<img src=".\arp-kali-mac.png" style="zoom:67%;" />

+ 此时再尝试访问百度，始终连不上。说明ARP欺骗攻击成功。

<img src=".\arp-after.png" style="zoom:67%;" />



### DNS欺骗攻击[^2][^3]

DNS欺骗，也称为DNS缓存投毒，是指攻击者通过篡改DNS服务器的缓存信息，使得域名解析错误，导致用户在访问某个网站时被错误地重定向到另一个网站。

#### 实验环境

与上一实验相同。

#### 实验过程

+ 尝试访问百度和哔哩哔哩官网。

```shell
(ubuntu)$ ping www.baidu.com
(ubuntu)$ ping www.bilibili.com
```

`www.baidu.com`对应IP地址为`182.61.200.6`。

`www.bilibili.com`对应IP地址为`121.194.11.72`。

<img src=".\dns-before.png" style="zoom:67%;" />

+ 后续的攻击通过Ettercap和其集成的DNS攻击插件完成。Ettercap是一个网络嗅探工具。在Kali上修改配置文件`/etc/ettercap/etter.dns`，将`www.baidu.com`映射到B站的IP地址。

```
(kali)$ sudo vim /etc/ettercap/etter.dns
```

<img src=".\dns-etter.png" alt="dns-etter" style="zoom:67%;" />

+ 在Kali上打开Ettercap，选择网卡eth0，开始嗅探同一网段中的主机。可以看到靶机和其网关都在其中。

<img src=".\dns-sniff.png" alt="dns-sniff" style="zoom:67%;" />

+ 在MITM Menu中选择ARP Poisoning。

<img src=".\dns-set.png" alt="dns-set" style="zoom:67%;" />

+ 在Plugins中激活dns_spoof插件。

<img src=".\dns-plugin.png" alt="dns-plugin" style="zoom:67%;" />

+ 将靶机IP加到Target2，其默认网关加到Target1。

<img src=".\dns-attack.png" style="zoom:67%;" />

+ 攻击者开始攻击。

```shell
(kali) sudo ettercap -T -q -i eth0 -P dns_proof
```

<img src=".\dns-attack-start.png" alt="dns-attack-start" style="zoom:67%;" />

+ 此时再在靶机上尝试访问百度，发现其IP地址变成了B站的IP地址。说明DNS欺骗成功。

```shell
(ubuntu)$ ping www.baidu.com
```

<img src=".\dns-attack-success.png" alt="dns-attack-success" style="zoom:67%;" />

+ 在Kali上也可以看到，靶机对`www.baidu.com`的访问被重定向到了`121.194.11.72`。

<img src=".\dns-attack-success-kali.png" alt="dns-attack-success-kali" style="zoom:67%;" />



 ### MAC欺骗攻击[^4][^5]

MAC地址欺骗是数据链路层攻击，它是利用交换机端口学习的漏洞，通过客户端向交换机发送欺骗报文、攻击交换机的CAM表的方式，使交换机CAM表的记录与真实的主机对应MAC地址不一致，从而使交换机将报文错误转发给攻击者。

#### 实验环境

- eNSP
- VMware Station：Kali Linux 2024

#### 实验过程

+ 在eNSP中搭建拓扑。

<img src="D:.\mac-拓扑.png" style="zoom: 67%;" />

+ PC1配置

<img src=".\mac-pc1.png" style="zoom:67%;" />

+ PC2配置

<img src=".\mac-pc2.png" style="zoom:67%;" />

+ Cloud1配置，网卡选择VMnet8，vmware里Kali的网卡也选择VMnet8。

<img src=".\mac-cloud1.png" style="zoom:67%;" />

+ PC1向PC2发送UDP数据包。

<img src=".\mac-pc1向pc2发送.png" style="zoom:67%;" />

+ 在交换机LSW1上执行命令，查看CAM表。

```shell
<Huawei> display mac-address
```

发现CAM将PC1的MAC地址绑定到了端口GE0/0/1。

<img src=".\mac-address table.png" style="zoom:67%;" />

+ 再构造一个数据包，由PC1发给PC2，源MAC地址换成Kali的MAC地址`00-0c-29-d7-6a-c8`。

<img src=".\mac-pc1伪造mac向pc2发送.png" style="zoom:67%;" />

+ 再次查看CAM表。

```shell
<Huawei> display mac-address
```

发现CAM将Kali的MAC地址绑定到了端口GE0/0/1。

<img src=".\mac-address table-2.png" style="zoom:67%;" />

由上不难发现，交换机从某个端口收到一个数据包，它先读取包头中的源MAC地址，这样他就知道源MAC地址来自哪个端口，它会在CAM表中添加一条端口和MAC地址对应的记录。这种工作很高效，但如果交换机接收到了客户端伪造的源MAC地址的数据包，交换机同样也会将伪造的记录添加到CAM表中，作为信任的记录，这样就形成了MAC地址欺骗的漏洞。

+ 在PC1上持续伪造源MAC为Kali的MAC地址的UDP包，向PC2轮播。

<img src=".\mac-pc1向pc2轮播.png" style="zoom:67%;" />

+ PC2也向Kali发送UDP包。

<img src=".\mac-pc2向kali.png" style="zoom:67%;" />

+ 在LSW1的GE0/0/1和GE0/0/3端口同时抓包。

GE0/0/3的抓包结果：

<img src=".\mac-kali抓取结果.png" style="zoom:67%;" />

GE0/0/1的抓包结果：

<img src=".\mac-pc1抓取结果.png" style="zoom:67%;" />

显然，在LSW1的GE0/0/3端口没有抓到PC2发送给Kali的包，在LSW1的GE0/0/1端口却抓到了。说明MAC欺骗攻击成功。



## References

[^1]: [ARP欺骗（ARP spoofing）网络攻击实验](https://blog.csdn.net/2301_79215224/article/details/134938245?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522171325829616800211563568%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&amp;amp;request_id=171325829616800211563568&amp;amp;biz_id=0&amp;amp;utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_ecpm_v1~rank_v31_ecpm-21-134938245-null-null.142^v100^pc_search_result_base7&amp;amp;utm_term=IP%E4%BC%AA%E9%80%A0%E6%94%BB%E5%87%BB%E5%AE%9E%E9%AA%8C&amp;amp;spm=1018.2226.3001.4187)
[^2]: [网络欺骗实验](https://blog.csdn.net/qq_45655136/article/details/119425397?utm_medium=distribute.pc_relevant.none-task-blog-2~default~baidujs_utm_term~default-1-119425397-blog-134938245.235^v43^pc_blog_bottom_relevance_base2&amp;spm=1001.2101.3001.4242.2&amp;utm_relevant_index=4)
[^3]: [kali之dns欺骗攻击](https://www.bilibili.com/video/BV1og4y1A7dU/?spm_id_from=333.337.search-card.all.click&amp;vd_source=04646980cbd14157d5eb18131c4fab9e)
[^4]: [MAC地址欺骗与MAC地址泛洪攻击（eNSP环境演示）](https://blog.csdn.net/xrgzky/article/details/128125358?spm=1001.2101.3001.6650.2&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-2-128125358-blog-105388491.235%5Ev43%5Epc_blog_bottom_relevance_base2&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-2-128125358-blog-105388491.235%5Ev43%5Epc_blog_bottom_relevance_base2&utm_relevant_index=5)
[^5]: [Kali Linux—eNSP模拟交换机MAC地址泛洪攻击](https://blog.csdn.net/redwand/article/details/105388491)