#!/usr/bin/env python3
"""
Build build/templates/npv_planner_template.html.j2 out of NPV_Target_Planner_EN.html
by literal, uniqueness-checked substitutions (same method as make_ipscore_template.py).

Unlike IPscore, this tool has no blank/demo split -- both language files always
include the "Load worked example" button -- so the template only takes a `lang`-ish
`ui` dict, plus injected data blocks (OEK_CARDS, QUAL_QUESTIONS, INSIGHTS, PARAM_META,
PARAM_TIPS) so the hand-authored oekCard()/qualCard() calls become data-driven loops
instead of 8+6 literal calls repeated per language.
"""
import re
import sys

SRC = "../NPV_Target_Planner_EN.html"
OUT = "templates/npv_planner_template.html.j2"

with open(SRC, encoding="utf-8") as f:
    html = f.read()

replacements = []


def add(old, new):
    replacements.append((old, new))


# --- head/header ---
add('<html lang="en">', '<html lang="{{ ui.html_lang }}">')
add(
    "<title>IPscore NPV Target Planner — EPO · ASP Adaptation</title>",
    "<title>{{ ui.title }}</title>",
)
add(
    '    <div class="brand">IPscore NPV Target Planner &mdash; EPO Tool &bull; ASP Adaptation</div>\n'
    '    <div class="sub">Work backwards from your target: find what it takes to reach your NPV goal</div>\n'
    "  </div>\n"
    '  <div class="badge">INTERACTIVE PLANNER</div>',
    '    <div class="brand">{{ ui.brand }}</div>\n'
    '    <div class="sub">{{ ui.sub }}</div>\n'
    "  </div>\n"
    '  <div class="badge">{{ ui.badge }}</div>',
)
add(
    '  <span class="lbl">Estimated NPV:</span>\n'
    '  <span class="npv-live" id="npv-live">—</span>\n'
    '  <span class="lbl">&nbsp;|&nbsp; Target:</span>\n'
    '  <span class="npv-tgt" id="npv-tgt">enter setup first</span>\n'
    '  <span class="npv-gap gap-none" id="npv-gap">enter setup</span>',
    '  <span class="lbl">{{ ui.npv_bar.estimated_label }}</span>\n'
    '  <span class="npv-live" id="npv-live">—</span>\n'
    '  <span class="lbl">{{ ui.npv_bar.target_label }}</span>\n'
    '  <span class="npv-tgt" id="npv-tgt">{{ ui.npv_bar.target_placeholder }}</span>\n'
    '  <span class="npv-gap gap-none" id="npv-gap">{{ ui.npv_bar.gap_placeholder }}</span>',
)
add(
    '  <button class="btn btn-prev" id="btn-prev" onclick="navigate(-1)">&#8592; Previous</button>\n'
    '  <div class="nav-info" id="nav-info"></div>\n'
    '  <button class="btn btn-next" id="btn-next" onclick="navigate(1)">Next &#8594;</button>',
    '  <button class="btn btn-prev" id="btn-prev" onclick="navigate(-1)">&#8592; {{ ui.nav_prev }}</button>\n'
    '  <div class="nav-info" id="nav-info"></div>\n'
    '  <button class="btn btn-next" id="btn-next" onclick="navigate(1)">{{ ui.nav_next }} &#8594;</button>',
)

# --- data blocks: INSIGHTS / PARAM_META / PARAM_TIPS become injected JSON ---
insights_start = html.index("var INSIGHTS = {")
insights_end = html.index("\n};\n", insights_start) + 4
html = html[:insights_start] + "var INSIGHTS = {{ insights_json }};\n\n" + html[insights_end:]

meta_start = html.index("var PARAM_META = {")
meta_end = html.index("\n};\n", meta_start) + 4
html = html[:meta_start] + "var PARAM_META = {{ param_meta_json }};\n\n" + html[meta_end:]

tips_start = html.index("var PARAM_TIPS = {")
tips_end = html.index("\n};\n", tips_start) + 4
html = html[:tips_start] + "var PARAM_TIPS = {{ param_tips_json }};\n\n" + html[tips_end:]

# --- OEK_CARDS / QUAL_QUESTIONS: inject as data, right after OEK_VALUES ---
add(
    "var OEK_VALUES = {\n"
    "  B5:[5,2,1,0.5,0], C2:[0.005,0.025,0.05,0.08,0.15], C3:[0.5,1,2,4,8],\n"
    "  C6:[0.005,0.02,0.04,0.06,0.1], D1:[1,0.75,0.5,0.25,0], D2:[0.3,0.15,0.08,0.025,0.005],\n"
    "  D3:[1.3,1.15,1.0,0.85,0.7], D4:[1.2,1.1,1.0,0.7,0.5]\n"
    "};",
    "var OEK_VALUES = {\n"
    "  B5:[5,2,1,0.5,0], C2:[0.005,0.025,0.05,0.08,0.15], C3:[0.5,1,2,4,8],\n"
    "  C6:[0.005,0.02,0.04,0.06,0.1], D1:[1,0.75,0.5,0.25,0], D2:[0.3,0.15,0.08,0.025,0.005],\n"
    "  D3:[1.3,1.15,1.0,0.85,0.7], D4:[1.2,1.1,1.0,0.7,0.5]\n"
    "};\n"
    "var OEK_CARDS = {{ oek_cards_json }};\n"
    "var QUAL_QUESTIONS = {{ qual_questions_json }};",
)

