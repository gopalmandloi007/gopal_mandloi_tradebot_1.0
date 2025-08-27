# gopal\_mandloi\_tradebot\_1.0 — README

**Language:** Mixed Hindi + English (explanations in simple Hinglish so you can copy to your audience).

---

## 1. Summary / क्या है

This repository is a Streamlit-based trading dashboard skeleton integrated with the **Definedge Integrate API** (via `pyintegrate` examples). It provides:

* Centralized connection/session management (no repeated login) using `.env` session keys.
* OTP + TOTP support for first-time login.
* Utilities for Orders (normal + GTT), Data (quotes & historical), WebSocket streaming, and master symbol management.
* Streamlit pages for Orders, Orderbook, Historical data, GTT (Auto Orders) and placeholders for Scanners/Backtest/Indicators.
* A consistent `data/` and `logs/` layout and `config.py` style helpers.

---

## 2. Quick start (local / Colab)

1. Clone or create the repo files (you can use the Colab script previously provided to auto-create the repo structure).

2. Create a Python virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. Configure credentials (choose secrets or env):

* For Streamlit UI pages use `.streamlit/secrets.toml` (recommended on Streamlit Cloud).
* For server scripts and persistent session keys use `.env` in project root.

Example `.streamlit/secrets.toml`:

```toml
[api]
token = "YOUR_API_TOKEN"
secret = "YOUR_API_SECRET"

[api.totp]
secret = ""  # optional TOTP secret
```

Example `.env` (the code will create .env if missing and will store session keys after login):

```env
INTEGRATE_API_TOKEN=your_api_token_here
INTEGRATE_API_SECRET=your_api_secret_here
INTEGRATE_TOTP_SECRET=optional_totp_secret_here
INTEGRATE_UID=
INTEGRATE_ACTID=
INTEGRATE_API_SESSION_KEY=
INTEGRATE_WS_SESSION_KEY=
```

4. Run Streamlit:

```bash
streamlit run app.py
```

---

## 3. Project structure (what each folder is for)

```
trading-dashboard-app/
├─ .streamlit/            # Streamlit secrets.toml
├─ data/
│  ├─ master/             # master symbols: trading_symbol, token, segment
│  ├─ historical/         # processed history + raw
│  ├─ trades/             # daily trade/order snapshots (datewise)
│  ├─ orders/             # saved orders (datewise)
│  └─ logs/               # application logs
├─ pages/                 # Streamlit pages (1..10)
├─ utils/                 # reusable helpers (api_utils, order_utils, ws_utils...)
├─ .gitignore
├─ README.md
├─ requirements.txt
├─ app.py
└─ config.py              # paths & helpers (recommended)
```

---

## 4. `config.py` (consolidated paths & helpers)

**Place this file at repo root.** It centralizes paths so all modules use the same location.

```python
# config.py
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MASTER_DIR = DATA_DIR / "master"
HISTORICAL_DIR = DATA_DIR / "historical"
HISTORICAL_RAW = HISTORICAL_DIR / "raw"
HISTORICAL_PROCESSED = HISTORICAL_DIR / "processed"
TRADES_DIR = DATA_DIR / "trades"
ORDERS_DIR = DATA_DIR / "orders"
LOGS_DIR = BASE_DIR / "logs"
STREAMLIT_SECRETS = BASE_DIR / ".streamlit" / "secrets.toml"
ENV_FILE = BASE_DIR / ".env"

def ensure_dirs():
    for p in [MASTER_DIR, HISTORICAL_RAW, HISTORICAL_PROCESSED, TRADES_DIR, ORDERS_DIR, LOGS_DIR, DATA_DIR]:
        p.mkdir(parents=True, exist_ok=True)

def historical_raw_path(symbol: str):
    s = symbol.replace('/', '_').replace(':', '_')
    return HISTORICAL_RAW / f"{s}.csv"

def trades_file_for_date(d: date):
    return TRADES_DIR / f"{d.strftime('%d_%m_%Y')}.csv"

def orders_file_for_date(d: date):
    return ORDERS_DIR / f"{d.strftime('%d_%m_%Y')}.csv"
```

> Use `from config import historical_raw_path, ensure_dirs` at the top of modules to get consistent paths. `ensure_dirs()` should be called once at app startup or module import if you want to auto-create folders.

---

## 5. How session management works (detailed flow)

**Goal:** login once, reuse session keys for up to 24 hours (Integrate example said session keys valid 24h).

