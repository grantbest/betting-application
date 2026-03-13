# WE do it inc. | MLB Betting Engine

This project is a Python-based analytics and betting engine for Major League Baseball (MLB) games. It identifies high-probability betting opportunities in real-time based on a set of predefined statistical models and sends alerts via Discord.

**Core Technologies:**
*   **Backend:** Python 3.11+ (with `asyncio`)
*   **Data:** `mlb-statsapi` Python library for live game data.
*   **Database:** PostgreSQL 15 for storing historical data, and tracking bets.
*   **Messaging:** Redis 7 for real-time updates (though not fully implemented in the provided code).
*   **Alerting:** Discord webhooks.
*   **Infrastructure:** Docker and Docker Compose for managing services.

**Architecture:**
The system is composed of a Python engine that fetches live MLB game data, applies several betting logic systems, and if a condition is met, calculates the optimal stake using the Kelly Criterion. It then sends a formatted alert to a Discord channel. The engine relies on a PostgreSQL database to log inning-by-inning data and track bets. All services (PostgreSQL, Redis, pgAdmin) are containerized using Docker.

# GitOps & CI/CD

The project includes a GitOps-ready CI/CD pipeline using GitHub Actions and Docker Compose.

**Pipeline Workflows:**
- **Build & Push:** On every push to `main` and `dev` branches, Docker images for the `engine`, `frontend`, and `mock-api` (dev-only) are built and pushed to the GitHub Container Registry (GHCR).
- **Automated Deployment:**
    - **Development:** Pushes to the `dev` branch automatically deploy to the development server using `docker-compose.yml` and `docker-compose.dev.yml`.
    - **Production:** Pushes to the `main` branch automatically deploy to the production server using `docker-compose.yml` and `docker-compose.prod.yml`.

**Required GitHub Secrets:**
To enable automated deployments, set up the following secrets in your GitHub repository:
- `DEV_SSH_HOST`: Hostname or IP of the development server.
- `DEV_SSH_USER`: SSH username for the development server.
- `DEV_SSH_KEY`: Private SSH key for accessing the development server.
- `PROD_SSH_HOST`: Hostname or IP of the production server.
- `PROD_SSH_USER`: SSH username for the production server.
- `PROD_SSH_KEY`: Private SSH key for accessing the production server.
- `DISCORD_WEBHOOK_URL`: (Production) The Discord webhook URL for betting alerts.
- `DB_PASS`: (Production) The PostgreSQL password for the production database.

**Environment Specifics:**
- **Development:** Uses a mock API server (`scripts/mock_api`) to simulate MLB game data, allowing for testing without hitting rate limits or needing live games.
- **Production:** Connects to live MLB APIs and uses a real Discord webhook.

# Building and Running locally

**1. Start Infrastructure:**
To start the PostgreSQL database and Redis message broker, run:
```bash
docker-compose up -d
```

**2. Initialize Database:**
The database schema must be initialized. You can do this by running the `init_db.py` script, which applies the `schema.sql` file.
```bash
python init_db.py
```
Alternatively, you can connect to the database directly at `localhost:5432` (User: `admin`, Pass: `password123`, DB: `mlb_engine`) and execute the contents of `schema.sql`.

**3. Install Dependencies:**
Install the required Python packages:
```bash
pip install -r requirements.txt
```

**4. Configure Environment:**
The application uses a Discord webhook to send alerts. You must set the webhook URL as an environment variable:
```bash
export DISCORD_WEBHOOK_URL="your_webhook_url_here"
```

**5. Run the Engine:**
To start the main application, run the `engine.py` script:
```bash
python engine.py
```

# Development Conventions

*   **Configuration:** Database credentials and the Discord webhook URL are configured via environment variables. The `engine.py` and `init_db.py` scripts provide default values for local development.
*   **Database Schema:** The database schema is defined in `schema.sql`. Any changes to the database structure should be made in this file and re-applied. The `init_db.py` script is provided for convenience.
*   **Alerting:** All betting alerts are sent through the `DiscordWebhookAlert` class in `discord_webhook.py`. This class standardizes the format of the alerts.
*   **Betting Logic:** The core betting strategies are implemented as separate functions within `engine.py` (e.g., `check_nr2i_logic`, `check_big_inning_momentum`).
*   **Mathematical Models:** The Kelly Criterion is used for bankroll management and is implemented in the `calculate_kelly` function.
