"""从线上 ECS 导出数据库并导入到本地

通过 admin exec-sql API 导出所有表结构和数据，在本地重建
"""
import requests
import sqlite3
import json
import os

BASE_URL = "http://106.14.99.100:8000"
# 目标库 = <项目根>/quiz-data/quiz.db（数据库唯一合法路径，本地开发 + Docker 卷统一用这一个）
# 旧版误指向 src/quiz.db（config 默认库），会导致拉库到错误位置，已修正。
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DB = os.path.join(PROJECT_ROOT, "quiz-data", "quiz.db")


def login():
    """登录获取 token"""
    resp = requests.post(
        BASE_URL + "/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if resp.status_code != 200:
        raise Exception(f"登录失败: {resp.text}")
    return resp.json()["access_token"]


def exec_sql(token, sql):
    """执行 SQL 查询"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    resp = requests.post(
        BASE_URL + "/api/admin/exec-sql",
        headers=headers,
        json={"sql": sql, "script": False}
    )
    if resp.status_code != 200:
        raise Exception(f"SQL 执行失败: {resp.text}")
    return resp.json()


def main():
    print("=" * 60)
    print("从线上 ECS 导出数据库")
    print("=" * 60)

    # 1. 登录
    print("\n[1/5] 登录线上系统...")
    token = login()
    print("  登录成功")

    # 2. 获取所有表名
    print("[2/5] 获取表结构...")
    result = exec_sql(token, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row["name"] for row in result["rows"]]
    # 跳过 sqlite_sequence（SQLite 内部保留表，无法手动创建）
    tables = [t for t in tables if t != "sqlite_sequence"]
    print(f"  找到 {len(tables)} 张表（已排除 sqlite_sequence）")

    # 3. 获取每张表的结构和数据
    print("[3/5] 导出表结构和数据...")
    
    # 先备份本地数据库
    if os.path.exists(LOCAL_DB):
        backup_path = LOCAL_DB + ".old"
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(LOCAL_DB, backup_path)
        print(f"  已备份旧数据库到: {backup_path}")

    # 连接本地 SQLite
    conn = sqlite3.connect(LOCAL_DB)
    cursor = conn.cursor()

    for table in tables:
        print(f"\n  处理表: {table}")
        
        # 获取表结构
        schema_result = exec_sql(token, f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        if schema_result["rows"]:
            create_sql = schema_result["rows"][0]["sql"]
            print(f"    创建表: {create_sql[:100]}...")
            cursor.execute(create_sql)
        
        # 获取所有列名
        cols_result = exec_sql(token, f"PRAGMA table_info('{table}')")
        if cols_result["rows"]:
            columns = [row["name"] for row in cols_result["rows"]]
        else:
            columns = []
        
        if not columns:
            print(f"    表为空，跳过")
            continue
        
        # 获取数据行数
        count_result = exec_sql(token, f"SELECT COUNT(*) as cnt FROM {table}")
        row_count = count_result["rows"][0]["cnt"]
        print(f"    共 {row_count} 行数据")
        
        if row_count == 0:
            continue
        
        # 分批导入数据（每次 500 行）
        batch_size = 500
        total_imported = 0
        
        while total_imported < row_count:
            offset = total_imported
            data_result = exec_sql(token, f"SELECT * FROM {table} LIMIT {batch_size} OFFSET {offset}")
            
            if not data_result["rows"]:
                break
            
            # 构建 INSERT 语句
            placeholders = ", ".join(["?"] * len(columns))
            cols_str = ", ".join(columns)
            insert_sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
            
            for row in data_result["rows"]:
                values = list(row.values())
                cursor.execute(insert_sql, values)
                total_imported += 1
            
            conn.commit()
            print(f"    已导入: {total_imported}/{row_count}")

    # 关闭连接
    conn.close()

    # 4. 验证
    print("\n[4/5] 验证本地数据库...")
    conn = sqlite3.connect(LOCAL_DB)
    cursor = conn.cursor()
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} 行")
    
    conn.close()

    # 5. 完成
    db_size = os.path.getsize(LOCAL_DB)
    print(f"\n[5/5] 完成！")
    print(f"  数据库位置: {LOCAL_DB}")
    print(f"  大小: {db_size / 1024:.1f} KB")

    return True


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n出错: {e}")
        import traceback
        traceback.print_exc()
