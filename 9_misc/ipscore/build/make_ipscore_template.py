#!/usr/bin/env python3
"""
Build build/templates/ipscore_template.html.j2 out of the current IPscore_IT.html
(the blank Italian form) by literal, uniqueness-checked substitutions.

Why start from a real working file instead of writing the template from scratch:
every substitution is checked to occur exactly once in the source before being
applied, so the result is guaranteed to be structurally identical to a file that
is already known to work -- only the enumerated, language/demo-specific spots
(identified via a full diff against IPscore_EN_Demo.html) become Jinja
placeholders. CSS and all engine logic (VAN calc, radar, navigation) are
untouched and shared by every rendered variant.
"""
import re
import sys

SRC = "../IPscore_IT.html"
OUT = "templates/ipscore_template.html.j2"

with open(SRC, encoding="utf-8") as f:
    html = f.read()

replacements = []  # (old, new) applied in order, each old must be unique at apply time

def add(old, new):
    replacements.append((old, new))

# --- <head> ---
add('<html lang="it">', '<html lang="{{ ui.html_lang }}">')
add(
    '<title>IPscore 3.0 — EPO · Valutazione Economica del Brevetto</title>',
    "<title>{% if demo %}{{ ui.title_demo }}{% else %}{{ ui.title_blank }}{% endif %}</title>",
)

# --- header ---
add(
    '  <div><div class="brand">IPscore 3.0 &mdash; Strumento EPO &bull; Adattamento ASP</div>'
    '<div class="sub">Valutazione qualitativa ed economica del brevetto · European Patent Office</div></div>\n'
    '  <div class="badge">TOOL INTERATTIVO</div>\n'
    '</header>\n'
    '<div class="step-bar" id="step-bar"></div>\n'
    '<div id="pages"></div>',
    '  <div><div class="brand">{{ ui.brand }}</div><div class="sub">{{ ui.sub }}</div></div>\n'
    '  <div class="badge"{% if demo %} style="background:#f59e0b"{% endif %}>'
    '{% if demo %}{{ ui.badge_demo }}{% else %}{{ ui.badge_blank }}{% endif %}</div>\n'
    '</header>\n'
    '<div class="step-bar" id="step-bar"></div>\n'
    '{% if demo %}<div id="demo-banner" style="background:#fffbeb;border-bottom:2px solid #f59e0b;'
    'padding:8px 28px;display:flex;align-items:center;gap:12px;font-size:.82rem;color:#92400e">\n'
    '  <span style="font-size:1.1rem">&#9888;</span>\n'
    '  <span><strong>{{ ui.demo_banner_lead }}</strong> {{ ui.demo_banner_desc_template'
    '.format(patent_short=demo.banner_short_name, company=demo.patent.company) }}</span>\n'
    '</div>{% endif %}\n'
    '<div id="pages"></div>',
)

add(
    '  <button class="btn btn-prev" id="btn-prev" onclick="navigate(-1)">&#8592; Precedente</button>\n'
    '  <div class="nav-info" id="nav-info"></div>\n'
    '  <button class="btn btn-next" id="btn-next" onclick="navigate(1)">Successivo &#8594;</button>',
    '  <button class="btn btn-prev" id="btn-prev" onclick="navigate(-1)">&#8592; {{ ui.nav_prev }}</button>\n'
    '  <div class="nav-info" id="nav-info"></div>\n'
    '  <button class="btn btn-next" id="btn-next" onclick="navigate(1)">{{ ui.nav_next }} &#8594;</button>',
)

# --- script top ---
add(
    "var STD5 = ['No','In misura ridotta','In qualche misura','In larga misura','In grandissima misura'];",
    "var STD5 = {{ std5_json }};",
)
add("/*QS_ARRAY_MARKER*/", "")  # placeholder, replaced below via regex (QS spans many lines)
add(
    "var SEC_NAMES = {A:'A. Stato Legale',B:'B. Tecnologia',C:'C. Condizioni di Mercato',D:'D. Finanza',E:'E. Strategia'};",
    "var SEC_NAMES = {{ sec_names_json }};",
)

# --- radar labels ---
add(
    "  var labels=['A. Legale','B. Tecnologia','C. Mercato','D. Finanza','E. Strategia'];",
    "  var labels={{ ui.radar_labels|tojson }};",
)

# --- locale ---
add(
    "  return n.toLocaleString('it-IT',{maximumFractionDigits:0});",
    "  return n.toLocaleString('{{ ui.locale }}',{maximumFractionDigits:0});",
)
add(
    "function fmtEur(n){ return n.toLocaleString('it-IT',{style:'currency',currency:'EUR',maximumFractionDigits:0}); }",
    "function fmtEur(n){ return n.toLocaleString('{{ ui.locale }}',{style:'currency',currency:'EUR',maximumFractionDigits:0}); }",
)

