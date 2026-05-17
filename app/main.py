from db import engine, SessionLocal, Base
from models import Item


def create_tables():
    Base.metadata.create_all(bind=engine)


def insert_sample_item():
    db = SessionLocal()

    try:
        item = Item(
            item_no="A001",
            name="Keyboard",
            quantity=10,
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        print("Inserted item:")
        print(item.id, item.item_no, item.name, item.quantity)

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()


def query_items():
    db = SessionLocal()

    try:
        items = db.query(Item).all()

        print("Current items:")
        for item in items:
            print(item.id, item.item_no, item.name, item.quantity)

    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    insert_sample_item()
    query_items()