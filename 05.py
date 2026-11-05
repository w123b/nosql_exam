# task3.py
import redis
import time

studentId = "12403030209"
r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)
prefix = f"exam:{studentId}:"

# ========== 1. Hash 学生信息 ==========
stu_hash_key = prefix + "student"
r.delete(stu_hash_key)
r.hset(stu_hash_key, mapping={
    "studentId": studentId,
    "studentName": "张三",
    "className": f"COURSE-{studentId}-01",
    "status": "learning"
})
print("===== 1.Hash学生信息 =====")
print("单独读取 studentName：", r.hget(stu_hash_key, "studentName"))
print("单独读取 status：", r.hget(stu_hash_key, "status"))
full_hash = r.hgetall(stu_hash_key)
print("完整Hash：", full_hash)

# ========== 2. Set 已完成章节 ==========
set_key = prefix + "chapters"
r.delete(set_key)
chap_list = ["CH01", "CH02", "CH02", "CH03"]
for c in chap_list:
    cnt = r.sadd(set_key, c)
    print(f"提交 {c}，本次新增数量：{cnt}")
all_chap = r.smembers(set_key)
print("全部已完成章节：", all_chap)
print("集合元素总数：", r.scard(set_key))
print("CH02 是否完成：", r.sismember(set_key, "CH02"))
print("CH04 是否完成：", r.sismember(set_key, "CH04"))

# ========== 3. ZSet 成绩排行 ==========
zkey = prefix + "score_rank"
r.delete(zkey)
r.zadd(zkey, {
    studentId: 89,
    "demo01": 90,
    "demo02": 60,
    "demo03": 80,
    "demo04": 80
})
print("\n===== 3.ZSet成绩排行 =====")
top3 = r.zrevrange(zkey, 0, 2, withscores=True)
print("分数从高到低前3名：", top3)
# 更新本人分数 +10
r.zincrby(zkey, 10, studentId)
print("本人分数+10之后：")
new_top3 = r.zrevrange(zkey, 0, 2, withscores=True)
print("更新后前3名：", new_top3)
# 查询本人名次（从0开始，+1转为第1名）
rank = r.zrevrank(zkey, studentId) + 1
print(f"本人 {studentId} 当前名次：第{rank}名")

# ========== 4. 会话生命周期 String 5s过期 ==========
session_key = prefix + "session"
r.delete(session_key)
r.setex(session_key, 5, "自定义会话标识")
print("\n===== 4.会话过期验证 =====")
ttl1 = r.ttl(session_key)
val1 = r.get(session_key)
print("创建立刻读取，value：", val1, " 剩余TTL：", ttl1)
print("等待6秒...")
time.sleep(6)
val2 = r.get(session_key)
ttl2 = r.ttl(session_key)
print("6s后读取，value：", val2, " 剩余TTL：", ttl2)

# ========== 5.简答（输出在控制台，提交可复制） ==========
print("\n===== 5.数据类型简答 =====")
ans = """
Hash：适合存储对象、多条属性（学生信息），字段独立读写；
Set：无序不重复集合，适合去重场景（已学章节）；
Sorted Set(ZSet)：带权重有序集合，适合排行榜、排序需求；
String：简单K-V，适合短文本、验证码、临时会话。
"""
print(ans)