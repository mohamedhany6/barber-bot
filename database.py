
import sqlite3
import config

DB_NAME = "barber.db"


# ================= CONNECTION =================
def get_conn():

    conn = sqlite3.connect(DB_NAME, check_same_thread=False)

    return conn


# ================= INIT DB =================
def init_db():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        date TEXT,
        time TEXT,
        service TEXT,
        chat_id INTEGER
    )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_date ON bookings(date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_date_time ON bookings(date, time)")
    cur.execute("""
                 CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_slot
                 ON bookings(date, time)
                """)

    conn.commit()
    conn.close()


# ================= ADD BOOKING =================
def add_booking(name, phone, date, time, service, chat_id):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO bookings(name, phone, date, time, service, chat_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (name, phone, date, time, service, chat_id))

        conn.commit()
        return cur.lastrowid

    except sqlite3.IntegrityError:
        return None

    finally:
        conn.close()


# ================= CHECK SLOT =================
def is_slot_taken(date, time):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT id FROM bookings
    WHERE date=? AND time=?
    """, (date, time))

    result = cur.fetchone()

    conn.close()

    return result is not None


# ================= GET TAKEN TIMES =================
def get_taken_times(date):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT time FROM bookings WHERE date=?
    """, (date,))

    rows = cur.fetchall()

    conn.close()

    return [r[0] for r in rows]


# ================= GET BOOKINGS BY DATE =================
def get_bookings_by_date(date):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, name, phone, date, time, service, chat_id
    FROM bookings
    WHERE date=?
    ORDER BY time
    """, (date,))

    data = cur.fetchall()

    conn.close()

    return data

# ================= GET TODAY INCOME =================
def get_today_income(date):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT service
    FROM bookings
    WHERE date=?
    """, (date,))

    data = cur.fetchall()

    conn.close()

    total = 0
    details = []

    for row in data:

        service = row[0]

        price = config.PRICES.get(service, 0)

        total += price

        details.append({
            "service": service,
            "price": price
        })

    return {
        "total": total,
        "details": details
    }
# ================= DELETE =================
def delete_booking_by_id(booking_id):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM bookings
    WHERE id=?
    """, (booking_id,))

    conn.commit()

    deleted = cur.rowcount > 0

    conn.close()

    return deleted

# ================= DELETE OLD BOOKINGS =================
def delete_old_bookings():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM bookings
    WHERE date < date('now')
    """)

    conn.commit()
    conn.close()