# --- fmtEur locale ---
add(
    "  return n.toLocaleString('en-GB',{style:'currency',currency:'EUR',maximumFractionDigits:0});",
    "  return n.toLocaleString('{{ ui.locale }}',{style:'currency',currency:'EUR',maximumFractionDigits:0});",
)

# --- updateNPVBar texts ---
add(
    "  document.getElementById('npv-tgt').textContent=inputs.bt>0?fmtEur(tgt):'enter setup first';\n"
    "  var gap=document.getElementById('npv-gap');\n"
    "  if(!inputs.bt){gap.textContent='enter setup'; gap.className='npv-gap gap-none'; return;}\n"
    "  var pct=tgt>0?Math.round(npv/tgt*100):0;\n"
    "  if(npv>=tgt){gap.textContent='&#10003; Target reached';gap.className='npv-gap gap-ok';}\n"
    "  else if(pct>=80){gap.textContent='&#9888; '+pct+'% of target';gap.className='npv-gap gap-warn';}\n"
    "  else{gap.textContent='&#10060; '+pct+'% of target';gap.className='npv-gap gap-bad';}",
    "  document.getElementById('npv-tgt').textContent=inputs.bt>0?fmtEur(tgt):{{ ui.npv_bar.target_placeholder|tojson }};\n"
    "  var gap=document.getElementById('npv-gap');\n"
    "  if(!inputs.bt){gap.textContent={{ ui.npv_bar.gap_placeholder|tojson }}; gap.className='npv-gap gap-none'; return;}\n"
    "  var pct=tgt>0?Math.round(npv/tgt*100):0;\n"
    "  if(npv>=tgt){gap.textContent={{ ui.npv_bar.gap_reached|tojson }};gap.className='npv-gap gap-ok';}\n"
    "  else if(pct>=80){gap.textContent='{{ ui.npv_bar.gap_warn_template|jsq }}'.replace('{pct}',pct);gap.className='npv-gap gap-warn';}\n"
    "  else{gap.textContent='{{ ui.npv_bar.gap_bad_template|jsq }}'.replace('{pct}',pct);gap.className='npv-gap gap-bad';}",
)

# --- updateNavInfo / buildStepBar ---
add(
    "  var names=['Setup','Technology','Market','Finance','Legal & Strategy','Results'];\n"
    "  document.getElementById('nav-info').textContent='Step '+(cur+1)+' of '+NPAGE+' — '+names[cur];",
    "  var names={{ ui.nav_page_names|tojson }};\n"
    "  document.getElementById('nav-info').textContent={{ ui.nav_step_label|tojson }}+' '+(cur+1)+' '+{{ ui.nav_of_label|tojson }}+' '+NPAGE+' — '+names[cur];",
)
add(
    "      pb.innerHTML='&#128424; Print / PDF'; pb.onclick=function(){window.print();};",
    "      pb.innerHTML={{ ui.print_btn2_text|tojson }}; pb.onclick=function(){window.print();};",
)
add(
    "  var names=['Setup','Technology','Market','Finance','Legal &amp; Strategy','Results'];",
    "  var names={{ ui.step_bar_names|tojson }};",
)

