# Schedly

## Project Structure
```
my_project/
├── config/
│   ├── config.yaml           # Configuration file for database connection and LLM API keys
│   └── __init__.py
├── db/
│   ├── create_db.py          # Script to create the test database and tables
│   ├── models.py             # SQLAlchemy ORM models
│   ├── crud.py               # Functions to interact with the database using SQLAlchemy
│   └── __init__.py
├── llm/
│   ├── agent.py              # LangChain agent configuration and setup
│   └── __init__.py
├── main.py                   # Entry point to run the agent and interact with the database
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```