1. `get_connection()` (in `utils/api_utils.py`) tries to read `INTEGRATE_UID`, `INTEGRATE_ACTID`, `INTEGRATE_API_SESSION_KEY`, `INTEGRATE_WS_SESSION_KEY` from `.env`.
2. If all present, it calls `conn.set_session_keys(uid, actid, api_session_key, ws_session_key)` and returns the connected client — **fast path, no login**.
3. If missing or invalid, it falls back to login using `api_token` + `api_secret` (from `.env` or `.streamlit/secrets.toml` or passed explicitly).
4. If TOTP is used, `get_connection()` will generate the TOTP using `INTEGRATE_TOTP_SECRET` (pyotp) and pass it to `conn.login(...)` if the client accepts an OTP parameter.
5. On successful login `conn.get_session_keys()` is invoked, and session keys are saved back to `.env` using `python-dotenv.set_key()`.
6. Next runs will reuse the keys.

**If session expired:** `set_session_keys()` or subsequent calls will fail — `get_connection()` will catch and run the login flow again and update `.env`.

---

## 6. Files overview — responsibilities (short)

* `utils/api_utils.py` — single place to get `ConnectToIntegrate` instance. Handles `.env`, TOTP/OTP, saving session keys.
* `utils/order_utils.py` — wrappers: `place_order`, `place_gtt_order`, `get_orders`, `get_gtt_orders`, `cancel_order`, `get_order_status`, `get_limits`.
* `utils/data_handler.py` — `get_quote`, `get_security_info`, `get_historical_data`, `save_history_to_csv`.
* `utils/ws_utils.py` — `IntegrateWSManager` class: subscribe tokens, start blocking/daemon WS with default callbacks.
* `utils/master_data_loader.py` — load `data/master/symbols.csv` and helper to find token for trading symbols.
* `pages/*.py` — Streamlit pages that use utils to show UI and charts.
* `app.py` — Streamlit home / entry.

---

## 7. Typical workflows with examples (copy-paste)

### 7.1 Place a market order (script)

```python
# test_place_order.py
from utils.order_utils import place_order

api_token = None  # will pick from .env
api_secret = None
order = place_order(api_token, api_secret, tradingsymbol='SBIN-EQ', side='BUY', quantity=1)
print(order)
```

### 7.2 Place a GTT order

```python
from utils.order_utils import place_gtt_order
place_gtt_order(None, None, tradingsymbol='SBIN-EQ', price=620.0, alert_price=619.95, quantity=1)
```

### 7.3 Fetch historical data and save

```python
from utils.data_handler import get_historical_data, save_history_to_csv
from datetime import datetime, timedelta

end = datetime.today()
start = end - timedelta(days=7)
data = get_historical_data(None, None, symbol='SBIN-EQ', start=start, end=end)
save_history_to_csv(data, 'data/historical/raw/SBIN-EQ_7d.csv')
```

### 7.4 Start WebSocket (blocking)

```python
from utils.api_utils import get_connection
from utils.ws_utils import IntegrateWSManager

conn = get_connection()
ws = IntegrateWSManager(conn)
ws.subscribe_symbols(['SBIN-EQ', 'TCS-EQ'])
ws.connect_blocking(ssl_verify=True)  # or ssl_verify=False if SSL errors
```

**Daemonized WS:** `ws.connect_daemon()` and keep main thread alive with a while loop.

---

## 8. Troubleshooting & error resolution (deep — read carefully)

I have listed common errors you may hit and how to fix them. Step-by-step with commands and diagnostics so you can resolve ASAP.

### 8.1 `GitCommandError: repository 'https://github.com/...git/' not found`

**Cause:** Remote repo doesn't exist or repo name mismatch or wrong username in URL.
**Fix:**

* Create repo on GitHub (UI) OR create via API:

```python
import requests
headers = {'Authorization': f'token {GITHUB_TOKEN}'}
requests.post('https://api.github.com/user/repos', headers=headers, json={'name': 'gopal_mandloi_tradebot_1.0'})
```

* Ensure `GITHUB_USERNAME` and `REPO_NAME` match exactly.
* If pushing to an existing repo, make sure you have `repo` scope on PAT.

### 8.2 `ModuleNotFoundError: No module named 'integrate'` or `No module named pyintegrate`

**Cause:** `pyintegrate` not installed or installed in different env.
**Fix:**

* Activate correct venv and install: `pip install -r requirements.txt` or `pip install pyintegrate`.
* If package is on GitHub: `pip install git+https://github.com/definedge/pyintegrate.git`
* Verify: `python -c "import integrate; print(integrate.__file__)"`

### 8.3 Login failed / invalid credentials

**Cause:** wrong API token/secret or OTP required and not provided.
**Fix:**

1. Verify credentials: check `.streamlit/secrets.toml` and `.env`.
2. If provider requires OTP, pass it to `get_connection(..., otp='123456')` or set `INTEGRATE_TOTP_SECRET` for TOTP.
3. Check the exact login signature expected by your installed `pyintegrate` version — sometimes OTP arg name differs.
4. Turn on debug logs to see server error message.

### 8.4 Session keys invalid or 401 during API calls

**Cause:** saved session keys expired (24h) or invalid.
**Fix:**