# --- PAGE 0 (setup) ---
add(
    "    <div class=\"page-title\">&#127919; Set Your Target</div>\n"
    "    <div class=\"page-desc\">Tell us about your company and the NPV you want to achieve. We will guide you through the key factors and show you in real time whether your situation can reach the goal.</div>\n"
    "    <div class=\"setup-grid\">\n"
    "      <div class=\"setup-field\" style=\"grid-column:span 2\">\n"
    "        <label>Total Annual Company Turnover <span class=\"hint\">(entire company, not just the patent area)</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_bt\" placeholder=\"e.g. 8000000\" oninput=\"readSetup();updateNPVBar()\">\n"
    "      </div>\n"
    "      <div class=\"setup-field\">\n"
    "        <label>Your NPV Target <span class=\"hint\">% of turnover</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_tpct\" value=\"15\" min=\"1\" max=\"50\" oninput=\"readSetup();updateNPVBar()\">\n"
    "        <div style=\"font-size:.73rem;color:#64748b;margin-top:6px\">Typical range: 5&ndash;25% of turnover. The higher the target, the more demanding the required patent parameters.</div>\n"
    "      </div>\n"
    "      <div class=\"setup-field\">\n"
    "        <label>Patent Business Area <span class=\"hint\">% of turnover</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_sector\" value=\"30\" min=\"1\" max=\"100\" oninput=\"readSetup();updateNPVBar()\">\n"
    "        <div style=\"font-size:.73rem;color:#64748b;margin-top:6px\">What share of your total revenues comes from the market segment where this patent operates?</div>\n"
    "      </div>\n"
    "      <div class=\"setup-field\">\n"
    "        <label>Operating Costs <span class=\"hint\">% of turnover</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_costs\" value=\"73\" min=\"1\" max=\"99\" oninput=\"readSetup();updateNPVBar()\">\n"
    "        <div style=\"font-size:.73rem;color:#64748b;margin-top:6px\">All running costs (production + overheads) as a percentage of your total turnover. Typical range: 65&ndash;85%.</div>\n"
    "      </div>\n"
    "      <div class=\"setup-field\">\n"
    "        <label>Discount Rate <span class=\"hint\">%</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_discount\" value=\"11\" min=\"1\" max=\"30\" oninput=\"readSetup();updateNPVBar()\">\n"
    "        <div style=\"font-size:.73rem;color:#64748b;margin-top:6px\">Not sure? Use 10% as a safe default. Higher-risk businesses should use 12&ndash;15%.</div>\n"
    "      </div>\n"
    "    </div>\n"
    "    <button class=\"adv-toggle\" onclick=\"document.getElementById('adv').classList.toggle('open');this.textContent=document.getElementById('adv').classList.contains('open')?'&#9650; Hide advanced settings':'&#9660; Advanced settings (depreciation)'\">&#9660; Advanced settings (depreciation)</button>\n"
    "    <div id=\"adv\" class=\"adv-section\">\n"
    "      <div class=\"setup-field\">\n"
    "        <label>Annual Depreciation <span class=\"hint\">% of turnover</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_deprecpct\" value=\"2.5\" step=\"0.1\" oninput=\"readSetup();updateNPVBar()\">\n"
    "      </div>\n"
    "      <div class=\"setup-field\">\n"
    "        <label>Asset Useful Life <span class=\"hint\">years</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_deprecperiod\" value=\"8\" oninput=\"readSetup();updateNPVBar()\">\n"
    "      </div>\n"
    "    </div>\n"
    "    <br>\n"
    "    <button class=\"demo-btn\" onclick=\"fillDemo()\">&#9654; Load worked example (NovaMed Diagnostics Ltd.)</button>",
    "    <div class=\"page-title\">{{ ui.page0.title }}</div>\n"
    "    <div class=\"page-desc\">{{ ui.page0.desc }}</div>\n"
    "    <div class=\"setup-grid\">\n"
    "      <div class=\"setup-field\" style=\"grid-column:span 2\">\n"
    "        <label>{{ ui.page0.bt_label }} <span class=\"hint\">{{ ui.page0.bt_hint }}</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_bt\" placeholder=\"{{ ui.page0.bt_placeholder }}\" oninput=\"readSetup();updateNPVBar()\">\n"
    "      </div>\n"
    "      <div class=\"setup-field\">\n"
    "        <label>{{ ui.page0.tpct_label }} <span class=\"hint\">{{ ui.page0.tpct_hint }}</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_tpct\" value=\"15\" min=\"1\" max=\"50\" oninput=\"readSetup();updateNPVBar()\">\n"
    "        <div style=\"font-size:.73rem;color:#64748b;margin-top:6px\">{{ ui.page0.tpct_note }}</div>\n"
    "      </div>\n"
    "      <div class=\"setup-field\">\n"
    "        <label>{{ ui.page0.sector_label }} <span class=\"hint\">{{ ui.page0.sector_hint }}</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_sector\" value=\"30\" min=\"1\" max=\"100\" oninput=\"readSetup();updateNPVBar()\">\n"
    "        <div style=\"font-size:.73rem;color:#64748b;margin-top:6px\">{{ ui.page0.sector_note }}</div>\n"
    "      </div>\n"
    "      <div class=\"setup-field\">\n"
    "        <label>{{ ui.page0.costs_label }} <span class=\"hint\">{{ ui.page0.costs_hint }}</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_costs\" value=\"73\" min=\"1\" max=\"99\" oninput=\"readSetup();updateNPVBar()\">\n"
    "        <div style=\"font-size:.73rem;color:#64748b;margin-top:6px\">{{ ui.page0.costs_note }}</div>\n"
    "      </div>\n"
    "      <div class=\"setup-field\">\n"
    "        <label>{{ ui.page0.discount_label }} <span class=\"hint\">{{ ui.page0.discount_hint }}</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_discount\" value=\"11\" min=\"1\" max=\"30\" oninput=\"readSetup();updateNPVBar()\">\n"
    "        <div style=\"font-size:.73rem;color:#64748b;margin-top:6px\">{{ ui.page0.discount_note }}</div>\n"
    "      </div>\n"
    "    </div>\n"
    "    <button class=\"adv-toggle\" onclick=\"document.getElementById('adv').classList.toggle('open');this.textContent=document.getElementById('adv').classList.contains('open')?{{ ui.page0.adv_toggle_hide|tojson }}:{{ ui.page0.adv_toggle_open|tojson }}\">{{ ui.page0.adv_toggle_open }}</button>\n"
    "    <div id=\"adv\" class=\"adv-section\">\n"
    "      <div class=\"setup-field\">\n"
    "        <label>{{ ui.page0.deprecpct_label }} <span class=\"hint\">{{ ui.page0.deprecpct_hint }}</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_deprecpct\" value=\"2.5\" step=\"0.1\" oninput=\"readSetup();updateNPVBar()\">\n"
    "      </div>\n"
    "      <div class=\"setup-field\">\n"
    "        <label>{{ ui.page0.deprecperiod_label }} <span class=\"hint\">{{ ui.page0.deprecperiod_hint }}</span></label>\n"
    "        <input class=\"setup-input\" type=\"number\" id=\"s_deprecperiod\" value=\"8\" oninput=\"readSetup();updateNPVBar()\">\n"
    "      </div>\n"
    "    </div>\n"
    "    <br>\n"
    "    <button class=\"demo-btn\" onclick=\"fillDemo()\">{{ ui.page0.demo_btn }}</button>",
)

