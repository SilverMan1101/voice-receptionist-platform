import sys
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared_kernel.core.database import get_db, engine
from shared_kernel.domain.models import User, Base
from shared_kernel.domain.schemas import Token
from libs.auth.jwt_validator import verify_password, create_access_token

# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

@app.post("/api/v1/auth/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "org_id": str(user.organization_id), "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "auth_service"}
