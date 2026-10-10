from werkzeug.utils import secure_filename
from flask import Flask, request, render_template_string, redirect, send_from_directory
from urllib.parse import quote
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "/tmp/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
WHATSAPP = "918423426200"


load_dotenv()
GOOGLE_SHEET_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwpJcYxiIXOcQQheYniuVvTW_lLvdwO9lTjd6nRPmXGxTekn6b5teW2cgrlEOSDKXj__Q/exec"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

def ai_classify(name, mobile, email, query, requested_type=""):
    """Return a small structured classification/summary. Falls back safely if API is unavailable."""
    if not OPENAI_API_KEY:
        return requested_type or "Inquiry", query[:180]
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = (
            "Classify this TipsR Pro customer message. Return exactly two lines: "
            "TYPE: one of Order, Query, Inquiry, Support, Quote\n"
            "SUMMARY: one concise English sentence.\n\n"
            f"Name: {name}\nMobile: {mobile}\nEmail: {email}\n"
            f"Selected type: {requested_type}\nMessage: {query}"
        )
        r = client.responses.create(model=OPENAI_MODEL, input=prompt)
        text = (r.output_text or "").strip()
        typ = requested_type or "Inquiry"
        summary = query[:180]
        for line in text.splitlines():
            if line.upper().startswith("TYPE:"):
                typ = line.split(":",1)[1].strip() or typ
            elif line.upper().startswith("SUMMARY:"):
                summary = line.split(":",1)[1].strip() or summary
        return typ, summary[:500]
    except Exception:
        return requested_type or "Inquiry", query[:180]

def save_to_google_sheet(payload):
    try:
        r = requests.post(GOOGLE_SHEET_WEB_APP_URL, json=payload, timeout=30)
        try:
            result = r.json()
            return bool(r.ok and result.get("success", False))
        except Exception:
            return bool(r.ok)
    except Exception:
        return False


SERVICES = [
    "Custom Tool", "Custom APK / Android App", "Custom Website",
    "Excel Work", "Google Sheets Work", "Data Entry / Data Cleaning",
    "Dashboard / Data Analysis", "Automation", "Other / Something Else"
]