# --- PAGE 1 (technology) ---
add(
    "    <div class=\"page-title\">&#9200; Technology Window</div>\n"
    "    <div class=\"page-desc\">This is the single most powerful parameter in the entire model. Answer honestly — the rest of the planning depends on it.</div>\n"
    "    ${oekCard('B5','&#9200;','Time to Market','When will your technology be ready to generate sales?',\n"
    "      'Every year of delay before launch means development costs pile up with no revenue to offset them. A technology that can be sold today is worth dramatically more than one that needs 2 or 3 more years of work — even if everything else is identical.',\n"
    "      [\n"
    "        {label:'5+ years away',desc:'We are still in early research or development — launch is far off'},\n"
    "        {label:'About 2 years away',desc:'Significant development work remains before we can launch'},\n"
    "        {label:'About 1 year away',desc:'We expect to be ready to launch within the next 12 months'},\n"
    "        {label:'Around 6 months away',desc:'Final preparations are under way — launch is imminent'},\n"
    "        {label:'Ready now',desc:'The technology is fully developed and we can start selling today'}\n"
    "      ]\n"
    "    )}\n"
    "    <div style=\"background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:16px;font-size:.82rem;color:#1e3a8a;line-height:1.6\">\n"
    "      <strong>&#128161; Why does this matter so much?</strong> The NPV formula adds up cash flows over 10 years, discounting each one back to today. Every year of delay does two things simultaneously: it adds development costs in early years (negative) <em>and</em> delays when positive revenue starts (negative). These two effects compound, making time-to-market the dominant lever in almost every scenario.\n"
    "    </div>",
    "    <div class=\"page-title\">{{ ui.page1.title }}</div>\n"
    "    <div class=\"page-desc\">{{ ui.page1.desc }}</div>\n"
    "    ${OEK_CARDS.filter(function(c){return ['B5'].indexOf(c.id)>=0;}).map(function(c){return oekCard(c.id,c.icon,c.title,c.question,c.context,c.opts);}).join('')}\n"
    "    <div style=\"background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:16px;font-size:.82rem;color:#1e3a8a;line-height:1.6\">\n"
    "      {{ ui.page1.why_box }}\n"
    "    </div>",
)

# --- PAGE 2 (market) ---
add(
    "    <div class=\"page-title\">&#127758; Market Potential</div>\n"
    "    <div class=\"page-desc\">Three questions that define how much revenue your patent can actually generate over its commercial life. Together, these are the primary source of positive value in the model.</div>\n"
    "    ${oekCard('C2','&#128200;','Market Growth Rate','How fast is the market you are entering growing each year?',\n"
    "      'A faster-growing market means that each year you are on the market, your revenue base naturally expands — even before accounting for your own sales efforts.',\n"
    "      [\n"
    "        {label:'Very slow — about 0.5% per year',desc:'A mature or declining market, barely growing'},\n"
    "        {label:'Slow — about 2.5% per year',desc:'Modest growth, roughly in line with general inflation'},\n"
    "        {label:'Moderate — about 5% per year',desc:'Healthy, stable market expanding at a solid pace'},\n"
    "        {label:'Fast — about 8% per year',desc:'A dynamic, expanding sector with strong momentum'},\n"
    "        {label:'Very fast — 15% or more per year',desc:'A high-growth or booming market, rapidly expanding'}\n"
    "      ]\n"
    "    )}\n"
    "    ${oekCard('C3','&#128336;','Competitive Window (Market Lifetime)','Once your product is on the market, how long will you realistically maintain a competitive edge before substitutes or copies arrive?',\n"
    "      'This is how many years of protected or semi-protected revenue you can realistically count on. It may end before the patent expires if competitors find workarounds. Be honest — overestimating this is the most common forecasting mistake.',\n"
    "      [\n"
    "        {label:'About 6 months',desc:'Competitors will react and close in very quickly'},\n"
    "        {label:'About 1 year',desc:'A very short window before substitutes emerge'},\n"
    "        {label:'About 2 years',desc:'Enough time to establish a position, but very tight'},\n"
    "        {label:'About 4 years',desc:'A solid window — enough to grow and recover investment'},\n"
    "        {label:'8 years or more',desc:'Long-lasting advantage with high barriers to imitation'}\n"
    "      ]\n"
    "    )}\n"
    "    ${oekCard('C6','&#128181;','Revenue Uplift','By how much will this patent increase revenues in your business area, compared to operating without it?',\n"
    "      'Think of it as the commercial premium the patent delivers: extra sales from a superior product, higher prices, or new customers you would not otherwise reach.',\n"
    "      [\n"
    "        {label:'Very small — less than 0.5% of sector revenue',desc:'Barely a measurable difference commercially'},\n"
    "        {label:'Small — about 2% of sector revenue',desc:'A modest uplift, visible but not dramatic'},\n"
    "        {label:'Moderate — about 4% of sector revenue',desc:'A meaningful competitive advantage customers notice'},\n"
    "        {label:'Significant — about 6% of sector revenue',desc:'A clear, strong commercial premium driven by the patent'},\n"
    "        {label:'Major — 10% or more of sector revenue',desc:'A dominant advantage — customers pay substantially more or switch to you'}\n"
    "      ]\n"
    "    )}",
    "    <div class=\"page-title\">{{ ui.page2.title }}</div>\n"
    "    <div class=\"page-desc\">{{ ui.page2.desc }}</div>\n"
    "    ${OEK_CARDS.filter(function(c){return ['C2','C3','C6'].indexOf(c.id)>=0;}).map(function(c){return oekCard(c.id,c.icon,c.title,c.question,c.context,c.opts);}).join('')}",
)

