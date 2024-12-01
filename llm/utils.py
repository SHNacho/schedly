from functools import partial
from db import Session
from db.crud import (
    get_stylist, 
    get_all_stylists,
    get_service, 
    get_customer, 
    get_appointment, 
    get_work_schedule
)
import json


def get_stylists_data():
    return get_all_stylists()

if __name__ == "__main__":
    db = Session()
    stylists = get_all_stylists(db)
    #data = json.dumps([dict(stylist) for stylist in stylists], default=str)
    print(str(stylists))


    
