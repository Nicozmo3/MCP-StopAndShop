"""
Outils pour l'analyse et la suggestion d'emoji pour les pétitions
Utilise UNIQUEMENT Mistral AI pour des suggestions basées sur le texte
Avec logs de débogage détaillés
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
    print(f"[MISTRAL] === DEBUT APPEL MISTRAL ===")
    print(f"[MISTRAL] Model: {model}")
    print(f"[MISTRAL] Max tokens: {max_tokens}")
    print(f"[MISTRAL] Temperature: {temperature}")
    print(f"[MISTRAL] Prompt: {prompt[:100]}...")
    
    if not MISTRAL_API_KEY:
        print("[MISTRAL] ERROR: MISTRAL_API_KEY is not set!")
        raise ValueError("MISTRAL_API_KEY is required")
    
    print("[MISTRAL] Initialisation du client Mistral...")
    
    try:
        from mistralai.client import MistralClient
        from mistralai.models.chat_completion import ChatMessage
        
        client = MistralClient(api_key=MISTRAL_API_KEY)
        print("[MISTRAL] Client Mistral initialisé")
        
        print("[MISTRAL] Appel à l'API...")
        response = client.chat(
            model=model,
            messages=[ChatMessage(role="user", content=prompt)],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        print("[MISTRAL] Réponse reçue")
        content = response.choices[0].message.content.strip()
        print(f"[MISTRAL] Content: {content}")
        print(f"[MISTRAL] === FIN APPEL MISTRAL (SUCCESS) ===")
        
        return content
        
    except Exception as e:
        print(f"[MISTRAL] ERROR: {type(e).__name__}: {e}")
        print(f"[MISTRAL] === FIN APPEL MISTRAL (ERROR) ===")
        raise


def suggest_petition_emoji(description: str) -> dict:
    """
    Suggère un emoji pertinent pour une pétition basé UNIQUEMENT sur sa description via Mistral AI.
    
    Args:
        description: La description textuelle de la pétition
        
    Returns:
        dict: {"emoji": "🌱"}
    """
    print(f"\n[TOOL] === DEBUT suggest_petition_emoji ===")
    print(f"[TOOL] Description: {description[:100]}...")
    
    if not description or len(description.strip()) < 10:
        print("[TOOL] Description trop courte (< 10 chars), fallback à 📢")
        print(f"[TOOL] === FIN suggest_petition_emoji (TOO SHORT) ===\n")
        return {"emoji": DEFAULT_EMOJI}
    
    if not MISTRAL_API_KEY:
        print("[TOOL] MISTRAL_API_KEY non configurée, fallback à 📢")
        print(f"[TOOL] === FIN suggest_petition_emoji (NO API KEY) ===\n")
        return {"emoji": DEFAULT_EMOJI}
    
    try:
        prompt = f'Suggère UN SEUL emoji qui représente au mieux le thème de cette pétition : "{description}". Réponds UNIQUEMENT avec l emoji, sans texte.'
        print(f"[TOOL] Prompt envoyé à Mistral: {prompt[:100]}...")
        
        suggested = call_mistral_api(prompt, "mistral-tiny", 10, 0.2)
        print(f"[TOOL] Mistral a retourné: '{suggested}'")
        
        # Valider que c'est bien un emoji
        if suggested and is_valid_emoji(suggested):
            print(f"[TOOL] Emoji valide: {suggested}")
            print(f"[TOOL] === FIN suggest_petition_emoji (SUCCESS) ===\n")
            return {"emoji": suggested}
        
        print(f"[TOOL] Emoji INVALIDE: '{suggested}'")
        print(f"[TOOL] === FIN suggest_petition_emoji (INVALID EMOJI) ===\n")
        return {"emoji": DEFAULT_EMOJI}
        
    except ImportError as e:
        print(f"[TOOL] ImportError: {e}")
        print(f"[TOOL] === FIN suggest_petition_emoji (IMPORT ERROR) ===\n")
        return {"emoji": DEFAULT_EMOJI}
    except Exception as e:
        print(f"[TOOL] Exception: {type(e).__name__}: {e}")
        print(f"[TOOL] === FIN suggest_petition_emoji (EXCEPTION) ===\n")
        return {"emoji": DEFAULT_EMOJI}


def analyze_petition_text(text: str) -> dict:
    """
    Analyse complétement le texte d'une pétition UNIQUEMENT via Mistral AI.
    
    Args:
        text: Le texte à analyser
        
    Returns:
        dict: Analyse avec catégorie, sentiment, mots-clés et emoji suggéré
    """
    print(f"\n[TOOL] === DEBUT analyze_petition_text ===")
    print(f"[TOOL] Text: {text[:100]}...")
    
    if not text or len(text.strip()) == 0:
        print("[TOOL] Texte vide, fallback")
        print(f"[TOOL] === FIN analyze_petition_text (EMPTY) ===\n")
        return {
            "category": "autre",
            "sentiment": "neutre",
            "keywords": [],
            "suggested_emoji": DEFAULT_EMOJI
        }
    
    if not MISTRAL_API_KEY:
        print("[TOOL] MISTRAL_API_KEY non configurée, fallback")
        print(f"[TOOL] === FIN analyze_petition_text (NO API KEY) ===\n")
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
        
        print(f"[TOOL] Prompt envoyé à Mistral (analyze): {prompt[:100]}...")
        
        content = call_mistral_api(prompt, "mistral-small", 200, 0.3)
        print(f"[TOOL] Mistral a retourné (analyze): {content[:100]}...")
        
        # Essayer de parser le JSON
        try:
            import json
            result = json.loads(content)
            print(f"[TOOL] JSON parsé avec succès")
            print(f"[TOOL] === FIN analyze_petition_text (SUCCESS) ===\n")
            return result
        except Exception as e:
            print(f"[TOOL] Erreur de parsing JSON: {e}")
            print(f"[TOOL] Content brut: {content}")
            print(f"[TOOL] === FIN analyze_petition_text (PARSE ERROR) ===\n")
            return {
                "category": "autre",
                "sentiment": "neutre",
                "keywords": [],
                "suggested_emoji": DEFAULT_EMOJI
            }
            
    except ImportError as e:
        print(f"[TOOL] ImportError: {e}")
        print(f"[TOOL] === FIN analyze_petition_text (IMPORT ERROR) ===\n")
        return {
            "category": "autre",
            "sentiment": "neutre",
            "keywords": [],
            "suggested_emoji": DEFAULT_EMOJI
        }
    except Exception as e:
        print(f"[TOOL] Exception: {type(e).__name__}: {e}")
        print(f"[TOOL] === FIN analyze_petition_text (EXCEPTION) ===\n")
        return {
            "category": "autre",
            "sentiment": "neutre",
            "keywords": [],
            "suggested_emoji": DEFAULT_EMOJI
        }