# --- interp text tiers ---
add(
    "  if(pct<=40){interpText='Portafoglio IP a rischio elevato — Revisione urgente necessaria';interpColor='var(--red)';}\n"
    "  else if(pct<=60){interpText='Portafoglio IP necessita attenzione — Valutare rafforzamento';interpColor='var(--yellow)';}\n"
    "  else if(pct<=75){interpText='Portafoglio IP in buona salute — Continuare a monitorare';interpColor='#16a34a';}\n"
    "  else{interpText='Portafoglio IP eccellente — Mantenere e valorizzare la strategia';interpColor='#15803d';}",
    "  if(pct<=40){interpText='{{ ui.interp[0].text }}';interpColor='var(--red)';}\n"
    "  else if(pct<=60){interpText='{{ ui.interp[1].text }}';interpColor='var(--yellow)';}\n"
    "  else if(pct<=75){interpText='{{ ui.interp[2].text }}';interpColor='#16a34a';}\n"
    "  else{interpText='{{ ui.interp[3].text }}';interpColor='#15803d';}",
)

# --- VAN table year label ---
add(
    "          +'<td>Anno '+r.y+'</td>'",
    "          +'<td>{{ ui.year_label }} '+r.y+'</td>'",
)

# --- van-sign texts ---
add(
    "    document.getElementById('van-sign').textContent=van.van>=0?'Valore Attuale Netto POSITIVO — il brevetto crea valore economico':'Valore Attuale Netto NEGATIVO — rivedere ipotesi o strategia';",
    "    document.getElementById('van-sign').textContent=van.van>=0?'{{ ui.van_sign_pos }}':'{{ ui.van_sign_neg }}';",
)

# --- next-steps texts ---
add(
    "  if(pct<50) steps+='<div class=\"step-item\"><div class=\"step-icon warn\">!</div><div class=\"step-text\"><strong>IPscore basso ('+pct+'%):</strong> Prioritizzare il miglioramento delle sezioni con punteggi inferiori al 50%.</div></div>';",
    "  if(pct<50) steps+='<div class=\"step-item\"><div class=\"step-icon warn\">!</div><div class=\"step-text\"><strong>{{ ui.low_ipscore_label }} ('+pct+'%):</strong> {{ ui.low_ipscore_text }}</div></div>';",
)
add(
    "    if(p<50) steps+='<div class=\"step-item\"><div class=\"step-icon warn\">▲</div><div class=\"step-text\"><strong>Sezione '+sec+' ('+p+'%):</strong> '+getSuggestion(sec)+'</div></div>';",
    "    if(p<50) steps+='<div class=\"step-item\"><div class=\"step-icon warn\">&#9650;</div><div class=\"step-text\"><strong>{{ ui.section_label }} '+sec+' ('+p+'%):</strong> '+getSuggestion(sec)+'</div></div>';",
)
add(
    "  if(riskPct>60) steps+='<div class=\"step-item\"><div class=\"step-icon warn\">⚠</div><div class=\"step-text\"><strong>Rischio elevato ('+riskPct+'%):</strong> Verificare solidità giuridica, copertura geografica e capacità di enforcement.</div></div>';\n"
    "  if(oppPct>70) steps+='<div class=\"step-item\"><div class=\"step-icon good\">✓</div><div class=\"step-text\"><strong>Alto potenziale di opportunità ('+oppPct+'%):</strong> Valutare accordi di licensing e nuovi mercati geografici.</div></div>';\n"
    "  if(fin.turnover>0 && van.van>0) steps+='<div class=\"step-item\"><div class=\"step-icon good\">€</div><div class=\"step-text\"><strong>VAN positivo ('+fmtEur(van.van)+'):</strong> Il brevetto mostra valore economico. Considerare di aggiornare la perizia IP per il bilancio e per accesso a finanziamenti.</div></div>';\n"
    "  if(fin.turnover>0 && van.van<0) steps+='<div class=\"step-item\"><div class=\"step-icon warn\">€</div><div class=\"step-text\"><strong>VAN negativo:</strong> Rivedere le ipotesi di mercato (crescita, vita attesa, quota settore) o considerare strategie di licensing per generare ricavi da IP senza produzione diretta.</div></div>';\n"
    "  if(!steps) steps='<div class=\"step-item\"><div class=\"step-icon good\">✓</div><div class=\"step-text\">Portafoglio IP solido. Mantenere il monitoraggio e l\\'allineamento con la strategia aziendale.</div></div>';",
    "  if(riskPct>60) steps+='<div class=\"step-item\"><div class=\"step-icon warn\">&#9888;</div><div class=\"step-text\"><strong>{{ ui.risk_label }} ('+riskPct+'%):</strong> {{ ui.risk_text }}</div></div>';\n"
    "  if(oppPct>70) steps+='<div class=\"step-item\"><div class=\"step-icon good\">&#10003;</div><div class=\"step-text\"><strong>{{ ui.opp_label }} ('+oppPct+'%):</strong> {{ ui.opp_text }}</div></div>';\n"
    "  if(fin.turnover>0 && van.van>0) steps+='<div class=\"step-item\"><div class=\"step-icon good\">&euro;</div><div class=\"step-text\"><strong>{{ ui.npv_positive_label }} ('+fmtEur(van.van)+'):</strong> {{ ui.npv_positive_text }}</div></div>';\n"
    "  if(fin.turnover>0 && van.van<0) steps+='<div class=\"step-item\"><div class=\"step-icon warn\">&euro;</div><div class=\"step-text\"><strong>{{ ui.npv_negative_label }}:</strong> {{ ui.npv_negative_text }}</div></div>';\n"
    "  if(!steps) steps='<div class=\"step-item\"><div class=\"step-icon good\">&#10003;</div><div class=\"step-text\">{{ ui.solid_portfolio_text }}</div></div>';",
)