* Delete session keys from `.env` (INTEGRATE\_UID, INTEGRATE\_ACTID, INTEGRATE\_API\_SESSION\_KEY, INTEGRATE\_WS\_SESSION\_KEY) and re-run `get_connection()` to force login and refresh keys.
* Example to clear keys:

```python
from dotenv import set_key
set_key('.env', 'INTEGRATE_UID', '')
set_key('.env', 'INTEGRATE_API_SESSION_KEY', '')
# Or manually open .env and remove
```

### 8.5 WebSocket SSL errors

**Typical:** `ssl.SSLCertVerificationError` during `iws.connect()`.
**Fix options:**

* Preferable: fix system CA store / update certs.
* Quick dev workaround (not for prod): `iws.connect(ssl_verify=False)`.
* Check network proxies or corporate firewall that intercept SSL.

### 8.6 Rate limit / HTTP 429

**Cause:** too many API calls.
**Fix:**

* Implement exponential backoff: sleep(1), sleep(2), sleep(4) and retry.
* Cache results when possible (eg: symbol lists, static security info).

### 8.7 `KeyError` for env variables in scripts (e.g. INTEGRATE\_API\_TOKEN)

**Cause:** .env not loaded or name mismatch.
**Fix:**

* Confirm `.env` in project root and keys spelled correctly.
* `from dotenv import load_dotenv; load_dotenv()` in scripts that run outside Streamlit.
* For Streamlit pages use `st.secrets` or fallback to `os.environ`.

### 8.8 Data save / file permission errors

**Typical:** `PermissionError` when writing CSV.
**Fix:**

* Ensure directories created with `os.makedirs(..., exist_ok=True)`.
* Check user permissions for the working directory.
* In Colab write under `/content/` (Colab cannot write outside sandbox).

### 8.9 `TypeError` or signature mismatch with pyintegrate methods

**Cause:** your installed `pyintegrate` version's method signatures differ from examples.
**Fix:**

* Print `help(ConnectToIntegrate.login)` or check `pip show pyintegrate` and its documentation.
* If mismatch, adapt `utils/api_utils.py` to call the correct parameter names.

### 8.10 Debugging tips (general)

* Add logging everywhere: `logging.basicConfig(level=logging.DEBUG)` and write to `logs/general_log/errors.log`.
* Reproduce with minimal script (e.g., `test_connection.py`) to isolate.
* Check raw HTTP responses or exception stacktrace to find provider error messages.

---

## 9. Debugging checklist (if something breaks)

1. Confirm virtualenv activated and `pip list` shows `pyintegrate`.
2. Confirm `.streamlit/secrets.toml` or `.env` contains `INTEGRATE_API_TOKEN` and `INTEGRATE_API_SECRET`.
3. Try `python -c "from utils.api_utils import get_connection; get_connection()"` and see exception.
4. Check `logs/general_log/errors.log` for stacktrace.
5. If git push fails, check token scopes and repo existence.
6. If WebSocket fails, try `ssl_verify=False` to rule out TLS trust.
7. When in doubt, clear `.env` session keys and re-login.

---

## 10. Tests & sanity scripts (small examples to keep)

Create these small scripts under `tests/` and run them during development.

* `tests/test_connection.py`

```python
from utils.api_utils import get_connection
c = get_connection()
print('Connected: OK')
```

* `tests/test_order_flow.py`

```python
from utils.order_utils import place_order, get_orders
resp = place_order(None, None, 'SBIN-EQ', side='BUY', quantity=1)
print(resp)
print(get_orders(None, None))
```

* `tests/test_ws.py`

```python
from utils.api_utils import get_connection
from utils.ws_utils import IntegrateWSManager
c = get_connection()
ws = IntegrateWSManager(c)
ws.subscribe_symbols(['SBIN-EQ'])
ws.connect_blocking(ssl_verify=False)
```

---

## 11. Operational notes (production-ready tips)

* Never commit your `.env` or `.streamlit/secrets.toml` to GitHub. Add them to `.gitignore`.
* For CI/CD, store secrets in GitHub Actions secrets or Streamlit Cloud secrets, not in repository.
* For long-running websockets, run on a server (VM / Docker) with supervised process manager (systemd, supervisor, or Docker + restart policies).
* For logging use rotation (watchdog / TimedRotatingFileHandler) to keep log sizes under control.

---

## 12. If you want, I can (choose one):

* Provide a single **Colab script** that creates the repo files (including `config.py`) and pushes to GitHub (you gave token earlier). ✅
* Or create the repo and push it for you from Colab if you paste token in the Colab cell. ✅

Tell me which and I'll give that exact script next.

---

## 13. Final note

Maine deeply सोचा हुआ workflow और troubleshooting list दिया hai — agar tum specific error stacktrace paste karoge (exact traceback), मैं उसी के हिसाब से step-by-step fix dedunga.

Good luck — ready to create the repo+files for you directly if you say **"Create repo now"** and paste your token (or run in Colab with token variable).
