from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models, schemas, database

# Non-existent yet,
#   models and database dependent on issue: 'Create a skeleton database module 4'.

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()


def get_session():
    """
    Dependency to provide a database session.

    returns:
    *   Session, a SQLAlchemy session that is automatically closed afterwards.
    """

    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ENDPOINTS BELOW (TBI)
@app.post("/users/", response_model=schemas.UserRead)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_session),
) -> schemas.UserRead:
    """
    Register a new user in the database.

    This endpoint expects a JSON body matching UserCreate (name, email, password),
    (see schemas.py) then should hash the password, create a User row, and
    return UserRead.

    * Args:
        user_in (schemas.UserCreate): Data required to create a new user.
        db (Session): SQLAlchemy session to interact with the database.

    * Returns:
        schemas.UserRead: The newly created user (id, name, email, is_active).
    """
    # Placeholder: actual logic to check email, hash password, insert, etc
    raise HTTPException(status_code=501, detail="endpoint not implemented yet")