# --- getSuggestion() action plan dict ---
add(
    "  var s={\n"
    "    A:'Rafforzare la posizione legale: ampliare la copertura geografica, completare ricerche di anteriorità e stabilire un processo di monitoraggio delle contraffazioni.',\n"
    "    B:'Accelerare lo sviluppo tecnologico: completare i test di produzione, valutare la riduzione del time-to-market e analizzare la differenziazione rispetto alle tecnologie sostitutive.',\n"
    "    C:'Potenziare la strategia di mercato: condurre un\\'analisi di mercato formale, valutare il pricing premium possibile e identificare canali di commercializzazione alternativi.',\n"
    "    D:'Ottimizzare la struttura finanziaria: ridurre i costi di sviluppo, valutare incentivi fiscali (Patent Box, credito R&S) e pianificare il cash flow per i rinnovi.',\n"
    "    E:'Allineare la strategia IP: integrare il brevetto nella strategia aziendale, considerare accordi di licensing e rafforzare il posizionamento competitivo.'\n"
    "  };\n"
    "  return s[sec]||'Analizzare i fattori chiave e definire un piano d\\'azione.';",
    "  var s={{ action_plan_json }};\n"
    "  return s[sec]||{{ ui.action_plan_fallback|tojson }};",
)

# --- updateNavInfo page names ---
add(
    "  var pageNames=['Brevetto','A: Legale','B: Tecno.','C: Mercato','D: Finanza','E: Strategia','Dati Fin.','Risultati'];\n"
    "  document.getElementById('nav-info').textContent='Passo '+(cur+1)+' di '+NPAGE+' — '+pageNames[cur];",
    "  var pageNames={{ ui.page_names_nav|tojson }};\n"
    "  document.getElementById('nav-info').textContent='{{ ui.nav_step_label|default('Step') }} '+(cur+1)+' {{ ui.nav_of_label|default('of') }} '+NPAGE+' — '+pageNames[cur];",
)
add(
    "      pb.textContent='🖨 Stampa / PDF';",
    "      pb.textContent='{{ ui.print_btn2_text }}';",
)

# --- section score bar + help buttons ---
add(
    "    +'<div class=\"sec-score-bar\">Punteggio: <strong id=\"sscore-'+sec+'\">0</strong> / '+maxPts+'</div>';",
    "    +'<div class=\"sec-score-bar\">{{ ui.score_label|default('Punteggio') }}: <strong id=\"sscore-'+sec+'\">0</strong> / '+maxPts+'</div>';",
)
add(
    "    html+='<button class=\"help-btn\" onclick=\"toggleHelp(\\''+q.id+'\\')\" type=\"button\">&#9432; Informazioni utili</button>';",
    "    html+='<button class=\"help-btn\" onclick=\"toggleHelp(\\''+q.id+'\\')\" type=\"button\">&#9432; {{ ui.help_btn_label }}</button>';",
)

# --- fin_net locale ---
add(
    "  if(el){ el.value=net!==0?Math.round(net).toLocaleString('it-IT'):''; }",
    "  if(el){ el.value=net!==0?Math.round(net).toLocaleString('{{ ui.locale }}'):''; }",
)

