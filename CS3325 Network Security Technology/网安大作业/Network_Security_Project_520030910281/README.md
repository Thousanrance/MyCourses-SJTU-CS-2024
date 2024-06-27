# Network Security Project: RSA, CCA2 and OAEP

## 文件树

```
Network_Security_Project_520030910281
│  README.md
|  Report.pdf # 报告
│
├─Task 1
│      RSA.ipynb                     # Code与运行结果
│      RSA_Moduler.txt               # RSA 模N
│      RSA_p.txt                     # RSA 大素数p
│      RSA_q.txt                     # RSA 大素数q
│      RSA_Public_Key.txt            # RSA 公钥对(N, e)
│      RSA_Secret_Key.txt            # RSA 私钥对(N, d)
│      Raw_Message.txt               # 明文消息
│      Encrypted_Message.txt         # RSA加密的密文
│
├─Task 2
│      CCA2.ipynb                    # Code与运行结果
│      RSA_Public_Key.txt            # RSA 公钥对(N, e) 来自Task1
│      RSA_Secret_Key.txt            # RSA 私钥对(N, d) 来自Task1
│      WUP_Request.txt               # WUP_Request明文
│      AES_Key.txt                   # AES密钥
│      AES_Encrypted_WUP.txt         # AES加密后的WUP_Request
│      History_Message.txt           # 历史消息 包括AES加密的WUP_Request和RSA加密的AES密钥
│
└─Task 3
       OAEP.ipynb                    # Code与运行结果
       RSA_Public_Key.txt            # RSA 公钥对(N, e) 来自Task1
       RSA_Secret_Key.txt            # RSA 私钥对(N, d) 来自Task1
       Random_Number.txt             # OAEP 随机数r
       Message_After_Padding.txt     # OAEP填充后的消息
       Encrypted_Message.txt         # OAEP-RSA加密的密文
```



## 运行说明

+ Jupyter Notebook文件已保留了所有运行结果。

+ 若需再次运行，请直接运行所有单元格。
+ 请确保已安装了以下依赖库：Crypto，binascii，hashlib。
