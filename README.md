# Web Server Security — Group Assignment

**Course:** Cyber Security (IT-30001)  
**Semester:** Autumn 2026  
**Institute:** Indian Institute of Information Technology Allahabad

This repository contains our group project for demonstrating four common web-server vulnerabilities. Each member is responsible for implementing one assigned vulnerability, demonstrating it in our own application, applying a mitigation, and showing that the same test is blocked after mitigation.

## Group Members and Vulnerability Allocation

| Member | Vulnerability | Assigned variant |
|---|---|---|
| Amarnath | SQL Injection (SQLi) | Authentication bypass |
| Mohit Kumar | Cross-Site Scripting (XSS) | Stored XSS |
| Santu Khanra | Cross-Site Request Forgery (CSRF) | GET-based forged action |
| Ankit Kumar Maurya | OS Command Injection | In-band command injection |

## Repository Structure

```text
CS--Assignment-4/
├── SQL-Injection/
│   └── README.md
├── Stored-XSS/
│   └── README.md
├── CSRF/
│   └── README.md
├── OS-Command-Injection/
│   └── README.md
└── README.md
```

## Vulnerability Demonstrations

### 1. SQL Injection (SQLi) — Authentication Bypass
- **Assigned to:** Amarnath
- **Demo functionality:** Login page connected to a database
- **Mitigation to implement:** Parameterized SQL queries

### 2. Stored Cross-Site Scripting (Stored XSS)
- **Assigned to:** Mohit Kumar
- **Demo functionality:** Comment submission and display
- **Mitigation to implement:** Context-aware output encoding

### 3. Cross-Site Request Forgery (CSRF)
- **Assigned to:** Santu Khanra
- **Demo functionality:** Authenticated profile-setting change
- **Assigned variant:** GET-based forged action
- **Mitigation to implement:** Anti-CSRF synchronizer token

### 4. OS Command Injection
- **Assigned to:** Ankit Kumar Maurya
- **Demo functionality:** IP ping utility
- **Assigned variant:** In-band command injection
- **Mitigation to implement:** Avoid shell execution; use argument-vector execution

## Work Required for Each Member

Every member must complete the following:

1. Implement the assigned vulnerable variant and identify the vulnerable code path.
2. Demonstrate a working exploit against this group's application and record the exact payload or request.
3. Explain the root cause clearly.
4. Implement the selected mitigation.
5. Run the same payload/request again and capture evidence that the attack is blocked.
6. Explain other mitigation alternatives covered in the lecture slides.
7. Record an individual voice-over section of approximately 2–3 minutes and prepare for the individual viva.

## Setup and Run

The application setup and run commands will be added here once the group application framework, dependencies, and entry point are finalized.

For now, open the relevant vulnerability folder and follow its README for the assigned module and implementation checklist.

## Testing and Safety

- Perform demonstrations only against this group's own application or another environment for which you have explicit authorization.
- Use controlled test data and a local development environment where possible.
- Do not test these payloads against third-party websites or systems.
- Keep vulnerable demonstration code isolated from production systems.

## Submission Checklist

- [ ] Public GitHub repository containing the application source code.
- [ ] README with setup/run instructions and completed ownership declaration.
- [ ] Working demonstration of each assigned vulnerability.
- [ ] Evidence of the exploit before mitigation and the same test being blocked after mitigation.
- [ ] Group screen-recording with voice-over: exploit first, then mitigation.
- [ ] Video or unlisted video link submitted as instructed on the course page.
- [ ] Every member prepared to demonstrate and explain their own variant during the viva.

## Important

This repository is an educational security assignment. Each member must implement one assigned variant, demonstrate the exploit, implement one mitigation, and explain alternative mitigations theoretically. Follow the assignment instructions and lecture slides.
