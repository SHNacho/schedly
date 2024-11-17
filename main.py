import json
from db import Session
from db.crud import get_all_stylists, get_customer

if __name__ == "__main__":
    db_session = Session()
    stylists = get_all_stylists(db_session)
    for stylist in stylists:
        print(json.dumps(stylist.model_dump(), indent=4, default=str))
    customer = get_customer(db_session, customer_id=1)
    print(json.dumps(customer.model_dump(), indent=4, default=str))
    