# --- intro page ---
add(
    "        +'<h1>IPscore 3.0 — Valutazione Economica del Brevetto</h1>'\n"
    "        +'<p>Strumento sviluppato dall\\'<strong>Ufficio Europeo dei Brevetti (EPO)</strong>. Traduce le caratteristiche tecniche, legali, di mercato e strategiche di un brevetto in un punteggio quantitativo (0–200 punti) e in una stima del Valore Attuale Netto (VAN) attribuibile alla tecnologia brevettata. Versione adattata per il contesto italiano, con riferimenti normativi, fiscali e di mercato aggiornati al 2024–2025.</p>'\n"
    "        +'<div class=\"features-list\">'\n"
    "        +'<div class=\"feat\"><div class=\"feat-icon\">📋</div>40 domande su 5 aree</div>'\n"
    "        +'<div class=\"feat\"><div class=\"feat-icon\">💶</div>Calcolo VAN</div>'\n"
    "        +'<div class=\"feat\"><div class=\"feat-icon\">📊</div>Radar & Risk/Opp</div>'\n"
    "        +'</div>'\n"
    "        +'</div>'\n"
    "        +'<div class=\"page-desc\" style=\"margin-bottom:16px\">Inserire le informazioni identificative del brevetto prima di procedere con la valutazione.</div>'\n"
    "        +'<div class=\"info-grid\">'\n"
    "        +'<div class=\"info-field\" style=\"grid-column:span 2\"><label>Nome/Titolo del Brevetto</label><input type=\"text\" id=\"pat-name\" placeholder=\"Es.: Sistema innovativo per il controllo della qualità in linea\"></div>'\n"
    "        +'<div class=\"info-field\"><label>Numero di Brevetto / Riferimento</label><input type=\"text\" id=\"pat-num\" placeholder=\"Es.: EP3456789 / IT102023000010000\"></div>'\n"
    "        +'<div class=\"info-field\"><label>Azienda / Titolare</label><input type=\"text\" id=\"pat-company\" placeholder=\"Ragione sociale\"></div>'\n"
    "        +'<div class=\"info-field\"><label>Settore Tecnologico</label><input type=\"text\" id=\"pat-sector\" placeholder=\"Es.: Meccanica, Biomedica, ICT, Chimico...\"></div>'\n"
    "        +'<div class=\"info-field\"><label>Data Valutazione</label><input type=\"date\" id=\"pat-date\" value=\"'+new Date().toISOString().split('T')[0]+'\"></div>'\n"
    "        +'<div class=\"info-field\" style=\"grid-column:span 2\"><label>Descrizione sintetica</label><textarea rows=\"3\" id=\"pat-desc\" placeholder=\"Breve descrizione della tecnologia e del prodotto/processo che il brevetto tutela...\"></textarea></div>'\n"
    "        +'</div>';",
    "        +'<h1>{{ ui.intro.h1 }}</h1>'\n"
    "        +'<p>{{ ui.intro.p }}</p>'\n"
    "        +'<div class=\"features-list\">'\n"
    "        +'<div class=\"feat\"><div class=\"feat-icon\">📋</div>{{ ui.intro.feat1 }}</div>'\n"
    "        +'<div class=\"feat\"><div class=\"feat-icon\">💶</div>{{ ui.intro.feat2 }}</div>'\n"
    "        +'<div class=\"feat\"><div class=\"feat-icon\">📊</div>{{ ui.intro.feat3 }}</div>'\n"
    "        +'</div>'\n"
    "        +'</div>'\n"
    "        +'<div class=\"page-desc\" style=\"margin-bottom:16px\">{{ ui.intro.page_desc }}</div>'\n"
    "        +'<div class=\"info-grid\">'\n"
    "        +'<div class=\"info-field\" style=\"grid-column:span 2\"><label>{{ ui.intro.pat_name_label }}</label><input type=\"text\" id=\"pat-name\" placeholder=\"{{ ui.intro.pat_name_placeholder }}\"></div>'\n"
    "        +'<div class=\"info-field\"><label>{{ ui.intro.pat_num_label }}</label><input type=\"text\" id=\"pat-num\" placeholder=\"{{ ui.intro.pat_num_placeholder }}\"></div>'\n"
    "        +'<div class=\"info-field\"><label>{{ ui.intro.pat_company_label }}</label><input type=\"text\" id=\"pat-company\" placeholder=\"{{ ui.intro.pat_company_placeholder|default('') }}\"></div>'\n"
    "        +'<div class=\"info-field\"><label>{{ ui.intro.pat_sector_label }}</label><input type=\"text\" id=\"pat-sector\" placeholder=\"{{ ui.intro.pat_sector_placeholder }}\"></div>'\n"
    "        +'<div class=\"info-field\"><label>{{ ui.intro.pat_date_label }}</label><input type=\"date\" id=\"pat-date\" value=\"'+new Date().toISOString().split('T')[0]+'\"></div>'\n"
    "        +'<div class=\"info-field\" style=\"grid-column:span 2\"><label>{{ ui.intro.pat_desc_label }}</label><textarea rows=\"3\" id=\"pat-desc\" placeholder=\"{{ ui.intro.pat_desc_placeholder }}\"></textarea></div>'\n"
    "        +'</div>';",
)

