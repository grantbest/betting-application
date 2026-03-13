# betting-application
# WE do it inc. | MLB Inning Betting Strategy Platform

This platform is a real-time analytics and betting engine designed to identify high-probability opportunities in MLB inning-based markets using historical patterns.

---

## 1. Business Requirements

### Core Betting Systems

| System | Logic | Win Rate | Target |
| --- | --- | --- | --- |
| **1. NR2I Regression** | Both teams score in 1st; Game Total <= 9 | ~59% | No Run 2nd Inning |
| **2. Big Inning Momentum** | Previous inning had 3+ runs and 4+ baserunners | ~58% | Yes Run Next Inning |
| **3. 5th Inning Fatigue** | Game Total >= 9; Starter facing lineup 3rd time | ~55% | Yes Run 5th Inning |
| **4. Late Bullpen** | Game within 3 runs; Both bullpens top-20 ERA | ~55% | No Run 8th Inning |

### Discipline Rules
* **Price Ceiling:** Do not place bets with odds worse than **-120**.
* **Bankroll Management:** Use fractional Kelly Criterion.

---

## 2. Architecture

* **Engine:** Python 3.11+ (Asyncio)
* **Database:** PostgreSQL 15 (Storage)
* **Message Broker:** Redis 7 (Real-time updates)
* **Alerting:** Discord Webhooks

---

## 3. Setup Instructions

### Prerequisites
* Docker & Docker Compose
* Python 3.11+

### Installation

1. **Start Infrastructure:**
   ```bash
   docker-compose up -d
   ```

2. **Initialize Database:**
   Connect to `localhost:5432` (User: `admin`, Pass: `password123`, DB: `mlb_engine`) and run the contents of `schema.sql`.

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment:**
   Set your Discord Webhook URL:
   ```bash
   export DISCORD_WEBHOOK_URL="your_webhook_url_here"
   ```

5. **Run Engine:**
   ```bash
   python engine.py
   ```

---

## 4. Mathematical Foundation

**Kelly Criterion Formula:**

$$f^* = \frac{bp - q}{b}$$

Where:
* $f^*$ = Percentage of bankroll to wager.
* $b$ = Net odds (Decimal odds - 1).
* $p$ = Probability of winning.
* $q$ = Probability of losing ($1 - p$).