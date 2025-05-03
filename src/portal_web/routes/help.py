from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional
from ..services.auth import get_current_active_user
from ..services.utils import format_response

router = APIRouter()

@router.get("/topics")
async def get_help_topics(
    current_user: str = Depends(get_current_active_user),
    category: Optional[str] = None
):
    """Retorna os tópicos de ajuda disponíveis."""
    try:
        # Aqui você implementaria a lógica para buscar os tópicos de ajuda
        # Por enquanto, retornamos dados de exemplo
        topics = [
            {
                "id": "monitoring",
                "title": "Monitoramento",
                "category": "básico",
                "description": "Como monitorar o sistema",
                "related_topics": ["alerts", "metrics"]
            },
            {
                "id": "diagnostics",
                "title": "Diagnóstico",
                "category": "avançado",
                "description": "Como diagnosticar problemas",
                "related_topics": ["problems", "analysis"]
            },
            {
                "id": "actions",
                "title": "Ações",
                "category": "avançado",
                "description": "Como executar ações de recuperação",
                "related_topics": ["recovery", "rollback"]
            },
            {
                "id": "observability",
                "title": "Observabilidade",
                "category": "avançado",
                "description": "Como visualizar e analisar dados",
                "related_topics": ["visualization", "metrics"]
            }
        ]
        
        if category:
            topics = [t for t in topics if t["category"] == category]
        
        return format_response(topics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topics/{topic_id}")
async def get_topic_details(
    topic_id: str,
    current_user: str = Depends(get_current_active_user)
):
    """Retorna os detalhes de um tópico específico."""
    try:
        # Aqui você implementaria a lógica para buscar os detalhes do tópico
        # Por enquanto, retornamos dados de exemplo
        topic_details = {
            "id": topic_id,
            "title": f"Tópico {topic_id}",
            "content": f"Conteúdo detalhado do tópico {topic_id}",
            "sections": [
                {
                    "title": "Introdução",
                    "content": "Introdução ao tópico"
                },
                {
                    "title": "Como usar",
                    "content": "Instruções de uso"
                },
                {
                    "title": "Exemplos",
                    "content": "Exemplos práticos"
                }
            ],
            "related_topics": ["topic1", "topic2"],
            "last_updated": "2024-03-20T10:00:00Z"
        }
        return format_response(topic_details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_help(
    query: str,
    current_user: str = Depends(get_current_active_user),
    category: Optional[str] = None
):
    """Pesquisa nos tópicos de ajuda."""
    try:
        # Aqui você implementaria a lógica para pesquisar nos tópicos
        # Por enquanto, retornamos dados de exemplo
        results = [
            {
                "id": f"result_{i}",
                "title": f"Resultado {i} para '{query}'",
                "category": "básico",
                "snippet": f"Trecho relevante do resultado {i} contendo '{query}'",
                "relevance": 0.8
            }
            for i in range(5)
        ]
        
        if category:
            results = [r for r in results if r["category"] == category]
        
        return format_response(results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/faq")
async def get_faq(
    current_user: str = Depends(get_current_active_user),
    category: Optional[str] = None
):
    """Retorna as perguntas frequentes."""
    try:
        # Aqui você implementaria a lógica para buscar as FAQs
        # Por enquanto, retornamos dados de exemplo
        faqs = [
            {
                "id": f"faq_{i}",
                "question": f"Pergunta frequente {i}?",
                "answer": f"Resposta para a pergunta frequente {i}",
                "category": "básico",
                "tags": ["tag1", "tag2"]
            }
            for i in range(10)
        ]
        
        if category:
            faqs = [f for f in faqs if f["category"] == category]
        
        return format_response(faqs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tutorials")
async def get_tutorials(
    current_user: str = Depends(get_current_active_user),
    level: Optional[str] = None
):
    """Retorna os tutoriais disponíveis."""
    try:
        # Aqui você implementaria a lógica para buscar os tutoriais
        # Por enquanto, retornamos dados de exemplo
        tutorials = [
            {
                "id": f"tutorial_{i}",
                "title": f"Tutorial {i}",
                "description": f"Descrição do tutorial {i}",
                "level": "iniciante",
                "duration": "30 minutos",
                "steps": [
                    {
                        "number": j,
                        "title": f"Passo {j}",
                        "content": f"Conteúdo do passo {j}"
                    }
                    for j in range(5)
                ]
            }
            for i in range(5)
        ]
        
        if level:
            tutorials = [t for t in tutorials if t["level"] == level]
        
        return format_response(tutorials)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contact")
async def get_contact_info(
    current_user: str = Depends(get_current_active_user)
):
    """Retorna informações de contato para suporte."""
    try:
        # Aqui você implementaria a lógica para buscar as informações de contato
        # Por enquanto, retornamos dados de exemplo
        contact_info = {
            "email": "suporte@example.com",
            "phone": "+55 11 99999-9999",
            "slack": "#suporte",
            "office_hours": "Segunda a Sexta, 9h às 18h",
            "emergency_contact": {
                "phone": "+55 11 99999-8888",
                "email": "emergencia@example.com"
            }
        }
        return format_response(contact_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 