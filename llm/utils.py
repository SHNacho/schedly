from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI

from db import Session
from db.crud import (
    get_all_stylists,
)


def get_stylists_data():
    return get_all_stylists()

if __name__ == "__main__":
    llm = OpenAI()
    prompt = PromptTemplate.from_template()
    db = Session()
    stylists = get_all_stylists(db)
    for s in stylists:
        print(str(s))


    