# --- PAGE 3 (finance) ---
add(
    "    <div class=\"page-title\">&#128200; Financial Levers</div>\n"
    "    <div class=\"page-desc\">Four questions about costs and investment. These determine how much of the market opportunity actually converts into net value after you account for what you must spend to achieve it.</div>\n"
    "    ${oekCard('D1','&#128274;','Business Dependency','If this patent were taken away today, what fraction of your business could you still run?',\n"
    "      'The more your business depends on this patent, the more revenue it is protecting — and therefore the greater its economic value. A patent that protects a marginal feature of one product is worth far less than one without which the whole business would collapse.',\n"
    "      [\n"
    "        {label:'All of it — the business would carry on completely normally',desc:'The patent does not protect any critical revenue'},\n"
    "        {label:'About three-quarters — we would lose roughly 25% of output',desc:'Some dependency, but most of the business would survive'},\n"
    "        {label:'About half — we would lose roughly 50% of output',desc:'The patent protects a major part of the business'},\n"
    "        {label:'About a quarter — we would lose roughly 75% of output',desc:'The business is highly dependent on this technology'},\n"
    "        {label:'None — the entire business depends on this patent',desc:'Without it, the business cannot operate'}\n"
    "      ]\n"
    "    )}\n"
    "    ${oekCard('D2','&#128295;','Remaining Development Costs','How much more money still needs to be invested in this technology before it is ready to sell?',\n"
    "      'These are the costs you must pay before seeing any revenue — they appear as negative cash flows in the early years and directly reduce your NPV.',\n"
    "      [\n"
    "        {label:'Very high — about 30% of our annual sector revenue',desc:'Enormous remaining investment before launch'},\n"
    "        {label:'High — about 15% of annual sector revenue',desc:'Substantial costs still ahead before commercialisation'},\n"
    "        {label:'Moderate — about 8% of annual sector revenue',desc:'A significant but manageable pre-launch investment'},\n"
    "        {label:'Low — about 2–3% of annual sector revenue',desc:'Small remaining costs — we are nearly ready'},\n"
    "        {label:'Minimal — less than 1% of annual sector revenue',desc:'Virtually done — negligible further development needed'}\n"
    "      ]\n"
    "    )}\n"
    "    ${oekCard('D3','&#9881;&#65039;','Production Cost Effect','Once commercialised, will this technology make your production more expensive or cheaper compared to today?',\n"
    "      'This effect applies every year you operate. A cost saving compounds across the entire revenue period — a cost increase is a persistent drag on margins.',\n"
    "      [\n"
    "        {label:'Much more expensive — production costs rise by about 30%',desc:'A significant ongoing cost penalty each year'},\n"
    "        {label:'Somewhat more expensive — costs rise by about 15%',desc:'A moderate annual cost increase'},\n"
    "        {label:'No change — production costs stay the same',desc:'Neutral — neither saving nor costing more'},\n"
    "        {label:'Somewhat cheaper — production costs fall by about 15%',desc:'A meaningful annual saving on operations'},\n"
    "        {label:'Much cheaper — production costs fall by about 30%',desc:'A major efficiency gain every year of operation'}\n"
    "      ]\n"
    "    )}\n"
    "    ${oekCard('D4','&#127970;','Capital Investment at Launch','To implement this technology commercially, will you need more or less capital equipment than you currently have?',\n"
    "      'This is a one-time cost at the moment of launch. A large additional investment reduces early NPV; needing less capital than today is a positive bonus.',\n"
    "      [\n"
    "        {label:'Significantly more — about 20% more capital than today',desc:'A substantial one-time investment outlay at launch'},\n"
    "        {label:'Slightly more — about 10% more capital than today',desc:'A moderate additional investment at launch'},\n"
    "        {label:'The same — no change in capital requirements',desc:'Neutral — same level of investment as today'},\n"
    "        {label:'Less — about 30% less capital than today',desc:'A meaningful saving in capital at launch'},\n"
    "        {label:'Much less — about 50% less capital than today',desc:'Halving investment requirements — major capital saving'}\n"
    "      ]\n"
    "    )}",
    "    <div class=\"page-title\">{{ ui.page3.title }}</div>\n"
    "    <div class=\"page-desc\">{{ ui.page3.desc }}</div>\n"
    "    ${OEK_CARDS.filter(function(c){return ['D1','D2','D3','D4'].indexOf(c.id)>=0;}).map(function(c){return oekCard(c.id,c.icon,c.title,c.question,c.context,c.opts);}).join('')}",
)