# --- financial page ---
add(
    "      div.innerHTML='<div class=\"page-title\">Dati Finanziari</div>'\n"
    "        +'<div class=\"page-desc\">Inserire i dati dell\\'ultimo bilancio approvato riferiti all\\'<strong>intera azienda</strong>. I valori vengono usati per calcolare il Valore Attuale Netto (VAN) attribuibile al brevetto.</div>'\n"
    "        +'<div class=\"fin-grid\">'\n"
    "        +finField('fin_turnover','Fatturato Aziendale Totale','€','Fatturato totale annuo dell\\'azienda (voce A1 del Conto Economico riclassificato). <strong>NON</strong> solo del prodotto brevettato — si usa la quota di settore per isolare l\\'area di business rilevante.','number','252000')\n"
    "        +finField('fin_direct','Costi Diretti di Produzione','€','Materie prime, semilavorati, manodopera diretta, servizi di produzione. Per PMI manifatturiere italiane tipicamente 60–75% del fatturato. Corrisponde ai costi delle vendite (COGS).','number','180000')\n"
    "        +finField('fin_indirect','Costi Indiretti (Generali)','€','Affitti, utilities, stipendi admin/marketing/commerciali, assicurazioni, spese generali non attribuibili alla produzione diretta. Tipicamente 10–20% del fatturato.','number','21000')\n"
    "        +finField('fin_depreciation','Ammortamenti Annui','€','Quota annua di ammortamento di impianti, macchinari e attrezzature (non immobili, non ammortamento marchi/brevetti). Fonte: nota integrativa del bilancio.','number','5000')\n"
    "        +'<div class=\"fin-field\"><div class=\"fin-label\">Risultato Netto <span>(calcolato automaticamente)</span></div>'\n"
    "        +'<input class=\"fin-input readonly\" type=\"text\" id=\"fin_net\" readonly placeholder=\"Fatturato − Costi diretti − Indiretti − Amm.ti\"></div>'\n"
    "        +finField('fin_deprecPeriod','Periodo di Ammortamento','anni','Vita utile delle attrezzature produttive in anni. DM 31/12/1988: macchinari industriali 10–15%; impianti meccanici 15–17%. Valori tipici: 5–10 anni per macchinari moderni; 3–5 per elettronica.','number','5')\n"
    "        +finField('fin_sectorShare','Quota Fatturato nel Settore del Brevetto','%','Percentuale del fatturato aziendale relativa all\\'area di business specifica in cui il brevetto opera. Esempio: se il prodotto brevettato vale €150K su €1M totale → inserire 15.','number','15')\n"
    "        +finField('fin_discount','Tasso di Attualizzazione','%','Tasso usato per attualizzare i flussi futuri. Per PMI italiane senza rating: BTP 10Y (≈3,5%) + premio rischio operativo (4–7%) + premio illiquidità (1–2%) ≈ 8–12%. Suggerito default: 10%.','number','10')\n"
    "        +'</div>';",
    "      div.innerHTML='<div class=\"page-title\">{{ ui.fin_page.title }}</div>'\n"
    "        +'<div class=\"page-desc\">{{ ui.fin_page.desc }}</div>'\n"
    "        +'<div class=\"fin-grid\">'\n"
    "        +finField('fin_turnover','{{ ui.fin_page.turnover.label }}','{{ ui.fin_page.turnover.unit }}','{{ ui.fin_page.turnover.help }}','number','{{ ui.fin_page.turnover.default }}')\n"
    "        +finField('fin_direct','{{ ui.fin_page.direct.label }}','{{ ui.fin_page.direct.unit }}','{{ ui.fin_page.direct.help }}','number','{{ ui.fin_page.direct.default }}')\n"
    "        +finField('fin_indirect','{{ ui.fin_page.indirect.label }}','{{ ui.fin_page.indirect.unit }}','{{ ui.fin_page.indirect.help }}','number','{{ ui.fin_page.indirect.default }}')\n"
    "        +finField('fin_depreciation','{{ ui.fin_page.depreciation.label }}','{{ ui.fin_page.depreciation.unit }}','{{ ui.fin_page.depreciation.help }}','number','{{ ui.fin_page.depreciation.default }}')\n"
    "        +'<div class=\"fin-field\"><div class=\"fin-label\">{{ ui.fin_page.net_label }} <span>{{ ui.fin_page.net_sub }}</span></div>'\n"
    "        +'<input class=\"fin-input readonly\" type=\"text\" id=\"fin_net\" readonly placeholder=\"{{ ui.fin_page.net_placeholder }}\"></div>'\n"
    "        +finField('fin_deprecPeriod','{{ ui.fin_page.deprecPeriod.label }}','{{ ui.fin_page.deprecPeriod.unit }}','{{ ui.fin_page.deprecPeriod.help }}','number','{{ ui.fin_page.deprecPeriod.default }}')\n"
    "        +finField('fin_sectorShare','{{ ui.fin_page.sectorShare.label }}','{{ ui.fin_page.sectorShare.unit }}','{{ ui.fin_page.sectorShare.help }}','number','{{ ui.fin_page.sectorShare.default }}')\n"
    "        +finField('fin_discount','{{ ui.fin_page.discount.label }}','{{ ui.fin_page.discount.unit }}','{{ ui.fin_page.discount.help }}','number','{{ ui.fin_page.discount.default }}')\n"
    "        +'</div>';",
)