HTML = r"""
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{title}}</title>
<style>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#08111b;color:#eef7f5;font-family:Arial,Helvetica,sans-serif}
a{text-decoration:none;color:inherit}button,input,textarea,select{font:inherit}
.nav{height:76px;padding:0 6%;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #1b3037;background:#08111b;position:sticky;top:0;z-index:20}
.brand{font-size:22px;font-weight:800;display:flex;align-items:center;gap:10px}.logo{display:grid;place-items:center;width:36px;height:36px;border:2px solid #21d89a;border-radius:10px;color:#21d89a}
.navRight{display:flex;align-items:center;gap:18px}.nav nav{display:flex;gap:28px;color:#a9babd;font-size:14px}.nav nav a:hover{color:#21d89a}
.themeBtn{border:1px solid #29434a;background:#101d27;color:#eef7f5;border-radius:999px;padding:9px 14px;cursor:pointer;font-size:13px;font-weight:700}
.themeBtn:hover{border-color:#21d89a;color:#21d89a}
body.light{background:#f5f7f7;color:#17252a}
body.light .nav{background:#fff;border-color:#d7e0e2}
body.light .nav nav{color:#52656a}
body.light .hero{background:radial-gradient(circle at 50% 20%,#d8f2ea 0,transparent 36%),linear-gradient(180deg,#fff,#f5f7f7)}
body.light .hero p{color:#52656a}
body.light .section{background:#eef3f4}
body.light .card{background:#fff;border-color:#d5e0e2;color:#17252a}
body.light .card p,body.light .muted{color:#61757a}
body.light .toolsBox{background:#fff;border-color:#d5e0e2}
body.light .contact{background:#f5f7f7}
body.light footer{border-color:#d7e0e2}
body.light .form{background:#fff;border-color:#d5e0e2}
body.light input,body.light select,body.light textarea{background:#f9fbfb;color:#17252a;border-color:#c9d7da}
body.light .themeBtn{background:#eef3f4;color:#17252a;border-color:#c9d7da}
.hero{min-height:600px;padding:105px 7% 80px;text-align:center;background:radial-gradient(circle at 50% 20%,#173b3a 0,transparent 36%),linear-gradient(180deg,#0b1724,#08111b)}
.eyebrow{color:#21d89a;font-size:12px;font-weight:800;letter-spacing:2px}.hero h1{font-size:clamp(44px,7vw,78px);line-height:1.03;margin:18px auto;max-width:900px}.hero h1 span{color:#21d89a}
.hero p{max-width:760px;margin:0 auto;color:#afc0c4;font-size:18px;line-height:1.7}.actions{display:flex;justify-content:center;gap:14px;margin-top:34px}
.btn{border:0;border-radius:11px;padding:15px 24px;font-weight:800;cursor:pointer;display:inline-flex;justify-content:center;align-items:center}.primary{background:#21d89a;color:#06130e}.secondary{border:1px solid #21d89a;color:#21d89a;background:transparent}
.trust{display:flex;justify-content:center;gap:26px;margin-top:30px;color:#82979b;font-size:13px}
.section,.tools,.contact,.order{padding:90px 7%}.section{background:#0a141e}.sectionHead{display:flex;align-items:end;justify-content:space-between;margin-bottom:34px}
h2{font-size:40px;margin:8px 0}.muted{color:#8fa3a7;line-height:1.6}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.card{background:#101d27;border:1px solid #20363d;color:#fff;padding:26px;border-radius:18px;min-height:170px}.card h3{font-size:21px}.card p{color:#8fa3a7;line-height:1.5}
.toolsBox{display:flex;align-items:center;justify-content:space-between;gap:30px;padding:40px;border-radius:22px;border:1px solid #23434a;background:linear-gradient(120deg,#10242a,#0e1923)}
.contact{text-align:center}.contact p{max-width:620px;margin:0 auto 26px;color:#9cafb2;line-height:1.7}footer{text-align:center;padding:28px;color:#718589;border-top:1px solid #1b3037;font-size:13px}
.order{width:min(900px,100%);margin:auto;padding-top:70px}.orderIntro{text-align:center;max-width:700px;margin:0 auto 40px}
.form{background:#101d27;border:1px solid #20363d;border-radius:22px;padding:34px;display:grid;gap:18px}
label{display:grid;gap:8px;color:#b8c7ca;font-size:13px;font-weight:700}input,select,textarea{width:100%;border:1px solid #29434a;background:#09131c;color:#eef7f5;border-radius:10px;padding:14px;outline:none}
input:focus,select:focus,textarea:focus{border-color:#21d89a}.row{display:grid;grid-template-columns:1fr 1fr;gap:16px}.full{width:100%;margin-top:5px}.notice{text-align:center;color:#718589;font-size:12px}
@media(max-width:800px){.nav{height:auto;padding:16px 5%;gap:12px;flex-wrap:wrap}.navRight{display:flex;align-items:center;gap:10px;flex-wrap:wrap;justify-content:flex-end}.nav nav{gap:12px;flex-wrap:wrap;justify-content:flex-end}.hero{padding:75px 5% 60px}.grid{grid-template-columns:1fr}.section,.tools,.contact{padding:65px 5%}.sectionHead,.toolsBox{display:block}.row{grid-template-columns:1fr}.trust{flex-wrap:wrap}}
@media(max-width:520px){.hero h1{font-size:42px}.actions{flex-direction:column}.btn{width:100%}.trust{flex-direction:column;gap:10px}}
</style></head><body>
<header class="nav"><a class="brand" href="/"><span class="logo">R</span> TipsR Pro</a>
<div class="navRight"><nav><a href="/">Home</a><a href="/#services">Services</a><a href="/#tools">Ranveer Tools</a><a href="/contact">Contact</a></nav>
<button class="themeBtn" id="themeBtn" type="button">☀ Dark</button></div></header>

{% if page=="home" %}
<section class="hero"><span class="eyebrow">TIPS R PRO • DIGITAL WORK SOLUTIONS</span>
<h1>Tell us your work.<br><span>We build the solution.</span></h1>
<p>Excel, Google Sheets, dashboards, automation and custom tools. Send your requirement directly online.</p>
<div class="actions"><a class="btn primary" href="/start-order">✦ Create Your Order</a><a class="btn secondary" href="https://wa.me/{{whatsapp}}">☎ Contact Now</a></div>
<div class="trust"><span>✓ Custom work</span><span>✓ File upload</span><span>✓ Quote before work</span></div></section>
<section id="services" class="section"><div class="sectionHead"><div><span class="eyebrow">WHAT YOU CAN ORDER</span><h2>Build your own solution</h2></div><a class="btn secondary" href="/start-order">Start an Order →</a></div>
<div class="grid">{% for x in services %}<a class="card" href="/start-order"><span class="eyebrow">0{{loop.index}}</span><h3>{{x}}</h3><p>Open the order page and tell us what you need.</p></a>{% endfor %}</div></section>
<section id="tools" class="tools"><div class="toolsBox"><div><span class="eyebrow">RANVEER TOOLS</span><h2>Ready-made Windows tools</h2><p class="muted">Tools, downloads and future utilities can be added here.</p></div><a class="btn primary" href="/ranveer-tools">Open Ranveer Tools →</a></div></section>
<section id="contact" class="contact"><span class="eyebrow">CONTACT</span><h2>Need something different?</h2><p>Send your requirement or open our full contact page.</p><a class="btn primary" href="/contact">Contact Us →</a></section>
<footer>© 2026 TipsR Pro • Excel & Data Solutions</footer>

{% elif page=="order" %}
<section class="order"><div class="orderIntro"><span class="eyebrow">START AN ORDER</span><h1>Tell us what you need.</h1><p class="muted">Fill in your details, select the work type and describe your requirement.</p></div>
<form class="form" action="/submit-order" method="post" enctype="multipart/form-data">
<div class="row"><label>Name<input name="name" required placeholder="Your full name"></label><label>Mobile Number<input name="mobile" required pattern="[0-9]{10}" placeholder="10-digit mobile number"></label></div>
<label>Email<input name="email" required type="email" placeholder="you@example.com"></label>
<label>What do you need?<select name="work" required><option value="">Select an option</option>{% for x in services %}<option>{{x}}</option>{% endfor %}</select></label>
<label>Tell us about your work<textarea name="details" required rows="7" placeholder="Describe your requirement..."></textarea></label>
<div class="row"><label>Budget (optional)<input name="budget" placeholder="Example: ₹5,000"></label><label>Reference File (optional)<input name="reference_file" type="file" accept=".pdf,.xlsx,.xls,.csv,.doc,.docx"></label></div>
<button class="btn primary full" type="submit">Submit Order →</button><p class="notice">Your request will be saved securely. You will see a confirmation after submission.</p></form></section>
{% elif page=="contact" %}
<section class="order">
<div class="orderIntro"><span class="eyebrow">CONTACT US</span><h1>Let’s talk about your project.</h1><p class="muted">Have a question, need a custom tool, or want a quote? Send your details and we’ll connect with you on WhatsApp.</p></div>
<div class="grid" style="margin-bottom:28px">
<div class="card"><span class="eyebrow">WHATSAPP</span><h3>Chat with us</h3><p>Get a quick response about your requirement.</p><a class="btn primary" href="https://wa.me/{{whatsapp}}">Open WhatsApp →</a></div>
<div class="card"><span class="eyebrow">ORDER</span><h3>Start a project</h3><p>Tell us exactly what you want us to build or do.</p><a class="btn secondary" href="/start-order">Start an Order →</a></div>
<div class="card"><span class="eyebrow">SERVICES</span><h3>Custom work</h3><p>Excel, Google Sheets, automation, websites, apps and tools.</p><a class="btn secondary" href="/#services">View Services →</a></div>
</div>
<form class="form" action="/submit-contact" method="post">
<div class="row"><label>Name<input name="name" required placeholder="Your full name"></label><label>Mobile Number<input name="mobile" required pattern="[0-9]{10}" placeholder="10-digit mobile number"></label></div>
<label>Email<input name="email" type="email" required placeholder="you@example.com"></label>
<label>Subject<select name="subject" required><option value="">Select a subject</option><option>General Enquiry</option><option>Project / Custom Work</option><option>Quote Request</option><option>Technical Support</option><option>Ranveer Tools</option><option>Other</option></select></label>
<label>Message<textarea name="message" required rows="7" placeholder="Write your message..."></textarea></label>
<button class="btn primary full" type="submit">Send Message on WhatsApp →</button>
<p class="notice">WhatsApp: 8423426200</p>
</form>
</section>
{% elif page=="thankyou" %}
<section class="order">
  <div class="orderIntro">
    <span class="eyebrow">THANK YOU</span>
    <h1>Thank you! Your request has been received.</h1>
    <p class="muted">We have received your details. We’ll review your requirement and get back to you soon.</p>{% if reference_file_url %}<p><a class="btn secondary" href="{{ reference_file_url }}" target="_blank" rel="noopener">Open Reference File →</a></p>{% endif %}
    <div class="actions">
      <a class="btn primary" href="/">Back to Home</a>
      <a class="btn secondary" href="/start-order">Submit Another Order</a>
    </div>
  </div>
</section>
{% else %}
<section class="order"><div class="orderIntro"><span class="eyebrow">RANVEER TOOLS</span><h1>Ranveer Tools</h1><p class="muted">Tool downloads can be connected here.</p><a class="btn primary" href="https://wa.me/{{whatsapp}}">WhatsApp for Tool Access →</a></div></section>
{% endif %}<script>
(function(){
  const key="tipsrpro-theme";
  const button=document.getElementById("themeBtn");
  function apply(theme){
    document.body.classList.toggle("light", theme === "light");
    if(button) button.textContent = theme === "light" ? "☾ Light" : "☀ Dark";
  }
  let saved="dark";
  try { saved=localStorage.getItem(key) || "dark"; } catch(e) {}
  apply(saved);
  if(button){
    button.addEventListener("click", function(){
      const next=document.body.classList.contains("light") ? "dark" : "light";
      try { localStorage.setItem(key,next); } catch(e) {}
      apply(next);
    });
  }
})();
</script></body></html>
"""

