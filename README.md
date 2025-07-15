# Schedly

## Project Structure
```
schedly/
├── config/
│   ├── config.yaml           # Configuration file for database connection and LLM API keys
│   └── __init__.py
├── db/
│   ├── create_db.py          # Script to create the test database and tables
│   ├── models.py             # SQLAlchemy ORM models
│   ├── crud.py               # Functions to interact with the database using SQLAlchemy
│   ├── schemas.py            # Pydantic schemas
│   ├── enum.py               # Enums for pydantic schemas
│   └── __init__.py
├── llm/
│   ├── agents/
│   │    ├── supervisor.py     # Supervisor agent
│   │    ├── info.py           # Informative sub-agent
│   │    ├── schedule.py       # Scheduler sub-agent
│   │    └── availability.py   # Availability sub-agent
│   ├── state.py
│   ├── tools.py
│   ├── utils.py
│   └── __init__.py
├── main.py                   # Entry point to run the agent and interact with the database
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```