# --- results page ---
add(
    "      div.innerHTML='<div class=\"page-title\">Risultati IPscore</div>'\n"
    "        +'<div class=\"page-desc\">Riepilogo della valutazione economica del brevetto. Stampare o salvare come PDF per conservare i risultati.</div>'\n"
    "        +'<div class=\"results-grid\">'\n"
    "        +'<div class=\"score-card\"><div style=\"font-size:.85rem;opacity:.8;margin-bottom:4px\">IPscore Totale</div>'\n"
    "        +'<div class=\"score-big\" id=\"r-total\">—</div>'\n"
    "        +'<div class=\"score-sub\" id=\"r-pct\">—</div>'\n"
    "        +'<div class=\"score-interp\" id=\"r-interp\">Completare la valutazione</div></div>'\n"
    "        +'<div class=\"radar-card\"><canvas id=\"radar-canvas\"></canvas></div>'\n"
    "        +'</div>'\n"
    "        +'<div class=\"sec-bars\"><h3>Punteggi per Sezione</h3>'\n"
    "        +SEC_ORDER.map(function(sec){\n"
    "          return '<div class=\"bar-row\"><div class=\"bar-name\">'+SEC_NAMES[sec]+'</div>'\n"
    "            +'<div class=\"bar-track\"><div class=\"bar-fill\" id=\"bar-'+sec+'\" style=\"width:0%;background:var(--border)\"></div></div>'\n"
    "            +'<div class=\"bar-val\" id=\"barval-'+sec+'\">0/'+SEC_MAX[sec]+'</div></div>';\n"
    "        }).join('')\n"
    "        +'</div>'\n"
    "        +'<div class=\"risk-card\"><h3>Profilo Rischio / Opportunità</h3>'\n"
    "        +'<div class=\"risk-row\"><div class=\"risk-label\"><span>Rischio IP</span><span id=\"r-risk-val\">—</span></div>'\n"
    "        +'<div class=\"bar-track\" style=\"height:18px\"><div class=\"bar-fill\" id=\"r-risk-bar\" style=\"width:0%;background:var(--border);height:18px;border-radius:9px\"></div></div></div>'\n"
    "        +'<div class=\"risk-row\"><div class=\"risk-label\"><span>Opportunità IP</span><span id=\"r-opp-val\">—</span></div>'\n"
    "        +'<div class=\"bar-track\" style=\"height:18px\"><div class=\"bar-fill\" id=\"r-opp-bar\" style=\"width:0%;background:var(--green);height:18px;border-radius:9px\"></div></div></div>'\n"
    "        +'<div style=\"font-size:.75rem;color:#64748b;margin-top:8px\">Rischio: 0% = minimo rischio giuridico/tecnologico; 100% = rischio massimo. &nbsp;|&nbsp; Opportunità: 0% = potenziale minimo; 100% = potenziale massimo.</div>'\n"
    "        +'</div>'\n"
    "        +'<div class=\"van-card\"><h3>Valore Attuale Netto (VAN) del Brevetto <span id=\"van-sign\" style=\"font-size:.78rem;font-weight:400;margin-left:8px\"></span></h3>'\n"
    "        +'<div style=\"font-size:.8rem;color:#64748b;margin-bottom:12px\">Flussi di cassa attualizzati attribuibili alla tecnologia brevettata (orizzonte 10 anni).</div>'\n"
    "        +'<table class=\"van-table\"><thead><tr>'\n"
    "        +'<th style=\"text-align:left\">Anno</th><th>Ricavi</th><th>Costi</th><th>Ricavi Recuperati</th><th>Inv. Netto</th><th>Liquidità</th><th>Valore Attuale</th>'\n"
    "        +'</tr></thead><tbody id=\"van-tbody\"><tr><td colspan=\"7\" style=\"text-align:center;color:#94a3b8;padding:20px\">Inserire i dati finanziari nella pagina precedente</td></tr></tbody>'\n"
    "        +'<tfoot><tr class=\"total-row\"><td colspan=\"6\" style=\"text-align:right\">VAN Totale (10 anni)</td><td class=\"van-highlight\" id=\"van-total\">—</td></tr></tfoot>'\n"
    "        +'</table></div>'\n"
    "        +'<div class=\"steps-card\"><h3>Prossimi Passi Raccomandati</h3><div id=\"next-steps\"><div class=\"step-item\"><div class=\"step-icon info\">i</div><div class=\"step-text\">Completare tutte le sezioni per visualizzare le raccomandazioni personalizzate.</div></div></div></div>'\n"
    "        +'<div style=\"text-align:center;margin:20px 0\"><button class=\"btn btn-print\" onclick=\"window.print()\">🖨&nbsp; Stampa / Salva PDF</button></div>';",
    "      div.innerHTML='<div class=\"page-title\">{{ ui.results_page.title }}</div>'\n"
    "        +'<div class=\"page-desc\">{{ ui.results_page.desc }}</div>'\n"
    "        +'<div class=\"results-grid\">'\n"
    "        +'<div class=\"score-card\"><div style=\"font-size:.85rem;opacity:.8;margin-bottom:4px\">{{ ui.results_page.total_ipscore_label }}</div>'\n"
    "        +'<div class=\"score-big\" id=\"r-total\">—</div>'\n"
    "        +'<div class=\"score-sub\" id=\"r-pct\">—</div>'\n"
    "        +'<div class=\"score-interp\" id=\"r-interp\">{{ ui.results_page.complete_assessment_text }}</div></div>'\n"
    "        +'<div class=\"radar-card\"><canvas id=\"radar-canvas\"></canvas></div>'\n"
    "        +'</div>'\n"
    "        +'<div class=\"sec-bars\"><h3>{{ ui.results_page.section_scores_title }}</h3>'\n"
    "        +SEC_ORDER.map(function(sec){\n"
    "          return '<div class=\"bar-row\"><div class=\"bar-name\">'+SEC_NAMES[sec]+'</div>'\n"
    "            +'<div class=\"bar-track\"><div class=\"bar-fill\" id=\"bar-'+sec+'\" style=\"width:0%;background:var(--border)\"></div></div>'\n"
    "            +'<div class=\"bar-val\" id=\"barval-'+sec+'\">0/'+SEC_MAX[sec]+'</div></div>';\n"
    "        }).join('')\n"
    "        +'</div>'\n"
    "        +'<div class=\"risk-card\"><h3>{{ ui.results_page.risk_opp_title }}</h3>'\n"
    "        +'<div class=\"risk-row\"><div class=\"risk-label\"><span>{{ ui.results_page.ip_risk_label }}</span><span id=\"r-risk-val\">—</span></div>'\n"
    "        +'<div class=\"bar-track\" style=\"height:18px\"><div class=\"bar-fill\" id=\"r-risk-bar\" style=\"width:0%;background:var(--border);height:18px;border-radius:9px\"></div></div></div>'\n"
    "        +'<div class=\"risk-row\"><div class=\"risk-label\"><span>{{ ui.results_page.ip_opportunity_label }}</span><span id=\"r-opp-val\">—</span></div>'\n"
    "        +'<div class=\"bar-track\" style=\"height:18px\"><div class=\"bar-fill\" id=\"r-opp-bar\" style=\"width:0%;background:var(--green);height:18px;border-radius:9px\"></div></div></div>'\n"
    "        +'<div style=\"font-size:.75rem;color:#64748b;margin-top:8px\">{{ ui.results_page.risk_opp_footnote }}</div>'\n"
    "        +'</div>'\n"
    "        +'<div class=\"van-card\"><h3>{{ ui.results_page.van_title }} <span id=\"van-sign\" style=\"font-size:.78rem;font-weight:400;margin-left:8px\"></span></h3>'\n"
    "        +'<div style=\"font-size:.8rem;color:#64748b;margin-bottom:12px\">{{ ui.results_page.van_desc }}</div>'\n"
    "        +'<table class=\"van-table\"><thead><tr>'\n"
    "        +'<th style=\"text-align:left\">{{ ui.results_page.van_table_headers[0] }}</th><th>{{ ui.results_page.van_table_headers[1] }}</th><th>{{ ui.results_page.van_table_headers[2] }}</th><th>{{ ui.results_page.van_table_headers[3] }}</th><th>{{ ui.results_page.van_table_headers[4] }}</th><th>{{ ui.results_page.van_table_headers[5] }}</th><th>{{ ui.results_page.van_table_headers[6] }}</th>'\n"
    "        +'</tr></thead><tbody id=\"van-tbody\"><tr><td colspan=\"7\" style=\"text-align:center;color:#94a3b8;padding:20px\">{{ ui.results_page.van_empty_text }}</td></tr></tbody>'\n"
    "        +'<tfoot><tr class=\"total-row\"><td colspan=\"6\" style=\"text-align:right\">{{ ui.results_page.van_total_label }}</td><td class=\"van-highlight\" id=\"van-total\">—</td></tr></tfoot>'\n"
    "        +'</table></div>'\n"
    "        +'<div class=\"steps-card\"><h3>{{ ui.results_page.next_steps_title }}</h3><div id=\"next-steps\"><div class=\"step-item\"><div class=\"step-icon info\">i</div><div class=\"step-text\">{{ ui.results_page.next_steps_placeholder }}</div></div></div></div>'\n"
    "        +'<div style=\"text-align:center;margin:20px 0\"><button class=\"btn btn-print\" onclick=\"window.print()\">{{ ui.results_page.print_btn_text }}</button></div>';",
)

