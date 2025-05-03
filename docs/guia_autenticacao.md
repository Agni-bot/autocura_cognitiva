# Guia de Autenticação

## Visão Geral

Este guia descreve os processos e configurações de autenticação do Sistema de Autocura Cognitiva.

## Autenticação

### 1. JWT (JSON Web Tokens)

#### Geração de Token
```python
from datetime import datetime, timedelta
import jwt

def generate_token(user_id: str) -> str:
    """
    Gera um token JWT para o usuário.
    
    Args:
        user_id: ID do usuário
        
    Returns:
        str: Token JWT
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm='HS256'
    )
```

#### Validação de Token
```python
def validate_token(token: str) -> dict:
    """
    Valida um token JWT.
    
    Args:
        token: Token JWT
        
    Returns:
        dict: Payload do token
        
    Raises:
        jwt.ExpiredSignatureError: Token expirado
        jwt.InvalidTokenError: Token inválido
    """
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=['HS256']
        )
    except jwt.ExpiredSignatureError:
        raise Exception("Token expirado")
    except jwt.InvalidTokenError:
        raise Exception("Token inválido")
```

### 2. OAuth 2.0

#### Configuração
```python
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'email profile'}
)
```

#### Fluxo de Autenticação
```python
@app.route('/login')
async def login():
    redirect_uri = url_for('auth', _external=True)
    return await oauth.google.authorize_redirect(redirect_uri)

@app.route('/auth')
async def auth():
    token = await oauth.google.authorize_access_token()
    user = await oauth.google.parse_id_token(token)
    return jsonify(user)
```

## Autorização

### 1. RBAC (Role-Based Access Control)

#### Definição de Roles
```python
class Role(Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    USER = "user"

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
```

#### Mapeamento de Permissões
```python
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.READ,
        Permission.WRITE,
        Permission.EXECUTE
    ],
    Role.OPERATOR: [
        Permission.READ,
        Permission.EXECUTE
    ],
    Role.USER: [
        Permission.READ
    ]
}
```

### 2. ACL (Access Control Lists)

#### Definição de Regras
```python
class ACL:
    def __init__(self):
        self.rules = []
    
    def add_rule(self, subject, resource, action, effect):
        self.rules.append({
            'subject': subject,
            'resource': resource,
            'action': action,
            'effect': effect
        })
    
    def check_permission(self, subject, resource, action):
        for rule in self.rules:
            if (rule['subject'] == subject and
                rule['resource'] == resource and
                rule['action'] == action):
                return rule['effect'] == 'allow'
        return False
```

## MFA (Multi-Factor Authentication)

### 1. Configuração

#### TOTP (Time-Based One-Time Password)
```python
import pyotp

def generate_totp_secret() -> str:
    """
    Gera um segredo para TOTP.
    
    Returns:
        str: Segredo TOTP
    """
    return pyotp.random_base32()

def verify_totp(secret: str, token: str) -> bool:
    """
    Verifica um token TOTP.
    
    Args:
        secret: Segredo TOTP
        token: Token a verificar
        
    Returns:
        bool: True se válido, False caso contrário
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(token)
```

### 2. Implementação

#### Registro MFA
```python
@app.route('/mfa/setup', methods=['POST'])
@require_auth
async def setup_mfa(user):
    secret = generate_totp_secret()
    
    # Salvar segredo
    await db.users.update_one(
        {'_id': user['_id']},
        {'$set': {'mfa_secret': secret}}
    )
    
    # Gerar QR Code
    provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        user['email'],
        issuer_name='Autocura'
    )
    
    return jsonify({
        'secret': secret,
        'qr_code': generate_qr_code(provisioning_uri)
    })
```

#### Verificação MFA
```python
@app.route('/mfa/verify', methods=['POST'])
@require_auth
async def verify_mfa(user):
    token = request.json.get('token')
    
    if not verify_totp(user['mfa_secret'], token):
        raise Exception("Token inválido")
    
    # Gerar token de sessão
    session_token = generate_session_token(user)
    
    return jsonify({'token': session_token})
```

## Segurança

### 1. Senhas

#### Requisitos
```python
def validate_password(password: str) -> bool:
    """
    Valida uma senha.
    
    Args:
        password: Senha a validar
        
    Returns:
        bool: True se válida, False caso contrário
    """
    # Mínimo 12 caracteres
    if len(password) < 12:
        return False
    
    # Pelo menos 1 letra maiúscula
    if not re.search(r'[A-Z]', password):
        return False
    
    # Pelo menos 1 letra minúscula
    if not re.search(r'[a-z]', password):
        return False
    
    # Pelo menos 1 número
    if not re.search(r'\d', password):
        return False
    
    # Pelo menos 1 caractere especial
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True
```

#### Hash
```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """
    Gera hash de uma senha.
    
    Args:
        password: Senha em texto plano
        
    Returns:
        str: Hash da senha
    """
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """
    Verifica uma senha.
    
    Args:
        plain: Senha em texto plano
        hashed: Hash da senha
        
    Returns:
        bool: True se válida, False caso contrário
    """
    return pwd_context.verify(plain, hashed)
```

### 2. Rate Limiting

#### Implementação
```python
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.route("/login")
@limiter.limit("5/minute")
async def login(request: Request):
    # código de login
    pass
```

## Auditoria

### 1. Logs de Autenticação

#### Estrutura
```json
{
    "timestamp": "2024-05-02T12:00:00Z",
    "event": "login",
    "user_id": "user123",
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0",
    "status": "success",
    "metadata": {
        "mfa_used": true,
        "provider": "google"
    }
}
```

### 2. Monitoramento

#### Métricas
```python
from prometheus_client import Counter

login_attempts = Counter(
    'auth_login_attempts_total',
    'Total de tentativas de login',
    ['status']
)

mfa_attempts = Counter(
    'auth_mfa_attempts_total',
    'Total de tentativas MFA',
    ['status']
)
```

## Recuperação de Conta

### 1. Reset de Senha

#### Fluxo
```python
@app.route('/password/reset/request', methods=['POST'])
async def request_password_reset():
    email = request.json.get('email')
    
    # Gerar token
    token = generate_reset_token(email)
    
    # Enviar email
    await send_reset_email(email, token)
    
    return jsonify({'message': 'Email enviado'})

@app.route('/password/reset/confirm', methods=['POST'])
async def confirm_password_reset():
    token = request.json.get('token')
    new_password = request.json.get('password')
    
    # Validar token
    email = validate_reset_token(token)
    
    # Atualizar senha
    await update_password(email, new_password)
    
    return jsonify({'message': 'Senha atualizada'})
```

### 2. Desbloqueio de Conta

#### Implementação
```python
@app.route('/account/unlock', methods=['POST'])
@require_admin
async def unlock_account():
    user_id = request.json.get('user_id')
    
    # Desbloquear conta
    await db.users.update_one(
        {'_id': user_id},
        {
            '$set': {
                'locked': False,
                'failed_attempts': 0
            }
        }
    )
    
    return jsonify({'message': 'Conta desbloqueada'})
``` 