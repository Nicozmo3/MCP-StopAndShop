import os
import sys
from datetime import datetime, timedelta, timezone

import mysql.connector
from dotenv import load_dotenv

from mcp_adapter_http import MCPHttpAdapter
from mcp_adapter_stdio import MCPStdioAdapter
from mcp_server import MCPServer

load_dotenv()

from petition_tools import analyze_petition_text, suggest_petition_emoji

DEFAULT_LISTENING_PORT: int = 8081
DEFAULT_LISTENING_INTF: str = "0.0.0.0"
DEFAULT_TRANSPORT: str = "http"

mcp = MCPServer("stopandshop-moderation", "A moderation server for Stop and Shop")


def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "stopandshop"),
        port=int(os.getenv("DB_PORT", "3306")),
    )


@mcp.tool(
    name="get_comments_since",
    description="Retrieve comments posted after a given date with brand and belief context",
    input_schema={
        "type": "object",
        "properties": {"limit": {"type": "integer", "default": 50}},
        "required": [],
    },
)
def get_comments_since(limit: int = 50):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            c.comment_id,
            c.text,
            c.note,
            b.name AS brand_name,
            bl.title AS belief_title,
            bl.description AS belief_description

        FROM comment c
        JOIN brand b ON c.concerned_brand_id = b.brand_id
        JOIN belief bl ON c.concerned_belief_id = bl.belief_id

        WHERE c.is_moderation_pertinent IS NULL

        ORDER BY c.created_at ASC
        LIMIT %s
    """

    cursor.execute(query, (limit,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return {"comments": results}


@mcp.tool(
    name="mark_comments_not_pertinent",
    description="Mark multiple comments as not pertinent after LLM classification",
    input_schema={
        "type": "object",
        "properties": {
            "comment_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "List of comment IDs to mark as not pertinent",
            }
        },
        "required": ["comment_ids"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "updated_count": {"type": "integer"},
            "updated_ids": {"type": "array", "items": {"type": "integer"}},
        },
    },
)
def mark_comments_not_pertinent(comment_ids: list[int], reason: str = None):
    conn = get_conn()
    cursor = conn.cursor()

    placeholders = ",".join(["%s"] * len(comment_ids))

    query = f"""
        UPDATE comment
        SET is_moderation_pertinent = FALSE
        WHERE comment_id IN ({placeholders})
    """

    cursor.execute(query, comment_ids)
    conn.commit()

    updated_count = cursor.rowcount

    cursor.close()
    conn.close()

    if updated_count > 0:
        reason_str = f" - Raison: {reason}" if reason else ""
        print(f"[COMMENT_MODERATION] {updated_count} commentaires marques comme NON PERTINENTS en base: {comment_ids}{reason_str}")
    
    return {"updated_count": updated_count, "updated_ids": comment_ids}


@mcp.tool(
    name="check_comment_pertinence",
    description="Check if a single comment is pertinent using LLM analysis",
    input_schema={
        "type": "object",
        "properties": {
            "comment_id": {"type": "integer", "description": "The comment ID to check"},
            "text": {"type": "string", "description": "The comment text"},
            "brand_name": {"type": "string", "description": "The brand name"},
            "belief_title": {"type": "string", "description": "The belief title"},
        },
        "required": ["comment_id", "text", "brand_name", "belief_title"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "comment_id": {"type": "integer"},
            "is_pertinent": {"type": "boolean"},
            "reason": {"type": "string"},
        },
    },
)
def check_comment_pertinence(
    comment_id: int, text: str, brand_name: str, belief_title: str
) -> dict:
    """
    Check if a comment is pertinent based on its content and context using Mistral AI.
    """
    import os
    import json
    
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    
    text_preview = text[:50] + "..." if len(text) > 50 else text
    
    # Fallback à l'ancien algorithme si pas d'API key
    if not MISTRAL_API_KEY:
        print(f"[COMMENT_MODERATION] MISTRAL_API_KEY non configurée, utilisation de l'algorithme de fallback pour le commentaire {comment_id}")
        return check_comment_pertinence_fallback(comment_id, text, brand_name, belief_title)
    
    try:
        from mistralai.client import MistralClient
        from mistralai.models.chat_completion import ChatMessage
    except ImportError as e:
        print(f"[COMMENT_MODERATION] Erreur d'import Mistral AI: {e}, utilisation de l'algorithme de fallback pour le commentaire {comment_id}")
        return check_comment_pertinence_fallback(comment_id, text, brand_name, belief_title)
    
    try:
        print(f"\n[COMMENT_MODERATION] === DEBUT ANALYSE IA COMMENTAIRE {comment_id} ===")
        print(f"[COMMENT_MODERATION] Texte: '{text_preview}'")
        print(f"[COMMENT_MODERATION] Marque: {brand_name}")
        print(f"[COMMENT_MODERATION] Croyance: {belief_title}")
        
        prompt = f'''Analyse ce commentaire dans le contexte de la marque "{brand_name}" et de la croyance "{belief_title}".
Détermine si le commentaire est pertinent pour cette discussion.

Critères de pertinence :
- Le commentaire doit être lié à la marque ou à la croyance mentionnée
- Le commentaire doit être constructif et utile pour la discussion
- Exclure les commentaires hors-sujet, spam, ou non pertinents

Réponds UNIQUEMENT avec un JSON contenant :
{{
    "is_pertinent": true/false,
    "reason": "explication claire de la décision"
}}

Commentaire à analyser : "{text}"'''
        
        print(f"[COMMENT_MODERATION] Prompt envoyé à Mistral...")
        
        client = MistralClient(api_key=MISTRAL_API_KEY)
        response = client.chat(
            model="mistral-small",
            messages=[ChatMessage(role="user", content=prompt)],
            max_tokens=200,
            temperature=0.2,
        )
        
        content = response.choices[0].message.content.strip()
        print(f"[COMMENT_MODERATION] Mistral a retourné: {content}")
        
        # Nettoyer la réponse pour extraire le JSON (enlever les backticks et blocs markdown)
        import re
        # Supprimer les blocs ```json ... ``` ou ``` ... ```
        content = re.sub(r'^```(?:json)?\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        content = content.strip()
        
        # Essayer de parser le JSON
        try:
            result = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"[COMMENT_MODERATION] Erreur de parsing JSON: {e}, contenu brut: '{content}'")
            print(f"[COMMENT_MODERATION] Utilisation de l'algorithme de fallback pour le commentaire {comment_id}")
            return check_comment_pertinence_fallback(comment_id, text, brand_name, belief_title)
        
        result["comment_id"] = comment_id
        
        if result.get("is_pertinent"):
            print(f"[COMMENT_MODERATION] Comment {comment_id} CONSERVE - Raison: {result.get('reason', 'pas de raison fournie')} (texte: '{text_preview}')")
        else:
            print(f"[COMMENT_MODERATION] Comment {comment_id} MASQUE - Raison: {result.get('reason', 'pas de raison fournie')} (texte: '{text_preview}')")
        
        print(f"[COMMENT_MODERATION] === FIN ANALYSE IA COMMENTAIRE {comment_id} ===\n")
        return result
        
    except Exception as e:
        print(f"[COMMENT_MODERATION] Erreur avec Mistral AI: {type(e).__name__}: {e}, utilisation de l'algorithme de fallback pour le commentaire {comment_id}")
        return check_comment_pertinence_fallback(comment_id, text, brand_name, belief_title)


def check_comment_pertinence_fallback(
    comment_id: int, text: str, brand_name: str, belief_title: str
) -> dict:
    """
    Ancienne méthode de vérification par algorithme simple (fallback si IA indisponible).
    """
    text_lower = text.lower()
    text_preview = text[:50] + "..." if len(text) > 50 else text

    if len(text.strip()) < 10:
        result = {
            "comment_id": comment_id,
            "is_pertinent": False,
            "reason": "Comment is too short to be meaningful",
        }
        print(f"[COMMENT_MODERATION] Comment {comment_id} MASQUE - Raison: {result['reason']} (texte: '{text_preview}')")
        return result

    off_topic_keywords = ["test", "spam", "fake", "scam", "http", "https", "www"]
    if any(keyword in text_lower for keyword in off_topic_keywords):
        result = {
            "comment_id": comment_id,
            "is_pertinent": False,
            "reason": "Comment contains off-topic content",
        }
        print(f"[COMMENT_MODERATION] Comment {comment_id} MASQUE - Raison: {result['reason']} (texte: '{text_preview}')")
        return result

    import re
    
    def get_word_variations(word):
        cleaned = re.sub(r"[\W_]", "", word)
        variations = [cleaned]
        prefixes = ["l", "d", "de", "la", "le", "les", "du", "des"]
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                suffix = cleaned[len(prefix):]
                if suffix and len(suffix) >= 2:
                    variations.append(suffix)
        return variations
    
    all_context_words = brand_name.lower().split() + belief_title.lower().split()
    context_found = False
    for word in all_context_words:
        variations = get_word_variations(word)
        if any(v in text_lower for v in variations):
            context_found = True
            break
    
    if not context_found:
        result = {
            "comment_id": comment_id,
            "is_pertinent": False,
            "reason": "Comment does not mention the brand or belief",
        }
        print(f"[COMMENT_MODERATION] Comment {comment_id} MASQUE - Raison: {result['reason']} (texte: '{text_preview}')")
        return result

    result = {
        "comment_id": comment_id,
        "is_pertinent": True,
        "reason": "Comment appears to be on-topic and relevant",
    }
    print(f"[COMMENT_MODERATION] Comment {comment_id} CONSERVE - Raison: {result['reason']} (texte: '{text_preview}')")
    return result


@mcp.tool(
    name="suggest_petition_emoji",
    description="Suggère un emoji pertinent pour une pétition basé sur sa description en utilisant Mistral AI",
    input_schema={
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "La description textuelle de la pétition",
            }
        },
        "required": ["description"],
    },
    output_schema={
        "type": "object",
        "properties": {"emoji": {"type": "string", "description": "L'emoji suggéré"}},
    },
)
def mcp_suggest_petition_emoji(description: str) -> dict:
    return suggest_petition_emoji(description)


@mcp.tool(
    name="get_petitions_to_moderate",
    description="Retrieve petitions that have not yet been moderated, with their title, description, emoji, initiator info, and signature count. The LLM should evaluate whether each petition is relevant to ethical/engaged consumption and flag any malicious or off-topic content.",
    input_schema={
        "type": "object",
        "properties": {"limit": {"type": "integer", "default": 50}},
        "required": [],
    },
)
def get_petitions_to_moderate(limit: int = 50):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            p.petition_id,
            p.title,
            p.description,
            p.emoji,
            p.start_date,
            p.signatures,
            p.initiator_anonymous,
            a.username AS initiator_username

        FROM petition p
        JOIN account a ON p.initiator_id = a.account_id

        WHERE p.is_moderation_pertinent IS NULL

        ORDER BY p.start_date ASC
        LIMIT %s
    """

    cursor.execute(query, (limit,))
    results = cursor.fetchall()

    # Convert datetime objects to string for JSON serialization
    for r in results:
        if r.get("start_date"):
            r["start_date"] = r["start_date"].isoformat()

    cursor.close()
    conn.close()

    return {"petitions": results}


