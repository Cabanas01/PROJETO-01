from app import db, Client, Process, ProcessUpdate, Expense, Payment, Document

def init_db():
    db.drop_all()
    db.create_all()

    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
