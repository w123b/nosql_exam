# task2.py
from pymongo import MongoClient
from pymongo import WriteConcern
from pymongo.read_concern import ReadConcern

SID = "12403030209"
db_name = f"exam_{SID}"
client = MongoClient("mongodb://127.0.0.1:27017")
db = client[db_name]
inventory = db["inventory"]
orders = db["orders"]

STOCK = 9
BUY = 1

def reset_data():
    inventory.delete_many({})
    orders.delete_many({})
    inventory.insert_one({
        "_id": f"BOOK-{SID}",
        "title": "NoSQL数据库教材",
        "stock": STOCK
    })

def deduct_stock_one(requestId, forceError=False):
    session = client.start_session()
    session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(w="majority")
    )
    try:
        # 原子扣减：库存>=BUY才扣
        update_res = inventory.update_one(
            {"_id": f"BOOK-{SID}", "stock": {"$gte": BUY}},
            {"$inc": {"stock": -BUY}},
            session=session
        )
        if update_res.modified_count == 0:
            session.abort_transaction()
            return False, "库存不足或教材不存在"

        orders.insert_one({
            "_id": requestId,
            "bookId": f"BOOK-{SID}",
            "studentId": SID,
            "quantity": BUY
        }, session=session)

        if forceError:
            raise Exception("主动抛出异常，测试回滚")

        session.commit_transaction()
        return True, "订购成功"
    except Exception as e:
        session.abort_transaction()
        return False, str(e)
    finally:
        session.end_session()

def run_scene(scene_name, req_id, forceError=False):
    reset_data()
    init_inv = inventory.find_one({"_id": f"BOOK-{SID}"})["stock"]
    ok, msg = deduct_stock_one(req_id, forceError)
    final_inv = inventory.find_one({"_id": f"BOOK-{SID}"})["stock"]
    order_cnt = orders.count_documents({})
    print(f"【{scene_name}】")
    print(f"初始库存:{init_inv}, 购买量:{BUY}, 结果:{ok}, 信息:{msg}")
    print(f"最终库存:{final_inv}, 订单数:{order_cnt}\n")

if __name__ == "__main__":
    # T1 正常订购
    run_scene("T1 正常订购", "req001", forceError=False)
    # T2 库存不足：连续多次买到不够
    reset_data()
    print("【T2 连续购买直到库存不足】")
    cnt = 0
    while True:
        rid = f"req_t2_{cnt}"
        ok,_ = deduct_stock_one(rid, False)
        if not ok:
            break
        cnt +=1
    final = inventory.find_one({"_id":f"BOOK-{SID}"})["stock"]
    print(f"T2成功次数:{cnt}, 最后库存:{final}\n")

    # T3 中途异常 forceError=True
    run_scene("T3 中途异常回滚", "req003", forceError=True)

    # T4 连续购买 Stock/Buy +1次
    reset_data()
    print("【T4 连续 Stock/Buy +1 次订购】")
    total = STOCK // BUY + 1
    succ=0
    for i in range(total):
        rid = f"req_t4_{i}"
        ok,_ = deduct_stock_one(rid, False)
        if ok:
            succ +=1
    fin = inventory.find_one({"_id":f"BOOK-{SID}"})["stock"]
    print(f"T4 尝试次数:{total},成功:{succ},最终库存:{fin}\n")