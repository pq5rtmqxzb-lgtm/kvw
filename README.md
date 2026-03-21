# JTF Rijnmond – Social Media Analyse Tool

Een webapplicatie voor het controleren van social media uitingen van JTF-gefinancierde projecten op naleving van **Verordening (EU) 2021/1060** en het **JTF Communicatiehandboek**.

## 🚀 Gebruik

Open `jtf-social-media-analyse.html` direct in een browser — geen server of installatie nodig.

Of host via **GitHub Pages** (zie hieronder).

## ✅ Functionaliteiten

- **37 JTF Rijnmond projecten** ingeladen vanuit de officiële projectenlijst
- **Compliancecheck** voor LinkedIn, X/Twitter, Facebook en Instagram
- **Automatische analyse** van:
  - EU-embleem of vlag-emoji 🇪🇺
  - Cofinancieringsverklaring ("medegefinancierd door de Europese Unie")
  - Fondsnaam (JTF / Just Transition Fund)
  - Verplichte hashtag `#EUinmyregion`
  - Projectnaam herkenbaar
  - Tekenlimiet per platform
  - Inhoud en beschrijving aanwezig
  - Instagram: voldoende hashtags
- **Score en verdict** (compliant / gedeeltelijk / niet compliant)
- **Verbeterpunten** met concrete tekstsuggesties
- **Analysegeskiedenis** met KPI-dashboard
- **Voorbeeldposts** per platform die volledig voldoen

## 📋 Compliancebasis

| Vereiste | Bron |
|---|---|
| EU-embleem verplicht | Bijlage IX, Verordening (EU) 2021/1060 |
| Cofinancieringsverklaring | Art. 47 + Bijlage IX |
| Fondsnaam vermelden | JTF Communicatiehandboek |
| #EUinmyregion hashtag | JTF Communicatiehandboek |
| Sanctie bij niet-naleving | Max. 3% van EU-bijdrage |

## 🌐 Hosten op GitHub Pages

```bash
# 1. Initialiseer een Git-repository
git init
git add .
git commit -m "JTF Social Media Analyse Tool – initiële versie"

# 2. Maak een repository aan op GitHub (via github.com of gh CLI)
gh repo create jtf-social-media-analyse --public --source=. --push

# 3. Activeer GitHub Pages
# → Ga naar: github.com/JOUWGEBRUIKERSNAAM/jtf-social-media-analyse
# → Settings → Pages → Source: Deploy from branch → main → / (root)
# → De site is beschikbaar op: https://JOUWGEBRUIKERSNAAM.github.io/jtf-social-media-analyse/jtf-social-media-analyse.html
```

## 📁 Bestandsstructuur

```
├── jtf-social-media-analyse.html   # Volledige webapp (één bestand)
├── README.md                        # Deze instructies
└── .gitignore                       # Git ignore regels
```

## 🔗 Bronnen

- [JTF Rijnmond website](https://jtf-rijnmond.kansenvoorwest.nl)
- [Verordening (EU) 2021/1060 – EUR-Lex](https://eur-lex.europa.eu/eli/reg/2021/1060/oj)
- [KansenVoorWest](https://www.kansenvoorwest.nl)

---
*Data laatste update: Maart 2026 — 37 projecten, €60M+ EU-bijdrage Groot-Rijnmond*
