# ===================================================================================
# 作者:      Geek0ne
# 功能:      批量备份Cisco交换机配置
# 版本:      Version 2.82
# 日期:      2024-03-04
# 运行:      支持到Python <= 3.10  详见 https://docs.python.org/3/library/telnetlib.html      
# ===================================================================================

import telnetlib
import time
import os
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import getpass

def sanitize_filename(filename):
    """移除文件名中的非法字符，保留字母、数字、空格、点、下划线和破折号"""
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', filename)

def read_until(tn, expected, timeout):
    """带超时和重试机制的读取函数"""
    end_time = time.time() + timeout
    result = b''
    while time.time() < end_time:
        result += tn.read_very_eager()
        if expected in result:
            return result
        time.sleep(0.1)
    raise Exception(f"读取超时: 未能在{timeout}秒内读取到预期结果")

def backup_config(ip, user, password):
    try:
        tn = telnetlib.Telnet(ip, timeout=10)
        
        tn.read_until(b"Username: ", timeout=10)
        tn.write(user.encode('ascii') + b"\n")
        tn.read_until(b"Password: ", timeout=10)
        tn.write(password.encode('ascii') + b"\n")
        
        login_result = read_until(tn, b"#", 10)
        if b"#" not in login_result:
            raise Exception("登录失败")
        
        tn.write(b'terminal length 0\n')  # 取消分屏显示
        read_until(tn, b"#", 10)
        
        # 获取设备名
        tn.write(b'show running-config | include hostname\n')
        device_name_output = read_until(tn, b"#", 10).decode('utf-8')
        
        match = re.search(r'hostname (\S+)', device_name_output)
        if match:
            device_name = match.group(1)
        else:
            raise Exception("无法提取设备名")
        
        device_name = sanitize_filename(device_name)  # 清理设备名
        
        # 获取端口占用描述信息
        tn.write(b'show interfaces description\n')
        port_output = read_until(tn, b"#", 5).decode('utf-8')
        
        # 获取运行配置
        tn.write(b'show running-config\n')
        config_output = read_until(tn, b"#", 30).decode('utf-8')
        
        # 获取当前日期并创建备份目录
        current_date = datetime.now().strftime('%Y-%m-%d')
        backup_dir = f'./{current_date}-BackupData'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # 写入备份文件
        backup_file_path = f'{backup_dir}/{ip}_{device_name}.txt'
        with open(backup_file_path, 'w') as backup:
            backup.write("端口描述信息:\n")
            backup.write(port_output)
            backup.write("\n运行配置:\n")
            backup.write(config_output)
        
        print(f"{ip} 配置备份成功，保存到 {backup_file_path}")
        tn.close()
        return True
    
    except Exception as e:
        print(f"{ip} 连接或备份失败: {e}")
        return False

if __name__ == '__main__':
    start_time = time.time()
    
    ip_list = []
    
    # 从文件中读取IP地址
    with open('Cisco_ip.txt', 'r') as file:
        for line in file:
            ip = line.strip()
            ip_list.append(ip)
    
    user = input("请输入用户名: ")
    password = getpass.getpass("请输入密码: ")
    
    print("正在执行中，请稍候...")

    success_count = 0
    failure_count = 0
    
    # 并行备份多个设备
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(backup_config, ip, user, password) for ip in ip_list]
        for future in as_completed(futures):
            result = future.result()
            if result:
                success_count += 1
            else:
                failure_count += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    minutes, seconds = divmod(total_time, 60)
    
    print(f"备份成功：{success_count}台，失败：{failure_count}台，一共耗时：{int(minutes)}分{int(seconds)}秒")
