"""
Outils pour l'analyse et la suggestion d'emoji pour les pétitions
Utilise UNIQUEMENT Mistral AI pour des suggestions basées sur le texte
"""

import os
import re

# Configuration Mistral AI
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

# Emoji par défaut si Mistral échoue
DEFAULT_EMOJI = '📢'


def is_valid_emoji(text: str) -> bool:
    """
    Vérifie si le texte est un emoji valide
    """
    emoji_pattern = re.compile(
        r'^([\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF]|\u2640|\u2642|\u2600-\u2B55|\u23cf|\u23e9|\u231a|\ufe0f|\u200d)+$'
    )
    return bool(emoji_pattern.match(text))


def call_mistral_api(prompt: str, model: str = "mistral-tiny", max_tokens: int = 10, temperature: float = 0.2) -> str:
    """
    Appelle l'API Mistral et retourne le contenu de la réponse
    """
    if not MISTRAL_API_KEY:
        raise ValueError("MISTRAL_API_KEY is required")
    
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
    
    client = MistralClient(api_key=MISTRAL_API_KEY)
    
    response = client.chat(
        model=model,
        messages=[ChatMessage(role="user", content=prompt)],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    
    return response.choices[0].message.content.strip()


def suggest_petition_emoji(description: str) -> dict:
    """
    Suggère un emoji pertinent pour une pétition basé UNIQUEMENT sur sa description via Mistral AI.
    
    Args:
        description: La description textuelle de la pétition
        
    Returns:
        dict: {"emoji": "📢"}
    """
    if not description or len(description.strip()) < 10:
        return {"emoji": DEFAULT_EMOJI}
    
    if not MISTRAL_API_KEY:
        return {"emoji": DEFAULT_EMOJI}
    
    try:
        prompt = f'Suggère UN SEUL emoji qui représente au mieux le thème de cette pétition : "{description}". Réponds UNIQUEMENT avec l emoji, sans texte.'
        
        suggested = call_mistral_api(prompt, "mistral-tiny", 10, 0.2)
        
        # Valider que c'est bien un emoji
        if suggested and is_valid_emoji(suggested):
            return {"emoji": suggested}
        
        print(f"Invalid emoji received from Mistral: {suggested}")
        return {"emoji": DEFAULT_EMOJI}
        
    except ImportError:
        print("mistralai library not installed")
        return {"emoji": DEFAULT_EMOJI}
    except Exception as e:
        print(f"Error calling Mistral API: {e}")
        return {"emoji": DEFAULT_EMOJI}


def analyze_petition_text(text: str) -> dict:
    """
    Analyse complétement le texte d'une pétition UNIQUEMENT via Mistral AI.
    
    Args:
        text: Le texte à analyser
        
    Returns:
        dict: Analyse avec catégorie, sentiment, mots-clés et emoji suggéré
    """
    if not text or len(text.strip()) == 0:
        return {
            "category": "autre",
            "sentiment": "neutre",
            "keywords": [],
            "suggested_emoji": DEFAULT_EMOJI
        }
    
    if not MISTRAL_API_KEY:
        return {
            "category": "autre",
            "sentiment": "neutre",
            "keywords": [],
            "suggested_emoji": DEFAULT_EMOJI
        }
    
    try:
        prompt = f'''Analyse ce texte de pétition et retourne une analyse structurée au format JSON avec :
- "category": la catégorie principale (ex: environnement, économie, santé, société)
- "sentiment": le sentiment (positif, négatif, neutre)
- "keywords": une liste de 3 mots-clés principaux
- "suggested_emoji": un emoji représentant le thème

Texte à analyser : "{text}"

Réponds UNIQUEMENT avec le JSON, sans autres textes.'''
        
        content = call_mistral_api(prompt, "mistral-small", 200, 0.3)
        
        # Essayer de parser le JSON
        try:
            import json
            return json.loads(content)
        except Exception:
            # Retourner une analyse par défaut
            return {
                "category": "autre",
                "sentiment": "neutre",
                "keywords": [],
                "suggested_emoji": DEFAULT_EMOJI
            }
            
    except ImportError:
        print("mistralai library not installed")
        return {
            "category": "autre",
            "sentiment": "neutre",
            "keywords": [],
            "suggested_emoji": DEFAULT_EMOJI
        }
    except Exception as e:
        print(f"Error analyzing text: {e}")
        return {
            "category": "autre",
            "sentiment": "neutre",
            "keywords": [],
            "suggested_emoji": DEFAULT_EMOJI
        }
