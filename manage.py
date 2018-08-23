from app import manager,db
@manager.command
def create_db():
    """Creates database from sqlalchemy schema."""
    db.create_all()
if __name__ == "__main__":
    manager.run()



