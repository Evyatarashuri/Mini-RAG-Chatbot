**DRAFT EXERCISE BRIEF (choose ONE challenge, 3 h time‑box)**

---

### 0  Overview
You have **up to 3 hours** to ship a small, cloud‑hosted prototype that shows how you approach automation & AI problems.

*Use any language, framework, cloud host, or AI model you like.* Code quality matters, but **we care more about your architecture, problem‑solving process, and "how would this scale?" thinking.**

---

### 1  Challenges (pick one)

| # | Challenge | Core Tasks | Optional “Bonus Depth” (if time allows) |
|---|-----------|-----------|-----------------------------------------|
| **A** | **Brand Visibility Checker** | 1. Accept user input: `brand_name` + `product_or_domain`.<br>2. Generate 5‑10 realistic buyer questions (manually or via AI).<br>3. Query an LLM of your choice for each question.<br>4. Analyse each answer:<br>  • Is the brand mentioned?<br>  • Sentiment (positive / neutral / negative).<br>  • Key competitors mentioned.<br>5. Present results with:<br>  • Visibility score (e.g. “6 / 10 mentions”).<br>  • Sentiment tally.<br>  • Competitor count. | ▢ Smarter question generation<br>▢ Nuanced sentiment or competitor logic<br>▢ Charts / dashboards<br>▢ Persona‑specific prompts |
| **B** | **Mini RAG Chatbot** | 1. Ingest the three PDF policies supplied (chunk & embed).<br>2. Expose an `/ask` endpoint or mini‑UI that answers user questions **and** returns the source snippets used.<br>3. Keep everything in memory or simple local storage—no DB required. | ▢ Improved chunking strategy<br>▢ Streaming responses<br>▢ Comments on vector‑DB choice for scale<br>▢ Basic auth layer |

Choose whichever challenge lets you demonstrate your strengths.

---

### 2  What we give you

| Item | Purpose |
|------|---------|
| `policies.zip` (3 short PDFs) | Only for Challenge B. |
| This brief | Copy any part of it into your README. |

Everything else—frameworks, hosting, additional data, or LLM access keys—is up to you.

---

### 3  What you must deliver

1. **Public Git repository** containing:
   * `/README.md` with **one‑command run** instructions ( ≤ 90 sec setup ).
   * `/DECISIONS.md` (or a section in README) detailing what you built, key trade‑offs, and how you would scale / productionise it on “day 2”.
   * Source code.
2. **Live deployment URL** (Render, Replit, Fly.io, Vercel, etc.)—keep it online for at least 48 h after submission.
3. *(Optional)* Tests or CI workflow if you can fit them inside the 3 h box.
4. *(Optional)* Short demo GIF / Loom (< 2 min).
5. **Containerised build** – include a `Dockerfile` (and optionally a `docker‑compose.yml`) so reviewers can run `docker build .` and `docker run …` to start your app without local setup. Pass environment variables via `--env` flags or a template `.env` file.

> **Security note** – Do **NOT** commit secret keys. Use environment variables or secrets managers.

---

### 4  Timeboxing & honesty pledge
Track your own time—**maximum 3 real hours** from clone to push. You may use AI coding assistants, public libraries, or internet resources. **Do not receive help from another human.** In `DECISIONS.md` include a short note on how long you spent.

---

### 5  Timeline & follow‑up
* **Submission deadline** – within **7 calendar days** of receiving this brief.
* **Review & next steps** – we will quickly evaluate the repo and live demo. Short‑listed candidates will be invited to a brief code‑walk interview to discuss your decisions, scaling ideas, and next steps. Others may be declined based on the deliverables alone.

Good luck—have fun and show us how you think!
