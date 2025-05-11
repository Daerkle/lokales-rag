# Selbstgehostetes KI-Paket

**Selbstgehostetes KI-Paket** ist eine offene Docker-Compose-Vorlage, die schnell eine voll ausgestattete lokale KI- und Low-Code-Entwicklungsumgebung bereitstellt – inklusive Ollama für lokale LLMs, Open WebUI als Oberfläche für die Interaktion mit deinen N8N-Agenten sowie Supabase für Datenbank, Vektor-Store und Authentifizierung. Inklusive n8n <-> Openwebui Pipeline


##  Links

![n8n.io - Screenshot](https://raw.githubusercontent.com/n8n-io/self-hosted-ai-starter-kit/main/assets/n8n-demo.gif)


### Enthaltene Komponenten

✅ [**Selbstgehostetes n8n**](https://n8n.io/) – Low-Code-Plattform mit über 400 Integrationen und fortschrittlichen KI-Komponenten
✅ [**Supabase**](https://supabase.com/) – Open-Source-Datenbank-as-a-Service – die meistgenutzte Datenbank für KI-Agenten
✅ [**Ollama**](https://ollama.com/) – Plattform für lokale LLMs
✅ [**Open WebUI**](https://openwebui.com/) – ChatGPT-ähnliche Oberfläche für lokale Modelle und N8N-Agenten
✅ [**Flowise**](https://flowiseai.com/) – No/Low-Code KI-Agenten-Builder, der sehr gut mit n8n harmoniert
✅ [**Qdrant**](https://qdrant.tech/) – Open-Source, performanter Vektor-Store mit umfassender API
✅ [**SearXNG**](https://searxng.org/) – Open-Source-Metasuchmaschine, die Ergebnisse von bis zu 229 Diensten aggregiert
✅ [**Langfuse**](https://langfuse.com/) – Open-Source-Plattform für LLM-Engineering und Agenten-Überwachung

## Voraussetzungen

Vor dem Start stelle sicher, dass folgende Software installiert ist:

- [Python](https://www.python.org/downloads/) – Zum Ausführen des Setup-Skripts erforderlich
- [Git/GitHub Desktop](https://desktop.github.com/) – Für einfaches Repository-Management
- [Docker/Docker Desktop](https://www.docker.com/products/docker-desktop/) – Zum Ausführen aller Dienste erforderlich

## Installation auf Proxmox VE

Hier ist ein detaillierter Plan, wie du das Projekt auf Proxmox VE installierst und startest. Ich gehe davon aus, dass du eine VM oder einen LXC-Container mit Ubuntu (empfohlen) verwendest.

### 1. VM/LXC-Container in Proxmox anlegen

- **Im Proxmox Webinterface**:
  - Klicke auf „Erstellen“ > „CT“ (Container) oder „VM“ (Virtuelle Maschine).
  - Wähle ein Ubuntu-Image (z.B. Ubuntu 22.04 LTS).
  - Weise ausreichend CPU, RAM (mind. 8GB empfohlen) und Speicherplatz zu (mind. 20GB).
  - Netzwerk konfigurieren (am besten DHCP oder statische IP).
  - Installation abschließen und Container/VM starten.

### 2. Grundsystem vorbereiten

- **Per Konsole/SSH in die VM/den Container einloggen**
- System aktualisieren:
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```
- Notwendige Pakete installieren:
  ```bash
  sudo apt install -y git docker.io docker-compose python3 python3-pip
  ```
- Docker-Dienst starten und aktivieren:
  ```bash
  sudo systemctl enable --now docker
  ```

### 3. Projekt klonen

- Wechsle in das gewünschte Verzeichnis (z.B. `/opt`):
  ```bash
  cd /opt
  ```
- Repository klonen:
  ```bash
  git clone https://github.com/Daerkle/lokales-rag.git
  cd lokales-rag
  ```

### 4. Umgebungsvariablen einrichten

- Kopiere die Beispiel-Umgebungsdatei:
  ```bash
  cp .env.example .env
  ```
- Öffne `.env` mit einem Editor (z.B. `nano .env`) und trage sichere Werte für die Variablen ein (Passwörter, Keys etc.).

### 5. Dienste starten

- Starte alle Services mit Docker Compose:
  ```bash
  sudo docker-compose up -d
  ```
- Prüfe mit `docker ps`, ob alle Container laufen.

### 6. Portainer installieren (Port 8001)

```bash
sudo docker volume create portainer_data
sudo docker run -d -p 8001:8000 --name=portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data portainer/portainer-ce
```
### 6.1 Nginx Proxy Manager installieren (Optional)

Um deine Dienste sicher über Domains mit HTTPS zugänglich zu machen, kannst du den Nginx Proxy Manager verwenden.

**Docker Compose für Nginx Proxy Manager:**

Füge den folgenden Service zu deiner `docker-compose.yml` hinzu oder erstelle eine separate `docker-compose.nginx.yml`:

```yaml
version: '3.8'
services:
  app:
    image: 'jc21/nginx-proxy-manager:latest'
    restart: unless-stopped
**Erstanmeldung Nginx Proxy Manager:**  
Benutzername: `admin@example.com`  
Passwort: `changeme`
    ports:
      # Diese Ports sind für den Zugriff auf den Proxy Manager und die weitergeleiteten Dienste
      - '80:80'    # HTTP
      - '443:443'  # HTTPS
      # Admin-Interface des Nginx Proxy Managers
      - '81:81'
    volumes:
      - ./nginxproxymanager/data:/data
      - ./nginxproxymanager/letsencrypt:/etc/letsencrypt
```

**Starten des Nginx Proxy Managers:**

Wenn du eine separate Compose-Datei verwendest:
```bash
sudo docker-compose -f docker-compose.nginx.yml up -d
```
Andernfalls, wenn du es zur Haupt-`docker-compose.yml` hinzugefügt hast, starte alle Dienste neu:
```bash
sudo docker-compose up -d --force-recreate
```

**Konfiguration des Nginx Proxy Managers:**

1.  Öffne das Admin-Interface des Nginx Proxy Managers im Browser: `http://[IP-deiner-VM]:81`
2.  Standard-Anmeldedaten beim ersten Start:
    *   Email: `admin@example.com`
    *   Passwort: `changeme`
3.  Ändere sofort das Passwort.
4.  **Proxy Hosts einrichten:**
    *   Gehe zu "Hosts" -> "Proxy Hosts".
    *   Klicke auf "Add Proxy Host".
    *   **Domain Names:** Gib deine Domain ein (z.B. `n8n.deinedomain.com`).
    *   **Scheme:** `http`
    *   **Forward Hostname / IP:** `127.0.0.1` (oder die IP des Dienstes, falls er in einem anderen Docker-Netzwerk oder einer anderen VM läuft).
    *   **Forward Port:** Der Port des Dienstes, den du freigeben möchtest (z.B. `5678` für n8n, `71` für einen benutzerdefinierten Dienst).
    *   Aktiviere "Block Common Exploits".
    *   **SSL-Tab:**
        *   Wähle "Request a new SSL Certificate" mit Let's Encrypt.
        *   Aktiviere "Force SSL" und "HTTP/2 Support".
        *   Stimme den Let's Encrypt ToS zu.
        *   Speichern.

Der Nginx Proxy Manager kümmert sich nun um die SSL-Zertifikate und leitet Anfragen an deine internen Dienste weiter. Für den Port 71 würdest du entsprechend einen Proxy Host einrichten, der auf `127.0.0.1` und Port `71` zeigt, und diesem eine Domain zuweisen.

### 7. Webinterfaces aufrufen

- **n8n:**
  Im Browser öffnen: `http://[IP-der-VM]:5678`
- **Open WebUI:**
  Im Browser öffnen: `http://[IP-der-VM]:3000`
- **Portainer:**
  Im Browser öffnen: `http://[IP-der-VM]:8001` (Ersteinrichtung im Browser)


### 8. Workflows und Funktionen einrichten

- Folge der deutschen Anleitung im [`README.md`](README.md:1) für die Einrichtung der Workflows, Zugangsdaten und Funktionen.

---
## Installation

Repository klonen und ins Projektverzeichnis wechseln:
```bash
git clone https://github.com/Daerkle/lokales-rag.git
cd lokales-rag
```

Vor dem Start der Dienste müssen die Umgebungsvariablen für Supabase gemäß deren [Self-Hosting-Anleitung](https://supabase.com/docs/guides/self-hosting/docker#securing-your-services) eingerichtet werden.

1. Kopiere `.env.example` und benenne es in `.env` im Projektstammverzeichnis um.
2. Setze folgende erforderliche Umgebungsvariablen:
   ```bash
   ############
   # N8N Konfiguration
   ############
   N8N_ENCRYPTION_KEY=
   N8N_USER_MANAGEMENT_JWT_SECRET=

   ############
   # Supabase Secrets
   ############
   POSTGRES_PASSWORD=
   JWT_SECRET=
   ANON_KEY=
   SERVICE_ROLE_KEY=
   DASHBOARD_USERNAME=
   DASHBOARD_PASSWORD=
   POOLER_TENANT_ID=

   ############
   # Langfuse Zugangsdaten
   ############

   CLICKHOUSE_PASSWORD=
   MINIO_ROOT_PASSWORD=
   LANGFUSE_SALT=
   NEXTAUTH_SECRET=
   ENCRYPTION_KEY=
   ```

> [!IMPORTANT]
> Make sure to generate secure random values for all secrets. Never use the example values in production.

3. Set the following environment variables if deploying to production, otherwise leave commented:
   ```bash
   ############
   # Caddy Config
   ############

   N8N_HOSTNAME=n8n.yourdomain.com
   WEBUI_HOSTNAME=:openwebui.yourdomain.com
   FLOWISE_HOSTNAME=:flowise.yourdomain.com
   SUPABASE_HOSTNAME=:supabase.yourdomain.com
   OLLAMA_HOSTNAME=:ollama.yourdomain.com
   SEARXNG_HOSTNAME=searxng.yourdomain.com
   LETSENCRYPT_EMAIL=your-email-address
   ```   

---

The project includes a `start_services.py` script that handles starting both the Supabase and local AI services. The script accepts a `--profile` flag to specify which GPU configuration to use.

### Für Nvidia-GPU-Nutzer

```bash
python start_services.py --profile gpu-nvidia
```
> **Hinweis:** Wenn du deine Nvidia-GPU noch nie mit Docker verwendet hast, folge den [Ollama Docker-Anweisungen](https://github.com/ollama/ollama/blob/main/docs/docker.md).

### Für AMD-GPU-Nutzer unter Linux

```bash
python start_services.py --profile gpu-amd
```

### Für Mac / Apple Silicon Nutzer

Mit einem Mac (M1 oder neuer) kannst du deine GPU leider nicht an den Docker-Container durchreichen. Es gibt zwei Optionen:

1. Das Starter-Kit komplett auf der CPU ausführen:
   ```bash
   python start_services.py --profile cpu
   ```
2. Ollama auf dem Mac laufen lassen und von n8n aus darauf zugreifen:
   ```bash
   python start_services.py --profile none
   ```
   Installationsanleitung für Ollama auf dem Mac findest du auf der [Ollama-Homepage](https://ollama.com/).

#### Für Mac-Nutzer mit lokalem OLLAMA

Wenn OLLAMA lokal läuft (nicht in Docker), muss die Umgebungsvariable OLLAMA_HOST in der n8n-Konfiguration angepasst werden. Aktualisiere den x-n8n-Abschnitt in deiner Docker Compose Datei wie folgt:
```yaml
x-n8n: &service-n8n
  # ... weitere Konfigurationen ...
  environment:
    # ... weitere Umgebungsvariablen ...
    - OLLAMA_HOST=host.docker.internal:11434
```
Nachdem „Editor is now accessible via: http://localhost:5678/“ erscheint:

1. Gehe zu http://localhost:5678/home/credentials
2. Klicke auf „Local Ollama service“
3. Ändere die Basis-URL zu „http://host.docker.internal:11434/“

### Für alle anderen

```bash
python start_services.py --profile cpu
```

## Deployment in der Cloud

### Voraussetzungen

- Linux-Maschine (bevorzugt Ubuntu) mit Nano, Git und Docker installiert

### Zusätzliche Schritte

Vor dem Ausführen der obigen Befehle:

1. Führe die Befehle als root aus, um die notwendigen Ports zu öffnen:
   - ufw enable
   - ufw allow 8000 && ufw allow 8001 && ufw allow 3000 && ufw allow 5678 && ufw allow 3002 && ufw allow 80 && ufw allow 443
   - ufw allow 3001 (für Flowise, Authentifizierung siehe [Flowise Doku](https://docs.flowiseai.com/configuration/environment-variables))
   - ufw allow 8080 (für SearXNG)
   - ufw allow 11434 (für Ollama)
   - ufw reload

2. Lege A-Records bei deinem DNS-Anbieter für die Subdomains an, die du in der .env für Caddy einträgst.

   Beispiel: A-Record für n8n auf [Cloud-Instanz-IP] für n8n.deinedomain.com

## ⚡️ Schnellstart & Nutzung

Das Herzstück ist eine docker-compose-Datei, die bereits vorkonfiguriert ist. Nach der Installation:

1. Öffne <http://localhost:5678/> im Browser, um n8n einzurichten (nur einmal nötig, es wird kein Konto bei n8n erstellt!).
2. Öffne das enthaltene Workflow: <http://localhost:5678/workflow/vTN9y2dLXqTiDfPT>
3. Lege Zugangsdaten für alle Dienste an:
   
   Ollama URL: http://ollama:11434

   Postgres (über Supabase): Nutze DB, Benutzername und Passwort aus der .env. WICHTIG: Host ist 'db'
   (Das ist der Name des Dienstes, der Supabase ausführt.)

   Qdrant URL: http://qdrant:6333 (API-Key beliebig, läuft lokal)
   Google Drive: Folge [dieser Anleitung von n8n](https://docs.n8n.io/integrations/builtin/credentials/google/).
   Verwende nicht localhost für die Weiterleitungs-URI, sondern eine andere Domain, die du besitzt; es wird trotzdem funktionieren!
   Alternativ kannst du [lokale Datei-Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.localfiletrigger/) einrichten.
4. Wähle **Test workflow**, um den Workflow zu starten.
5. Wenn du den Workflow zum ersten Mal ausführst, musst du möglicherweise warten,
   bis Ollama Llama3.1 heruntergeladen hat. Du kannst die Docker-Konsolenprotokolle
   einsehen, um den Fortschritt zu überprüfen.
6. Stelle sicher, dass du den Workflow als aktiv schaltest und die "Production"-Webhook-URL kopierst!
7. Öffne <http://localhost:3000/> in deinem Browser, um Open WebUI einzurichten.
   Dies musst du nur einmal tun. Du erstellst hier KEIN Konto bei Open WebUI,
   es ist nur ein lokales Konto für deine Instanz!
8. Gehe zu Arbeitsbereich -> Funktionen -> Funktion hinzufügen -> Gib einen Namen und eine Beschreibung ein und füge dann den Code aus [`n8n_pipe.py`](n8n_pipe.py:1) ein.

   Die Funktion ist auch [hier auf der Open WebUI-Seite veröffentlicht](https://openwebui.com/f/coleam/n8n_pipe/).

9. Klicke auf das Zahnrad und setze n8n_url auf die Produktions-Webhook-URL.
10. Funktion aktivieren – sie steht nun im Model-Dropdown links oben zur Verfügung!

n8n öffnen: <http://localhost:5678/>
Open WebUI öffnen: <http://localhost:3000/>

Mit n8n stehen dir über 400 Integrationen und viele KI-Nodes wie [AI Agent](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/), [Text classifier](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.text-classifier/) und [Information Extractor](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.information-extractor/) zur Verfügung. Für alles Lokale: Nutze den Ollama-Node für Sprachmodelle und Qdrant als Vektor-Store.

> **Hinweis:** Dieses Starter-Kit ist für den schnellen Einstieg in selbstgehostete KI-Workflows gedacht. Es ist nicht vollständig für den Produktivbetrieb optimiert, aber die Komponenten funktionieren gut zusammen für Prototypen. Passe es nach Bedarf an.

## Upgrade

Um alle Container auf die neuesten Versionen zu aktualisieren, führe folgende Befehle aus:
```bash
# Alle Dienste stoppen
docker compose -p localai --profile <dein-profile> -f docker-compose.yml -f supabase/docker/docker-compose.yml down

# Neueste Versionen aller Container ziehen
docker compose -p localai --profile <dein-profile> -f docker-compose.yml -f supabase/docker/docker-compose.yml pull

# Dienste mit gewünschtem Profil neu starten
python start_services.py --profile <dein-profile>
```
Ersetze `<dein-profile>` mit: `cpu`, `gpu-nvidia`, `gpu-amd` oder `none`.

Hinweis: Das Skript `start_services.py` selbst aktualisiert keine Container – es startet sie nur neu oder lädt sie beim ersten Mal herunter. Für Updates müssen die obigen Befehle ausgeführt werden.

## Fehlerbehebung

Hier Lösungen zu häufigen Problemen:

### Supabase-Probleme

- **Supabase Pooler startet ständig neu:** Siehe [diesen GitHub-Issue](https://github.com/supabase/supabase/issues/30210#issuecomment-2456955578).
- **Supabase Analytics startet nicht:** Nach Änderung des Postgres-Passworts Ordner `supabase/docker/volumes/db/data` löschen.
- **Docker Desktop:** In den Docker-Einstellungen „Expose daemon on tcp://localhost:2375 without TLS“ aktivieren.
- **Supabase Service Unavailable:** Kein „@“-Zeichen im Postgres-Passwort verwenden! Wenn die Verbindung zum Kong-Container funktioniert, aber n8n keine Verbindung bekommt, ist dies meist die Ursache. Andere Sonderzeichen könnten ebenfalls problematisch sein.

### GPU-Unterstützung

- **Windows GPU:** Probleme mit Ollama und GPU unter Windows? In Docker Desktop WSL 2 Backend aktivieren und [Docker GPU-Doku](https://docs.docker.com/desktop/features/gpu/) beachten.
- **Linux GPU:** Probleme mit Ollama und GPU unter Linux? [Ollama Docker-Anleitung](https://github.com/ollama/ollama/blob/main/docs/docker.md) befolgen.

## 👓 Empfohlene Lektüre

n8n bietet viele Inhalte für den schnellen Einstieg in KI-Konzepte und Nodes. Bei Problemen siehe [Support](#support).

- [KI-Agenten für Entwickler: Von Theorie zur Praxis mit n8n](https://blog.n8n.io/ai-agents/)
- [Tutorial: Einen KI-Workflow in n8n erstellen](https://docs.n8n.io/advanced-ai/intro-tutorial/)
- [Langchain-Konzepte in n8n](https://docs.n8n.io/advanced-ai/langchain/langchain-n8n/)
- [Demonstration der Hauptunterschiede zwischen Agenten und Chains](https://docs.n8n.io/advanced-ai/examples/agent-chain-comparison/)
- [Was sind Vektor-Datenbanken?](https://docs.n8n.io/advanced-ai/examples/understand-vector-databases/)


## 🛍️ Weitere KI-Vorlagen

Für weitere Ideen siehe die [**offizielle n8n AI-Vorlagen-Galerie**](https://n8n.io/workflows/?categories=AI). Dort kannst du Workflows direkt in deine Instanz importieren.

### Zentrale KI-Konzepte

- [KI-Agenten-Chat](https://n8n.io/workflows/1954-ai-agent-chat/)
- [KI-Chat mit beliebigen Datenquellen (auch mit dem n8n-Workflow-Tool)](https://n8n.io/workflows/2026-ai-chat-with-any-data-source-using-the-n8n-workflow-tool/)
- [Chat mit OpenAI Assistant (durch Hinzufügen eines Speichers)](https://n8n.io/workflows/2098-chat-with-openai-assistant-by-adding-a-memory/)
- [Ein Open-Source-LLM verwenden (via HuggingFace)](https://n8n.io/workflows/1980-use-an-open-source-llm-via-huggingface/)
- [Mit PDF-Dokumenten chatten (Quellen zitieren)](https://n8n.io/workflows/2165-chat-with-pdf-docs-using-ai-quoting-sources/)
- [KI-Agent, der Webseiten scrapen kann](https://n8n.io/workflows/2006-ai-agent-that-can-scrape-webpages/)

### Lokale KI-Vorlagen

- [Steuergesetz-Assistent](https://n8n.io/workflows/2341-build-a-tax-code-assistant-with-qdrant-mistralai-and-openai/)
- [Dokumente in Lernnotizen aufteilen mit MistralAI und Qdrant](https://n8n.io/workflows/2339-breakdown-documents-into-study-notes-using-templating-mistralai-and-qdrant/)
- [Finanzdokumenten-Assistent mit Qdrant und](https://n8n.io/workflows/2335-build-a-financial-documents-assistant-using-qdrant-and-mistralai/) [ Mistral.ai](http://mistral.ai/)
- [Rezeptempfehlungen mit Qdrant und Mistral](https://n8n.io/workflows/2333-recipe-recommendations-with-qdrant-and-mistral/)

## Tipps & Tricks

### Zugriff auf lokale Dateien

Das selbstgehostete KI-Starter-Kit erstellt einen freigegebenen Ordner (standardmäßig im selben Verzeichnis), der in den n8n-Container eingebunden wird und n8n den Zugriff auf Dateien auf der Festplatte ermöglicht. Dieser Ordner befindet sich innerhalb des n8n-Containers unter `/data/shared` – dies ist der Pfad, den du in Nodes verwenden musst, die mit dem lokalen Dateisystem interagieren.

**Nodes, die mit dem lokalen Dateisystem interagieren**

- [Dateien von der Festplatte lesen/schreiben](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.filesreadwrite/)
- [Lokaler Datei-Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.localfiletrigger/)
- [Befehl ausführen](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)


## Bugfixes: Docker Compose anpassen

Falls es Probleme mit der Docker Compose Version gibt (z.B. auf neueren Systemen oder nach Updates), führe folgende Schritte aus, um die aktuelle Docker Compose CLI-Version zu installieren:

```bash
sudo apt remove docker-compose -y
mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose
```

Danach steht das aktuelle `docker compose`-Kommando zur Verfügung.

## Alles updaten (Update-Anleitung)

Um alle Container und das Repository auf den neuesten Stand zu bringen, führe folgende Schritte aus:

1. Repository aktualisieren:
   ```bash
   git pull
   ```

2. Container stoppen und alte Images entfernen:
   ```bash
   sudo docker compose down
   sudo docker system prune -af
   ```

3. Neueste Images herunterladen:
   ```bash
   sudo docker compose pull
   ```

4. Container wieder starten:
   ```bash
   sudo docker compose up -d
   ```

Damit sind alle Services und Images auf dem aktuellen Stand.
