from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import load_config

# Load database configuration
config = load_config()
DATABASE_URL = (
    f"postgresql+psycopg://{config['database']['user']}:{config['database']['password']}@"
    f"{config['database']['host']}:{config['database']['port']}/{config['database']['database']}"
)

# Create a single engine instance
engine = create_engine(DATABASE_URL)

# Configure a sessionmaker for consistent session usage
Session = sessionmaker(bind=engine)