# --- PAGE 4 (legal & strategy) ---
add(
    "    <div class=\"page-title\">&#9878;&#65039; Legal &amp; Strategic Foundation</div>\n"
    "    <div class=\"page-desc\">The NPV you calculated in previous steps only materialises if the patent is well-protected and the company has a plan to exploit it. These six questions assess that foundation.</div>\n"
    "    <div style=\"font-size:.82rem;color:#475569;background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:12px 16px;margin-bottom:18px\">\n"
    "      &#9432; These questions do not change the NPV number — but they tell you how <strong>reliable</strong> that number is in practice.\n"
    "    </div>\n"
    "    ${qualCard('Ag','Is the patent officially granted by a patent office?',[\n"
    "      'Not yet — still pending, or not yet filed',\n"
    "      'Yes, it is granted — but a legal challenge period is still open',\n"
    "      'Yes, fully granted — and no challenges remain'\n"
    "    ])}\n"
    "    ${qualCard('Al','How many years of patent protection do you still have?',[\n"
    "      'Less than 4 years remaining',\n"
    "      'Between 4 and 8 years remaining',\n"
    "      'More than 8 years remaining'\n"
    "    ])}\n"
    "    ${qualCard('Ab','How broadly does the patent protect the technology?',[\n"
    "      'Narrowly — only one very specific form of the product',\n"
    "      'Moderately — competitors would need real effort to work around it',\n"
    "      'Broadly — covers the core principle, very hard to design around'\n"
    "    ])}\n"
    "    ${qualCard('Ac','In how many countries or markets is the patent registered?',[\n"
    "      'Just one country',\n"
    "      'A handful of key markets (around 3&ndash;5 countries)',\n"
    "      'All major relevant markets worldwide'\n"
    "    ])}\n"
    "    ${qualCard('Ec','How central is this patent to what your company does?',[\n"
    "      'Not really central — it supports a side activity',\n"
    "      'Somewhat central — it underpins one important business line',\n"
    "      'Absolutely central — it is a cornerstone of the whole business'\n"
    "    ])}\n"
    "    ${qualCard('Es','Is there a clear commercial plan for how this patent will be used?',[\n"
    "      'No clear plan yet',\n"
    "      'A partial plan exists but is not fully developed',\n"
    "      'Fully integrated into the company\\'s business strategy'\n"
    "    ])}",
    "    <div class=\"page-title\">{{ ui.page4.title }}</div>\n"
    "    <div class=\"page-desc\">{{ ui.page4.desc }}</div>\n"
    "    <div style=\"font-size:.82rem;color:#475569;background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:12px 16px;margin-bottom:18px\">\n"
    "      {{ ui.page4.note }}\n"
    "    </div>\n"
    "    ${QUAL_QUESTIONS.map(function(q){return qualCard(q.id,q.t,q.opts);}).join('')}",
)

# --- PAGE 5 (results) ---
add(
    "    <div class=\"page-title\">&#127942; Your Results</div>\n"
    "    <div class=\"page-desc\">Here is a summary of where your patent stands relative to your NPV target — and what to prioritise.</div>\n"
    "    <div class=\"res-hero\" id=\"res-hero\">\n"
    "      <div class=\"res-npv\">\n"
    "        <div class=\"res-npv-val\" id=\"res-npv-val\">—</div>\n"
    "        <div class=\"res-npv-lbl\">Estimated NPV</div>\n"
    "        <div style=\"font-size:.78rem;margin-top:6px;opacity:.75\" id=\"res-tgt-lbl\">Target: —</div>\n"
    "      </div>\n"
    "      <div class=\"res-bar-wrap\">\n"
    "        <div class=\"res-bar-lbl\" id=\"res-bar-lbl\">Progress towards target</div>\n"
    "        <div class=\"res-bar-track\"><div class=\"res-bar-fill\" id=\"res-bar-fill\" style=\"width:0%\"></div></div>\n"
    "        <div class=\"res-verdict\" id=\"res-verdict\">Complete the previous steps to see your result.</div>\n"
    "      </div>\n"
    "    </div>\n"
    "    <div class=\"param-grid\" id=\"param-grid\"></div>\n"
    "    <div class=\"qual-result-card\" id=\"qual-result\"></div>\n"
    "    <div class=\"actions-card\" id=\"actions-card\">\n"
    "      <h3>&#127919; Your Top Priority Actions</h3>\n"
    "      <div id=\"actions-list\"></div>\n"
    "    </div>\n"
    "    <div style=\"text-align:center;margin:20px 0\">\n"
    "      <button class=\"btn btn-print\" onclick=\"window.print()\">&#128424; Print / Save PDF</button>\n"
    "    </div>",
    "    <div class=\"page-title\">{{ ui.page5.title }}</div>\n"
    "    <div class=\"page-desc\">{{ ui.page5.desc }}</div>\n"
    "    <div class=\"res-hero\" id=\"res-hero\">\n"
    "      <div class=\"res-npv\">\n"
    "        <div class=\"res-npv-val\" id=\"res-npv-val\">—</div>\n"
    "        <div class=\"res-npv-lbl\">{{ ui.page5.estimated_npv_label }}</div>\n"
    "        <div style=\"font-size:.78rem;margin-top:6px;opacity:.75\" id=\"res-tgt-lbl\">{{ ui.page5.target_prefix }}—</div>\n"
    "      </div>\n"
    "      <div class=\"res-bar-wrap\">\n"
    "        <div class=\"res-bar-lbl\" id=\"res-bar-lbl\">{{ ui.page5.progress_label }}</div>\n"
    "        <div class=\"res-bar-track\"><div class=\"res-bar-fill\" id=\"res-bar-fill\" style=\"width:0%\"></div></div>\n"
    "        <div class=\"res-verdict\" id=\"res-verdict\">{{ ui.page5.verdict_placeholder }}</div>\n"
    "      </div>\n"
    "    </div>\n"
    "    <div class=\"param-grid\" id=\"param-grid\"></div>\n"
    "    <div class=\"qual-result-card\" id=\"qual-result\"></div>\n"
    "    <div class=\"actions-card\" id=\"actions-card\">\n"
    "      <h3>{{ ui.page5.actions_title }}</h3>\n"
    "      <div id=\"actions-list\"></div>\n"
    "    </div>\n"
    "    <div style=\"text-align:center;margin:20px 0\">\n"
    "      <button class=\"btn btn-print\" onclick=\"window.print()\">{{ ui.page5.print_btn_text }}</button>\n"
    "    </div>",
)