@app.route("/")
def home():
    return render_template_string(HTML,title="TipsR Pro",page="home",services=SERVICES,whatsapp=WHATSAPP)

@app.route("/start-order")
def order():
    return render_template_string(HTML,title="Start an Order • TipsR Pro",page="order",services=SERVICES,whatsapp=WHATSAPP)

@app.post("/submit-order")
def submit():
    f = request.form
    name = f.get("name", "").strip()
    mobile = f.get("mobile", "").strip()
    email = f.get("email", "").strip()
    work = f.get("work", "").strip()
    details = f.get("details", "").strip()
    budget = f.get("budget", "").strip()

    # Read an optional PDF/Excel reference file and send it to Apps Script.
    # Apps Script stores the file in Google Drive and writes the Drive URL to the Sheet.
    reference_file_name = ""
    reference_file_mime = ""
    reference_file_base64 = ""
    uploaded = request.files.get("reference_file")
    if uploaded and uploaded.filename:
        allowed = {".pdf", ".xlsx", ".xls", ".csv", ".doc", ".docx"}
        original = secure_filename(uploaded.filename)
        ext = os.path.splitext(original)[1].lower()
        if original and ext in allowed:
            raw = uploaded.read()
            if len(raw) <= 12 * 1024 * 1024:
                import base64
                reference_file_name = original
                reference_file_mime = uploaded.mimetype or "application/octet-stream"
                reference_file_base64 = base64.b64encode(raw).decode("ascii")

    typ, summary = ai_classify(name, mobile, email, details, work or "Order")

    save_to_google_sheet({
        "name": name,
        "mobile": mobile,
        "email": email,
        "query": details,              # Tell us about your work
        "type": work,                  # What do you need?
        "budget": budget,              # Budget
        "reference_file": reference_file_name,
        "reference_file_mime": reference_file_mime,
        "reference_file_base64": reference_file_base64,
        "ai_summary": summary,
        "status": "New"
    })

    return redirect("/thank-you")

