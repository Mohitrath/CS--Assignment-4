# CSRF Demo – GET-based Forged Action
Cyber Security (IT-30001) | Web Server Security | IIIT Allahabad

## Ownership declaration
| Member | Vulnerability | Variant |
|---|---|---|
| Santu Khanra (IIT2024161) | CSRF | GET-based forged action |

(Other members add their rows/sections here.)

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run – vulnerable mode
```bash
python app.py
```
Open http://localhost:5000 and log in with `santu` / `pass123`.

## Run the attacker page (second terminal)
```bash
cd attacker
python -m http.server 8000
```
While logged in, open http://localhost:8000/evil.html in the same browser.
Go back to http://localhost:5000/profile: the email is now `hacker@evil.com`.

## Run – protected mode (anti-CSRF synchronizer token)
```bash
PROTECTED=1 python app.py       # PowerShell: $env:PROTECTED="1"; python app.py
```
Log in again and open the same evil.html: the forged request returns 403 and the email is unchanged.

## Vulnerable code path
`/change-email` in `app.py`: changes state on a GET request using only the session cookie.

## Root cause
The server trusts any request carrying a valid session cookie and the action is triggered by a GET with predictable parameters, so a third-party site can make the victim's browser send it.

## Mitigation implemented
Synchronizer token pattern: a random token is stored in the server session at login, embedded in the form as a hidden field, and verified on a POST-only endpoint.
