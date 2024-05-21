from db import get_db

def get_items_avail(item):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = f"SELECT available FROM {item}" 
    cursor.execute(query)
    rooms = cursor.fetchall()
    result = 0
    for room in rooms:
        result += room['available'] 
    return result

def get_sum_items(item):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = f"SELECT available FROM {item}" 
    cursor.execute(query)
    rooms = cursor.fetchall()
    result = 0
    for i in rooms:
        result += 1
    return result
    