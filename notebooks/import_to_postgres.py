import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:mintee%4012345T@localhost:5432/dropoffdesk')

# Drop tables in reverse dependency order (children first, parents last)
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS offers CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS pipeline_events CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS candidates CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS recruiters CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS roles CASCADE"))
    conn.commit()
    print("✅ Old tables dropped")

# Load in dependency order (parents first, children last)
tables = ['recruiters', 'roles', 'candidates', 'pipeline_events', 'offers']

for table in tables:
    df = pd.read_csv(f'../data/raw/{table}.csv')
    df.to_sql(table, engine, if_exists='replace', index=False)
    print(f"✅ Loaded {len(df):,} rows into {table}")

print("\nAll tables loaded successfully.")