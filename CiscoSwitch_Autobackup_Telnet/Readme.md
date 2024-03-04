# Cisco交换机配置批量备份工具

## 功能说明

此Python脚本程序用于批量备份Cisco交换机配置的Python工具。通过Telnet连接到Cisco交换机，自动批量获取网络设备的配置信息，并保存设备端口占用情况及整机运行配置。主要功能包括：
- 自动读取IP列表文件进行批量自动化备份配置及所有端口信息
- 支持多线程并发处理（默认10线程）
- 自动生成按日期分类的备份目录（格式：`YYYY-MM-DD-BackupData`）
- 每台设备备份文件包含设备名称和IP地址标识
- 智能过滤文件名非法字符
- 实时显示备份进度和结果统计
- 支持带中文环境的设备名称处理

## 环境要求

- Python 3.10或更低版本（`telnetlib`模块将在Python 3.11中已被弃用）
- 操作系统：Windows/Linux/MacOS

## 快速开始

### 1. 准备IP列表文件
在脚本同目录下创建`Cisco_ip.txt`文件，每行填写一个交换机IP地址

示例文件内容：
```
192.168.1.1
10.10.10.2
172.16.8.3
```

### 2. 运行备份脚本
```bash
python Cisco_Backup_Tool.py
```

> 也可以使用各IDE工具打开，在终端执行，如`Pychrm`，`VScode`等。

### 3. 输入登录信息

```text
请输入用户名: admin
请输入密码: (密码输入时不可见)
```

> 此处交换机登录账户凭据是统一的，由LDAP域控管理，所以一次输入，全程使用，直至程序运行结束。

## 输出示例

### 备份过程显示
```text
192.168.1.1 配置备份成功，保存到 ./2024-03-04-BackupData/192.168.1.1_SW-Core.txt
10.10.10.2 连接或备份失败: 登录失败
172.16.8.3 配置备份成功，保存到 ./2024-03-04-BackupData/172.16.8.3_SW-Office.txt
```

### 最终统计信息
```text
备份成功：2台，失败：1台，一共耗时：1分38秒
```

### 生成文件结构
```
├── 2024-03-04-BackupData
│   ├── 192.168.1.1_SW-Core.txt
│   └── 172.16.8.3_SW-Office.txt
├── Cisco_Backup_Tool.py
└── Cisco_ip.txt
```

## 备份文件内容示例
```text
端口描述信息:
SW-CORE-01#show interfaces description
Interface                      Status         Protocol Description
Po1                            up             up       UPLINK-TO-DISTRIBUTION-SWITCH
Gi0/1                          up             up       UPLINK-TO-DISTRIBUTION-SW1
Gi0/2                          up             up       UPLINK-TO-DISTRIBUTION-SW2
Gi0/3                          up             up       SERVER-VMWARE-ESXi-01
Gi0/4                          up             up       SERVER-VMWARE-ESXi-02
Gi0/5                          up             up       SERVER-VMWARE-ESXi-03
Gi0/6                          up             up       SERVER-VMWARE-ESXi-04
Gi0/7                          up             up       SERVER-DATABASE-01
Gi0/8                          up             up       SERVER-DATABASE-02
Gi0/9                          up             up       SERVER-APP-01
Gi0/10                         up             up       SERVER-APP-02
...

运行配置:
uilding configuration...

Current configuration : 12458 bytes
!
! Last configuration change at 15:30:45 CST Mon Mar 4 2024
! NVRAM config last updated at 10:15:22 CST Mon Mar 4 2024
!
version 15.2
no service pad
service timestamps debug datetime msec localtime
service timestamps log datetime msec localtime
service password-encryption
!
hostname SW-CORE-01
!
boot-start-marker
boot-end-marker
!
enable secret 5 $1$Xk9.$r3kf8H5gQpLPVJkF3jNZa1
!
username admin privilege 15 secret 5 $1$LkP.$fEqS3t.zLPwYbGCxIbVQA0
no aaa new-model
clock timezone CST 8 0
!
ip domain-name example.com
!
!
ip dhcp snooping vlan 10,20,30,40
ip dhcp snooping
!
!
crypto pki trustpoint TP-self-signed-1234567890
 enrollment selfsigned
 subject-name cn=IOS-Self-Signed-Certificate-1234567890
 revocation-check none
 rsakeypair TP-self-signed-1234567890
...
interface Port-channel1
 description UPLINK-TO-DISTRIBUTION-SWITCH
 switchport trunk encapsulation dot1q
 switchport trunk allowed vlan 10,20,30,40,50,100,200
 switchport mode trunk
 spanning-tree portfast trunk
!
interface GigabitEthernet0/1
 description UPLINK-TO-DISTRIBUTION-SW1
 switchport trunk encapsulation dot1q
 switchport trunk allowed vlan 10,20,30,40,50,100,200
 switchport mode trunk
 channel-group 1 mode active
!
interface GigabitEthernet0/2
 description UPLINK-TO-DISTRIBUTION-SW2
 switchport trunk encapsulation dot1q
 switchport trunk allowed vlan 10,20,30,40,50,100,200
 switchport mode trunk
 channel-group 1 mode active
!
...
```

## 注意事项

1. 确保交换机已开启Telnet服务
2. 账号需具有enable权限
3. 网络防火墙需开放TCP 23端口
4. 特殊字符处理规则：
   - 保留：字母、数字、空格、._-
   - 自动过滤：<>:"/\|?* 等非法字符
5. 单个配置文件最大支持30秒读取时间
6. 建议在低峰时段执行批量备份操作

## 版本更新

Version 2.82 (2024-03-04)
- 新增端口描述信息采集功能
- 优化多线程稳定性
- 增强特殊字符处理能力
- 增加连接超时重试机制

## 授权信息
本工具遵循MIT开源协议，作者：Geek0ne

> 提示：建议定期清理历史备份文件，建议保留周期不超过90天

```

这个README文件采用结构化设计，包含快速使用指引和技术细节说明，既适合运维人员直接使用，也便于二次开发参考。文件内容与实际脚本功能完全对应，并提供了典型使用场景的完整示例。