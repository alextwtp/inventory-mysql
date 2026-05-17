from config.database import SessionLocal
from repository.mysql_models import Inventory


def main():
    db = SessionLocal()

    try:
        # INSERT
        item = Inventory(
            pid="P003",
            item_name="Test Item",
            qty=10,
            location="A1",
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        print("Inserted item id:", item.id)

        # SELECT
        found = db.query(Inventory).filter(Inventory.pid == "P003").first()

        if found:
            print("Found:")
            print("pid:", found.pid)
            print("item_name:", found.item_name)
            print("qty:", found.qty)
            print("location:", found.location)
        else:
            print("Item not found")

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    main()