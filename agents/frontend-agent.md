# 🎨 Frontend Agent
## JTF Rijnmond Social Media Compliance Platform

---

## Role & Mandate

The Frontend Agent owns the user interface: the HTML/JS single-page application hosted on GitHub Pages. It progressively migrates hardcoded JSON data to live API calls, adds authentication, and improves UX for the JTF compliance team.

---

## Migration Roadmap: Static → API-driven

### Phase 1 (now): Hybrid mode
The current HTML embeds `PROJECTS`, `SCRAPED_RESULTS`, `PROJECT_URLS` as JSON constants.
These are the **fallback** when the API is not yet configured.

### Phase 2 (M1): Load projects from API
Replace:
```js
const PROJECTS = [...]; // hardcoded
```
With:
```js
let PROJECTS = [];
async function bootstrap() {
  try {
    PROJECTS = await API.getProjects();
  } catch {
    PROJECTS = PROJECTS_FALLBACK; // keep static fallback
  }
  renderProjectsGrid(PROJECTS);
}
```

### Phase 3 (M3): Load compliance results from API
Replace the hardcoded `SCRAPED_RESULTS` with:
```js
async function loadLiveResults() {
  const compliance = await API.getProjectCompliance();
  const posts      = await API.getAllPosts(200);
  renderLiveTable(posts, compliance);
}
```

### Phase 4 (M4): Add authentication
```html
<!-- Add login modal -->
<div id="login-modal" class="modal">
  <h2>Inloggen — JTF Rijnmond</h2>
  <input id="email" type="email" placeholder="E-mailadres">
  <input id="pass" type="password" placeholder="Wachtwoord">
  <button onclick="doLogin()">Inloggen</button>
</div>
```
```js
async function doLogin() {
  await API.login(email, password);
  hideLoginModal();
  loadProtectedData(); // posts, scrape history
}
```

---

## UI Components Inventory

| Component | Status | API-connected |
|---|---|---|
| Tab navigation | ✅ Working | — |
| Analyse post form | ✅ Working | Client-side only |
| Project grid + links | ✅ Working | ❌ Static JSON |
| Dashboard charts | ✅ Working | ❌ Static JSON |
| EU Regulation tab | ✅ Working | — |
| Live Results tab | ✅ Working | ❌ Static JSON |
| Login modal | ❌ Missing | — |
| Scrape history view | ❌ Missing | — |
| PDF export | ❌ Missing | — |
| Email digest | ❌ Missing | — |

---

## File Structure (target)

```
frontend/
├── index.html          ← main SPA (replaces jtf-social-media-analyse.html)
├── src/
│   ├── api.js          ← API client (done ✅)
│   ├── auth.js         ← login/logout/session
│   ├── charts.js       ← dashboard chart rendering
│   ├── compliance.js   ← 7-check engine
│   └── export.js       ← PDF / CSV export
└── assets/
    ├── eu-emblem.svg   ← EU logo (required for official reports)
    └── style.css       ← extracted styles
```

---

## Design Principles

- **No build step** — vanilla JS or CDN Vue 3, GitHub Pages compatible
- **Progressive enhancement** — static fallback if API is down
- **Mobile-friendly** — JTF officers may check on phone
- **Accessibility** — Dutch language, WCAG 2.1 AA target
- **Print-ready** — compliance reports should print cleanly

---

## Testing Checklist

- [ ] All 5 tabs navigate without recursion error
- [ ] Project cards show platform links
- [ ] Compliance score calculation matches server-side
- [ ] Login/logout works
- [ ] API errors show user-friendly message (not raw JSON)
- [ ] Works on Chrome, Firefox, Edge, Safari
- [ ] Works on mobile (375px viewport)