# --- updateResults() dynamic texts ---
add(
    "  document.getElementById('res-tgt-lbl').textContent='Target: '+(inputs.bt>0?fmtEur(tgt):'—');",
    "  document.getElementById('res-tgt-lbl').textContent={{ ui.results.target_prefix|tojson }}+(inputs.bt>0?fmtEur(tgt):'—');",
)
add(
    "  if(!inputs.bt){verdict='Enter your company turnover and target on the Setup page to see your result.';}\n"
    "  else if(pct>=100){verdict='<strong>&#10003; Target reached.</strong> Your current parameter profile supports an NPV that meets or exceeds your goal. Focus on defending this position — protect the technology, enforce the patent, and execute the commercial plan.';}\n"
    "  else if(pct>=80){verdict='<strong>&#9888; Almost there — '+pct+'% of target.</strong> You are close. One or two focused improvements in your weakest parameters should close the gap. See the priority actions below.';}\n"
    "  else if(pct>=50){verdict='<strong>&#9888; Partway there — '+pct+'% of target.</strong> Several parameters need strengthening. The NPV gap is real but closable. Prioritise the red-flagged items below.';}\n"
    "  else{verdict='<strong>&#10060; Significant gap — '+pct+'% of target.</strong> The current profile falls well short of the goal. Major changes in multiple parameters are required before the patent can justify its commercial target.';}\n"
    "  document.getElementById('res-verdict').innerHTML=verdict;\n"
    "  document.getElementById('res-bar-lbl').textContent='You are at '+pct+'% of your target';",
    "  if(!inputs.bt){verdict={{ ui.results.verdict_no_data|tojson }};}\n"
    "  else if(pct>=100){verdict={{ ui.results.verdict_reached|tojson }};}\n"
    "  else if(pct>=80){verdict='{{ ui.results.verdict_almost_template|jsq }}'.replace('{pct}',pct);}\n"
    "  else if(pct>=50){verdict='{{ ui.results.verdict_partway_template|jsq }}'.replace('{pct}',pct);}\n"
    "  else{verdict='{{ ui.results.verdict_gap_template|jsq }}'.replace('{pct}',pct);}\n"
    "  document.getElementById('res-verdict').innerHTML=verdict;\n"
    "  document.getElementById('res-bar-lbl').textContent='{{ ui.results.bar_pct_template|jsq }}'.replace('{pct}',pct);",
)
add(
    "      +'<span class=\"param-badge '+badgeCls+'\">'+icon+' Score '+score+'</span>'",
    "      +'<span class=\"param-badge '+badgeCls+'\">'+icon+' {{ ui.results.score_label }} '+score+'</span>'",
)
add(
    "  var legalStatus=legalScore>=10?{icon:'&#9989;',color:'#16a34a',label:'Strong legal protection'}:legalScore>=7?{icon:'&#9888;&#65039;',color:'#d97706',label:'Adequate — some gaps'}:{icon:'&#10060;',color:'#dc2626',label:'Needs attention'};\n"
    "  var stratStatus=stratScore>=5?{icon:'&#9989;',color:'#16a34a',label:'Well aligned with strategy'}:stratScore>=4?{icon:'&#9888;&#65039;',color:'#d97706',label:'Partially aligned'}:{icon:'&#10060;',color:'#dc2626',label:'Strategy alignment missing'};\n"
    "  var legalRec=legalScore<7?'Work on patent grant status, remaining life, geographic coverage and claim breadth to build a solid legal foundation that can actually protect the NPV you are targeting.':legalScore<10?'Legal position is adequate but has gaps. Prioritise the weakest legal element (coverage or enforceability) to reduce the risk of losing your competitive window unexpectedly.':'Your legal foundation is solid. Keep monitoring for infringement and reassess coverage every 2&ndash;3 years.';\n"
    "  var stratRec=stratScore<4?'A patent without a clear commercial plan rarely reaches its potential NPV. Define how you will use it: direct sales, licensing, or defensive positioning — and integrate it into your annual business plan.':stratScore<5?'Your strategy is partially in place. Formalise the commercial plan and ensure leadership is committed to deploying the patent actively.':'Excellent strategic alignment. Make sure the plan is reviewed annually and stays connected to business priorities.';\n"
    "  document.getElementById('qual-result').innerHTML='<h3>&#9878;&#65039; Legal &amp; Strategic Foundation</h3>'\n"
    "    +'<div class=\"qual-row\"><div class=\"qual-dot\" style=\"background:'+legalStatus.color+'\"></div><div><strong>Legal protection: '+legalStatus.icon+' '+legalStatus.label+'</strong><br>'+legalRec+'</div></div>'\n"
    "    +'<div class=\"qual-row\"><div class=\"qual-dot\" style=\"background:'+stratStatus.color+'\"></div><div><strong>Strategic alignment: '+stratStatus.icon+' '+stratStatus.label+'</strong><br>'+stratRec+'</div></div>';",
    "  var legalStatus=legalScore>=10?{icon:'&#9989;',color:'#16a34a',label:{{ ui.results.legal_status_strong|tojson }}}:legalScore>=7?{icon:'&#9888;&#65039;',color:'#d97706',label:{{ ui.results.legal_status_adequate|tojson }}}:{icon:'&#10060;',color:'#dc2626',label:{{ ui.results.legal_status_needs_attention|tojson }}};\n"
    "  var stratStatus=stratScore>=5?{icon:'&#9989;',color:'#16a34a',label:{{ ui.results.strat_status_well_aligned|tojson }}}:stratScore>=4?{icon:'&#9888;&#65039;',color:'#d97706',label:{{ ui.results.strat_status_partial|tojson }}}:{icon:'&#10060;',color:'#dc2626',label:{{ ui.results.strat_status_missing|tojson }}};\n"
    "  var legalRec=legalScore<7?{{ ui.results.legal_rec_low|tojson }}:legalScore<10?{{ ui.results.legal_rec_mid|tojson }}:{{ ui.results.legal_rec_high|tojson }};\n"
    "  var stratRec=stratScore<4?{{ ui.results.strat_rec_low|tojson }}:stratScore<5?{{ ui.results.strat_rec_mid|tojson }}:{{ ui.results.strat_rec_high|tojson }};\n"
    "  document.getElementById('qual-result').innerHTML='<h3>{{ ui.results.legal_strategic_title|jsq }}</h3>'\n"
    "    +'<div class=\"qual-row\"><div class=\"qual-dot\" style=\"background:'+legalStatus.color+'\"></div><div><strong>{{ ui.results.legal_protection_prefix|jsq }}'+legalStatus.icon+' '+legalStatus.label+'</strong><br>'+legalRec+'</div></div>'\n"
    "    +'<div class=\"qual-row\"><div class=\"qual-dot\" style=\"background:'+stratStatus.color+'\"></div><div><strong>{{ ui.results.strategic_alignment_prefix|jsq }}'+stratStatus.icon+' '+stratStatus.label+'</strong><br>'+stratRec+'</div></div>';",
)
add(
    "    al.innerHTML='<div class=\"action-item\"><div class=\"action-num\">&#10003;</div><div class=\"action-text\">All key parameters are in the green zone. Maintain the current position, enforce the patent actively, and execute the commercial plan.</div></div>';\n"
    "  } else {\n"
    "    al.innerHTML=actions.map(function(a,i){\n"
    "      return '<div class=\"action-item\"><div class=\"action-num\">'+(i+1)+'</div><div class=\"action-text\"><strong>'+a.name+'</strong> (current score: '+a.score+'): '+a.tip+'</div></div>';",
    "    al.innerHTML='<div class=\"action-item\"><div class=\"action-num\">&#10003;</div><div class=\"action-text\">{{ ui.results.actions_all_green }}</div></div>';\n"
    "  } else {\n"
    "    al.innerHTML=actions.map(function(a,i){\n"
    "      return '<div class=\"action-item\"><div class=\"action-num\">'+(i+1)+'</div><div class=\"action-text\"><strong>'+a.name+'</strong> {{ ui.results.action_score_template|jsq }}'.replace('{score}',a.score)+a.tip+'</div></div>';",
)

