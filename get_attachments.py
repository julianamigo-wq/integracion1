import os
import sys
from jira import JIRA
from jira.exceptions import JIRAError

# --- 1. Definición de Variables de Entorno Requeridas ---
# Estas variables deben ser inyectadas por GitHub Actions como Secrets o variables.
JIRA_SERVER = os.environ.get("JIRA_SERVER_URL")
JIRA_USER = os.environ.get("JIRA_USER_EMAIL")
JIRA_TOKEN = os.environ.get("JIRA_API_TOKEN")
JIRA_ISSUE_KEY = os.environ.get("JIRA_ISSUE_KEY") # Ej: PROJ-123

if not all([JIRA_SERVER, JIRA_USER, JIRA_TOKEN, JIRA_ISSUE_KEY]):
    print("Error: Una o más variables de entorno de Jira no están configuradas.")
    print("Asegúrate de configurar JIRA_SERVER_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN y JIRA_ISSUE_KEY.")
    sys.exit(1)

def get_attachment_names():
    """Conecta con Jira y obtiene los nombres de los archivos adjuntos de una tarjeta."""
    print(f"-> Conectando con el servidor Jira: {JIRA_SERVER}")
    
    try:
        # Autenticación usando Basic Auth con correo electrónico y token API
        jira = JIRA(
            server=JIRA_SERVER,
            basic_auth=(JIRA_USER, JIRA_TOKEN)
        )
        
        # 2. Obtener la tarjeta (Issue)
        print(f"-> Buscando la tarjeta: {JIRA_ISSUE_KEY}")
        issue = jira.issue(JIRA_ISSUE_KEY)
        
        # 3. Extraer los nombres de los adjuntos
        attachments = issue.fields.attachment
        
        if not attachments:
            print(f"La tarjeta '{JIRA_ISSUE_KEY}' no tiene archivos adjuntos.")
            return []

        attachment_names = [att.filename for att in attachments]
        
        print("\n--- NOMBRES DE ARCHIVOS ADJUNTOS ENCONTRADOS ---")
        for name in attachment_names:
            print(f"- {name}")
            
        return attachment_names

    except JIRAError as e:
        print(f"\nError de Jira (código {e.status_code}): {e.text}")
        if e.status_code == 401:
            print("Verifica el JIRA_USER_EMAIL y JIRA_API_TOKEN.")
        if e.status_code == 404:
            print(f"Verifica que la tarjeta '{JIRA_ISSUE_KEY}' exista.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    found_names = get_attachment_names()
    
    # 4. Exportar el resultado para que el siguiente paso en GitHub Actions lo use
    # Esto es vital para pasar información entre pasos de la Action
    if found_names:
        # Crea una cadena separada por comas para usar en el workflow YML
        names_string = ",".join(found_names)
        print(f"::set-output name=attachment_names::{names_string}")
        print("\nResultado exportado como 'attachment_names' para GitHub Actions.")
