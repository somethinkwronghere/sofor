import sqlite3

# Connect to the database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("=" * 60)
print("DATABASE TABLES")
print("=" * 60)
for table in tables:
    table_name = table[0]
    print(f"\n{table_name}")
    
    # Get column info for each table
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    for col in columns:
        col_id, col_name, col_type, not_null, default_val, pk = col
        pk_marker = " [PK]" if pk else ""
        not_null_marker = " NOT NULL" if not_null else ""
        print(f"  - {col_name}: {col_type}{pk_marker}{not_null_marker}")

# Count records in key tables
print("\n" + "=" * 60)
print("RECORD COUNTS")
print("=" * 60)

key_tables = ['sofor', 'arac', 'yurt', 'gorev', 'mesai', 'izin', 'gorevlendirmeler', 'malzeme', 'log']
for table_name in key_tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"{table_name}: {count} records")
    except sqlite3.OperationalError:
        print(f"{table_name}: Table does not exist")

conn.close()
print("\n" + "=" * 60)
print("Database verification complete!")
print("=" * 60)
