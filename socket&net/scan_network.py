import subprocess
import ipaddress
import platform
import concurrent.futures

# 配置参数
NETWORK = "192.168.8.0/24"  # 要检测的网段
TIMEOUT = 2  # 增加超时时间到2秒
THREADS = 4  # 最大并发数


def ping_host(ip):
    """检测单个IP是否能Ping通"""
    try:
        # 构造跨平台ping命令
        param = "-n 1 -w 2000" if platform.system().lower() == "windows" else "-c 1 -W 2"
        command = f"ping {param} {ip}"

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True,
            timeout=TIMEOUT
        )

        # 更可靠的响应判断
        if "TTL=" in result.stdout.upper() and result.returncode == 0:
            print(f"检测到活跃主机: {ip}")  # 实时显示进度
            return ip
        return None
    except Exception as e:
        print(f"检测 {ip} 时发生异常: {str(e)}")
        return None


def main():
    try:
        # 生成有效IP列表（排除网络地址和广播地址）
        network = ipaddress.IPv4Network(NETWORK, strict=False)
        ips = [str(host) for host in network.hosts()]

        print(f"开始扫描 {NETWORK} 网段，共 {len(ips)} 个IP...")

        # 使用线程池提高效率
        active_ips = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
            futures = {executor.submit(ping_host, ip): ip for ip in ips}
            for future in concurrent.futures.as_completed(futures):
                if (result := future.result()) is not None:
                    active_ips.append(result)

        # 按IP顺序输出结果
        if active_ips:
            print("\n✅ 活跃主机列表：")
            for ip in sorted(active_ips, key=lambda x: list(map(int, x.split('.')))):
                print(f"  → {ip}")
            else:
                print("\n❌ 未检测到活跃主机，可能原因：")
            print("  1. 本机不属于 192.168.8.x 网段")
            print("  2. 目标设备禁用了ICMP响应")
            print("  3. 防火墙/安全软件阻止了Ping请求")
            print("  4. 网络连接异常")

    except ValueError as e:
        print(f"错误：网段格式错误 - {str(e)}")
    except PermissionError:
        print("错误：需要管理员权限运行！")
    except KeyboardInterrupt:
        print("\n用户中断操作")


if __name__ == "__main__":
    main()