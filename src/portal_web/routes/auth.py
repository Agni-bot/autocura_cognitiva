from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional
from ..services.auth import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_active_user
)
from ..services.config import settings
from ..services.utils import format_response

router = APIRouter()

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint para autenticação e geração de token."""
    try:
        # Aqui você implementaria a lógica para verificar as credenciais
        # Por enquanto, usamos um usuário de exemplo
        if form_data.username != "admin" or form_data.password != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": form_data.username},
            expires_delta=access_token_expires
        )
        
        return format_response({
            "access_token": access_token,
            "token_type": "bearer"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def read_users_me(current_user: str = Depends(get_current_active_user)):
    """Retorna informações do usuário atual."""
    try:
        # Aqui você implementaria a lógica para buscar informações do usuário
        # Por enquanto, retornamos dados de exemplo
        user_info = {
            "username": current_user,
            "role": "admin",
            "permissions": ["read", "write", "execute"]
        }
        return format_response(user_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: str = Depends(get_current_active_user)
):
    """Altera a senha do usuário atual."""
    try:
        # Aqui você implementaria a lógica para alterar a senha
        # Por enquanto, apenas simulamos a operação
        if current_password != "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )
        
        hashed_password = get_password_hash(new_password)
        # Aqui você salvaria a nova senha no banco de dados
        
        return format_response({
            "message": "Senha alterada com sucesso"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 