@app.route("/contact")
def contact():
    return render_template_string(HTML,title="Contact Us • TipsR Pro",page="contact",services=SERVICES,whatsapp=WHATSAPP)

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=False)

@app.route("/thank-you")
def thank_you():
    file_url = request.args.get("file", "")
    return render_template_string(HTML,title="Thank You • TipsR Pro",page="thankyou",services=SERVICES,whatsapp=WHATSAPP,reference_file_url=file_url)

@app.route("/ranveer-tools")
def tools():
    return render_template_string(HTML,title="Ranveer Tools • TipsR Pro",page="tools",services=SERVICES,whatsapp=WHATSAPP)

@app.post("/submit-contact")
def submit_contact():
    f=request.form
    name=f.get('name','')
    mobile=f.get('mobile','')
    email=f.get('email','')
    subject=f.get('subject','Inquiry')
    message=f.get('message','')
    typ, summary = ai_classify(name,mobile,email,message,subject)
    save_to_google_sheet({
        "name": name, "mobile": mobile, "email": email,
        "query": message, "type": typ, "ai_summary": summary, "status": "New"
    })
    text=(f"TipsR Pro Contact Message\n\nName: {name}\nMobile: {mobile}\n"
          f"Email: {email}\nSubject: {subject}\nMessage: {message}")
    return redirect("/thank-you")


if __name__=="__main__":
    app.run(host="0.0.0.0",port=3002,debug=False)