# --- finField() help button label ---
add(
    "    +'<button class=\"help-btn\" onclick=\"toggleHelp(\\'fin_'+id+'\\')\" type=\"button\" style=\"margin-top:6px\">&#9432; Guida alla compilazione</button>'",
    "    +'<button class=\"help-btn\" onclick=\"toggleHelp(\\'fin_'+id+'\\')\" type=\"button\" style=\"margin-top:6px\">&#9432; {{ ui.fin_help_btn_label }}</button>'",
)

# --- step bar names ---
add(
    "  var names=['Brevetto','Sez. A','Sez. B','Sez. C','Sez. D','Sez. E','Finanza','Risultati'];",
    "  var names={{ ui.step_names|tojson }};",
)

# --- end of script: demo block + DOMContentLoaded ---
add(
    "document.addEventListener('DOMContentLoaded', function(){\n"
    "  buildPages();\n"
    "  buildStepBar();\n"
    "  updateNavInfo();\n"
    "});",
    "{% if demo %}\n"
    "function fillDemo(){\n"
    "  document.getElementById('pat-name').value={{ demo.patent.name|tojson }};\n"
    "  document.getElementById('pat-num').value={{ demo.patent.num|tojson }};\n"
    "  document.getElementById('pat-company').value={{ demo.patent.company|tojson }};\n"
    "  document.getElementById('pat-sector').value={{ demo.patent.sector|tojson }};\n"
    "  document.getElementById('pat-date').value={{ demo.patent.date|tojson }};\n"
    "  document.getElementById('pat-desc').value={{ demo.patent.desc|tojson }};\n"
    "\n"
    "  var scores={{ demo.scores|tojson }};\n"
    "  Object.keys(scores).forEach(function(qid){\n"
    "    var val=scores[qid];\n"
    "    var radio=document.querySelector('input[name=\"q_'+qid+'\"][value=\"'+val+'\"]');\n"
    "    if(radio){radio.checked=true; onRadio(qid,val);}\n"
    "  });\n"
    "\n"
    "  document.getElementById('fin_turnover').value={{ demo.financials.turnover }};\n"
    "  document.getElementById('fin_direct').value={{ demo.financials.direct }};\n"
    "  document.getElementById('fin_indirect').value={{ demo.financials.indirect }};\n"
    "  document.getElementById('fin_depreciation').value={{ demo.financials.depreciation }};\n"
    "  document.getElementById('fin_deprecPeriod').value={{ demo.financials.deprecPeriod }};\n"
    "  document.getElementById('fin_sectorShare').value={{ demo.financials.sectorShare }};\n"
    "  document.getElementById('fin_discount').value={{ demo.financials.discount }};\n"
    "  updateNetResult();\n"
    "\n"
    "  var dots=document.querySelectorAll('.step-dot');\n"
    "  var seps=document.querySelectorAll('.step-sep');\n"
    "  for(var i=0;i<NPAGE-1;i++){\n"
    "    if(dots[i]){dots[i].classList.remove('active');dots[i].classList.add('done');}\n"
    "    if(seps[i]) seps[i].classList.add('done');\n"
    "  }\n"
    "  goToPage(7);\n"
    "}\n"
    "{% endif %}\n"
    "\n"
    "document.addEventListener('DOMContentLoaded', function(){\n"
    "  buildPages();\n"
    "  buildStepBar();\n"
    "  updateNavInfo();\n"
    "  {% if demo %}fillDemo();{% endif %}\n"
    "});",
)