@mcp.tool(
    name="mark_petitions_not_pertinent",
    description="Mark multiple petitions as not pertinent (malicious, off-topic, or unrelated to ethical/engaged consumption) after LLM classification",
    input_schema={
        "type": "object",
        "properties": {
            "petition_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "List of petition IDs to mark as not pertinent",
            }
        },
        "required": ["petition_ids"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "updated_count": {"type": "integer"},
            "updated_ids": {"type": "array", "items": {"type": "integer"}},
        },
    },
)
def mark_petitions_not_pertinent(petition_ids: list[int]):
    if not petition_ids:
        return {"updated_count": 0, "updated_ids": []}

    conn = get_conn()
    cursor = conn.cursor()

    placeholders = ",".join(["%s"] * len(petition_ids))

    query = f"""
        UPDATE petition
        SET is_moderation_pertinent = FALSE
        WHERE petition_id IN ({placeholders})
    """

    cursor.execute(query, petition_ids)
    conn.commit()

    updated_count = cursor.rowcount

    cursor.close()
    conn.close()

    return {"updated_count": updated_count, "updated_ids": petition_ids}


@mcp.tool(
    name="analyze_petition_text",
    description="Analyse complète du texte d'une pétition avec catégorie, sentiment, mots-clés et emoji suggéré",
    input_schema={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Le texte à analyser"}
        },
        "required": ["text"],
    },
)
def mcp_analyze_petition_text(text: str) -> dict:
    return analyze_petition_text(text)


def main(argv: list[str]) -> int:
    # Lire le transport depuis les arguments ou le .env
    transport = argv[1] if len(argv) > 1 else os.getenv("TRANSPORT", DEFAULT_TRANSPORT)

    if transport == "stdio":
        adapter = MCPStdioAdapter(mcp)
    else:
        listening_intf = (
            argv[2] if len(argv) > 2 else os.getenv("HOST", DEFAULT_LISTENING_INTF)
        )
        listening_port = (
            int(argv[3])
            if len(argv) > 3
            else int(os.getenv("PORT", DEFAULT_LISTENING_PORT))
        )
        adapter = MCPHttpAdapter(mcp, listening_intf, listening_port)

    adapter.serve()
    return 0


if __name__ == "__main__":
    exit(main(sys.argv))
