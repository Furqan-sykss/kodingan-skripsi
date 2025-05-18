from sqlalchemy import create_engine, text

engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db"
)
# Eksekusi query
with engine.connect() as connection:
    query = text("SELECT DATABASE();")
    result = connection.execute(query)
    for row in result:
        print("Database yang terhubung:", row[0])