# Apply QS array replacement first (span-based, not literal-unique)
qs_start = html.index("var QS = [")
qs_end = html.index("\n];\n", qs_start) + 4
html = html[:qs_start] + "var QS = {{ qs_json }};\n\n" + html[qs_end:]

errors = []
for old, new in replacements:
    if old == "/*QS_ARRAY_MARKER*/":
        continue
    n = html.count(old)
    if n != 1:
        errors.append((n, old[:80].replace("\n", "\\n")))
        continue
    html = html.replace(old, new, 1)

if errors:
    print("ERRORS -- these substitutions did not match exactly once:", file=sys.stderr)
    for n, old in errors:
        print(f"  count={n}: {old!r}", file=sys.stderr)
    sys.exit(1)

# --- jsq-escape every ui./demo. interpolation inside <script> (i.e. after the
# opening <script> tag) that isn't already going through |tojson or .format(...).
# These sit inside single-quoted JS string literals in buildPages()/updateResults();
# an unescaped apostrophe in the injected text (very common in Italian: "dell'azienda",
# "un'analisi") truncates the JS string and silently kills the whole <script> block --
# exactly the class of bug BUILD_LOG.md's Bug 2 documents. This mirrors the
# uniqueness-checked-substitution philosophy above: mechanical and total, not
# spot-fixed wherever an apostrophe happened to be noticed.
script_start = html.index("<script>")
head, body = html[:script_start], html[script_start:]
placeholder_pattern = re.compile(r'\{\{\s*((?:ui|demo)\.[^}]*?)\s*\}\}')


def _jsq_wrap(m):
    expr = m.group(1)
    if "tojson" in expr or ".format(" in expr:
        return m.group(0)
    return "{{ " + expr + "|jsq }}"


body, n_jsq = placeholder_pattern.subn(_jsq_wrap, body)
html = head + body

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Wrote {OUT} ({len(html)} bytes), {len(replacements)} substitutions applied, "
      f"{n_jsq} expressions jsq-escaped.")