# --- fillDemo() ---
add(
    "  document.getElementById('s_bt').value=8000000;\n"
    "  document.getElementById('s_tpct').value=15;\n"
    "  document.getElementById('s_sector').value=30;\n"
    "  document.getElementById('s_costs').value=73;\n"
    "  document.getElementById('s_discount').value=11;\n"
    "  document.getElementById('s_deprecpct').value=2.5;\n"
    "  document.getElementById('s_deprecperiod').value=8;\n"
    "  readSetup();\n"
    "  var ds={B5:3,C2:4,C3:4,C6:3,D1:3,D2:4,D3:3,D4:3};\n"
    "  Object.keys(ds).forEach(function(id){selectOEK(id,ds[id]);});\n"
    "  var dq={Ag:3,Al:3,Ab:2,Ac:2,Ec:3,Es:2};\n"
    "  Object.keys(dq).forEach(function(id){selectQual(id,dq[id]);});\n"
    "  updateNPVBar();\n"
    "  alert('Example loaded: NovaMed Diagnostics Ltd.\\nTurnover: €8M | Target NPV: 15% | Sector share: 30%\\nNavigate through the pages to explore the parameter choices.');",
    "  document.getElementById('s_bt').value={{ demo.inputs.bt }};\n"
    "  document.getElementById('s_tpct').value={{ demo.inputs.targetPct }};\n"
    "  document.getElementById('s_sector').value={{ demo.inputs.sectorShare }};\n"
    "  document.getElementById('s_costs').value={{ demo.inputs.costRatio }};\n"
    "  document.getElementById('s_discount').value={{ demo.inputs.r }};\n"
    "  document.getElementById('s_deprecpct').value={{ demo.inputs.deprecPct }};\n"
    "  document.getElementById('s_deprecperiod').value={{ demo.inputs.deprecPeriod }};\n"
    "  readSetup();\n"
    "  var ds={{ demo.oekScores|tojson }};\n"
    "  Object.keys(ds).forEach(function(id){selectOEK(id,ds[id]);});\n"
    "  var dq={{ demo.qualScores|tojson }};\n"
    "  Object.keys(dq).forEach(function(id){selectQual(id,dq[id]);});\n"
    "  updateNPVBar();\n"
    "  alert({{ demo.alert_text|tojson }});",
)

errors = []
for old, new in replacements:
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

# jsq-escape remaining raw ui./demo. interpolations inside <script> not already tojson'd
script_start = html.index("<script>")
head, body = html[:script_start], html[script_start:]
placeholder_pattern = re.compile(r'\{\{\s*((?:ui|demo)\.[^}]*?)\s*\}\}')


def _jsq_wrap(m):
    expr = m.group(1)
    if "tojson" in expr or "jsq" in expr or ".format(" in expr:
        return m.group(0)
    return "{{ " + expr + "|jsq }}"


body, n_jsq = placeholder_pattern.subn(_jsq_wrap, body)
html = head + body

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Wrote {OUT} ({len(html)} bytes), {len(replacements)} substitutions applied, {n_jsq} extra jsq-escapes.")
