# task4.py 加分题：Pipeline对比
import redis
import time

studentId = "12403030209"
prefix = f"exam:{studentId}:seq:"
r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)
N = 1000

# 清空旧数据
for i in range(1, N+1):
    r.delete(f"{prefix}{i}")

# 方案A：逐条普通写入
start_a = time.time()
for i in range(1, N+1):
    r.set(f"{prefix}{i}", f"value-{studentId}-{i}")
end_a = time.time()
cost_a = (end_a - start_a) * 1000

# 清空
for i in range(1, N+1):
    r.delete(f"{prefix}{i}")

# 方案B：Pipeline批量写入
pipe = r.pipeline()
start_b = time.time()
for i in range(1, N+1):
    pipe.set(f"{prefix}{i}", f"value-{studentId}-{i}")
pipe.execute()
end_b = time.time()
cost_b = (end_b - start_b) * 1000

print("===== Task4 写入性能对比 N=1000 =====")
print(f"方案A（逐条）耗时：{cost_a:.2f} ms")
print(f"方案B（Pipeline）耗时：{cost_b:.2f} ms")
print("""
简答：
Pipeline减少客户端与Redis之间来回网络RTT，多条命令打包一次性发送、一次性返回，降低网络开销，速度更快；
逐条写入每一条都要单独网络往返，网络等待开销大，更慢。
""")