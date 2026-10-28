import os
import requests

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    github_token = os.environ.get("GITHUB_TOKEN")
    comments_url = os.environ.get("PR_COMMENTS_URL")
    
    if not api_key or not comments_url:
        print("Faltan variables de entorno necesarias.")
        return

    # Leer el diff generado
    if not os.path.exists("diff.txt") or os.path.getsize("diff.txt") == 0:
        print("El diff está vacío o no hay cambios para revisar.")
        return

    with open("diff.txt", "r", encoding="utf-8") as f:
        diff_content = f.read()

    # Prompt amigable y adaptado a estudiantes de videojuegos / Godot
    prompt = (
        "Eres un asistente de revisión de código educativo para estudiantes de desarrollo de videojuegos que usan Godot (GDScript)."
        "Revisa el siguiente 'git diff' de un Pull Request. Da feedback breve, constructivo, señala posibles errores lógicos simples "
        "En caso de no tener comentarios que hacer por estar correcto en lines generales, dejar un comentario al estilo 'PR Revisado y sin errores'"
        f"Diff:\n{diff_content}"
    )

    # Llamada a la API de Gemini (usando el modelo rápido y gratuito gemini-3.6-flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Error al llamar a la API de Gemini: {response.text}")
        return

    result = response.json()
    try:
        review_text = result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        print(f"Error al parsear la respuesta de Gemini: {e}")
        review_text = "No se pudo generar la revisión automática en este momento."

    # Publicar el comentario automáticamente en el PR de GitHub
    comment_payload = {
        "body": f"🤖 **Revisión automática de IA (Gemini):**\n\n{review_text}"
    }
    gh_headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }
    
    com_response = requests.post(comments_url, headers=gh_headers, json=comment_payload)
    if com_response.status_code == 201:
        print("Comentario de IA publicado exitosamente en el PR.")
    else:
        print(f"Error al publicar comentario en GitHub: {com_response.text}")

if __name__ == "__main__":
    main()