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
files = {
    'recruiters':      '../data/clean/recruiters_clean.csv',
    'roles':           '../data/clean/roles_clean.csv',
    'candidates':      '../data/clean/candidates_clean.csv',
    'pipeline_events': '../data/clean/pipeline_events_clean.csv',
    'offers':          '../data/clean/offers_clean.csv',
}

for table, filepath in files.items():
    df = pd.read_csv(filepath)
    df.to_sql(table, engine, if_exists='replace', index=False)
    print(f"✅ Loaded {len(df):,} rows into {table}")

print("\nAll tables loaded successfully.")