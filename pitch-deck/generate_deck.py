from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pypdf import PdfWriter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pitch-deck" / "rendered"
IMAGES = ROOT / "demo" / "images"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1600, 900
NAVY = "#071C2C"
NAVY_2 = "#0C2B3D"
TEAL = "#19C1B5"
MINT = "#A5F3E9"
INK = "#142A38"
MUTED = "#59707D"
PALE = "#EAF4F3"
WHITE = "#FFFFFF"
ORANGE = "#FFB454"
RED = "#F27C7C"

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)

def canvas(dark=False):
    im = Image.new("RGB", (W, H), NAVY if dark else WHITE)
    d = ImageDraw.Draw(im)
    return im, d

def rounded(d, box, fill, radius=24, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def wrap(text, f, max_w):
    words = text.split()
    lines, line = [], ""
    for word in words:
        attempt = (line + " " + word).strip()
        if ImageDraw.Draw(Image.new("RGB", (1,1))).textlength(attempt, font=f) <= max_w:
            line = attempt
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    return lines

def text(d, x, y, value, size=30, color=INK, bold=False, max_w=None, leading=1.25):
    f = font(size, bold)
    lines = wrap(value, f, max_w) if max_w else value.split("\n")
    step = int(size * leading)
    for line in lines:
        d.text((x, y), line, fill=color, font=f)
        y += step
    return y

def title(d, kicker, heading, sub=None, dark=False):
    fg = WHITE if dark else INK
    muted = MINT if dark else TEAL
    text(d, 82, 54, kicker.upper(), 16, muted, True)
    y = text(d, 82, 84, heading, 43, fg, True, 1120, 1.1)
    if sub:
        text(d, 82, y + 14, sub, 20, "#C6D6DA" if dark else MUTED, False, 1120)

def footer(d, n, dark=False):
    fg = "#A8C1C8" if dark else "#8AA0A8"
    d.line((82, 852, 1518, 852), fill="#31505D" if dark else "#D7E5E7", width=2)
    text(d, 82, 866, "CLEARSPEND  |  SYNTHETIC-DATA MVP", 13, fg, True)
    text(d, 1490, 866, f"{n:02d}", 13, fg, True)

def fit_image(path, box):
    src = Image.open(path).convert("RGB")
    x1, y1, x2, y2 = box
    bw, bh = x2-x1, y2-y1
    scale = max(bw/src.width, bh/src.height)
    size = (int(src.width*scale), int(src.height*scale))
    src = src.resize(size, Image.Resampling.LANCZOS)
    left, top = (src.width-bw)//2, (src.height-bh)//2
    return src.crop((left, top, left+bw, top+bh))

def screenshot(im, path, box, radius=18):
    shot = fit_image(path, box)
    x1,y1,x2,y2 = box
    mask = Image.new("L", (x2-x1,y2-y1), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,x2-x1,y2-y1), radius, fill=255)
    im.paste(shot, (x1,y1), mask)
    ImageDraw.Draw(im).rounded_rectangle(box, radius=radius, outline="#B7CBCC", width=2)

def card(d, x, y, w, h, heading, body, accent=TEAL, dark=False):
    fill = "#12384A" if dark else "#F4F9F9"
    rounded(d, (x,y,x+w,y+h), fill, 22)
    d.rectangle((x,y,x+7,y+h), fill=accent)
    text(d, x+28, y+24, heading, 22, WHITE if dark else INK, True, w-52)
    text(d, x+28, y+64, body, 17, "#C4D6D9" if dark else MUTED, False, w-52, 1.3)

def save(im, number):
    path = OUT / f"{number:02d}.png"
    im.save(path, quality=96)
    return path

# 1
im,d=canvas(True)
# subtle panels
rounded(d,(0,0,W,H),NAVY,0)
d.ellipse((1030,-220,1740,500), fill="#0E5260")
d.ellipse((1160,-90,1660,410), fill="#13716F")
text(d,82,80,"CLEARSPEND",18,MINT,True)
text(d,82,130,"Faster reimbursement review.",52,WHITE,True,720,1.08)
text(d,82,247,"Human-owned decisions.",52,MINT,True,720,1.08)
text(d,82,355,"Turn the receipts from one business trip into one reviewable, explainable approval—and an accountant-ready handoff.",24,"#D1E4E6",False,650,1.35)
rounded(d,(82,535,588,592),TEAL,28)
text(d,106,550,"Evidence organized. Authority retained.",17,NAVY,True)
screenshot(im, IMAGES/"assets3.png", (805,126,1518,720), 22)
text(d,805,750,"A single report with verified, line-level receipt evidence.",19,"#D1E4E6",False,700)
footer(d,1,True); save(im,1)

# 2
im,d=canvas(); title(d,"Customer problem","Reimbursement review is an evidence-reconstruction job.","Qualitative discovery indicates reviewers and submitters repeatedly reconnect receipts, policy context, and decision history.")
card(d,82,276,410,300,"Receipts live apart","Reviewers download, search for, or request receipt evidence across tools.",ORANGE)
card(d,595,276,410,300,"Policy context is detached","The rule, its evidence, and the decision are not always visible in one review surface.",TEAL)
card(d,1108,276,410,300,"Missing evidence restarts work","A missing receipt can trigger avoidable back-and-forth instead of continuing the same case.",RED)
text(d,82,646,"What this evidence does not prove",18,TEAL,True)
text(d,82,682,"It does not establish quantified time savings, willingness to pay, or market size. Those are the next discovery gates.",23,INK,False,1300)
footer(d,2); save(im,2)

# 3
im,d=canvas(True); title(d,"Product insight","Automate evidence assembly—not financial authority.","ClearSpend separates reproducible policy checks, bounded AI assistance, and the human decision.",True)
for x,label,body,col in [(82,"1  Deterministic checks","Receipt, policy, amount, date, and matching checks run first.",TEAL),(582,"2  Bounded AI advice","AI only helps with unresolved ambiguity. It cannot approve, export, or move money.",ORANGE),(1082,"3  Human decision","A finance reviewer approves, rejects, or requests information and owns the final state.",MINT)]:
    rounded(d,(x,315,x+390,590),"#10384A",24)
    d.ellipse((x+28,342,x+76,390),fill=col)
    text(d,x+95,346,label,21,WHITE,True,260)
    text(d,x+28,432,body,18,"#C9DCE0",False,330,1.35)
text(d,82,679,"Design boundary: ClearSpend is decision support for reimbursement review, not autonomous approval or payment execution.",24,MINT,True,1360)
footer(d,3,True); save(im,3)

# 4
im,d=canvas(); title(d,"Employee workflow","Submit one trip—not disconnected receipts.","Employees select one shared category and purpose, upload up to 20 receipts, then verify extracted details line by line.")
screenshot(im,IMAGES/"assets1.png",(82,250,748,660),18)
screenshot(im,IMAGES/"assets2.png",(790,250,1518,660),18)
text(d,82,696,"1. Upload a same-category receipt bundle",20,INK,True)
text(d,790,696,"2. Confirm merchant, date, and amount",20,INK,True)
text(d,82,733,"Receipt bytes are quarantined, malware-scanned, and then parsed; extraction is proposed evidence, not silent truth.",19,MUTED,False,1360)
footer(d,4); save(im,4)

# 5
im,d=canvas(True); title(d,"A complete evidence packet","One approval boundary. Line-level proof.","The server derives the aggregate total; every receipt remains individually visible and checked.",True)
screenshot(im,IMAGES/"assets3.png",(82,240,940,737),22)
card(d,1080,273,355,135,"One report","Up to 20 same-category receipt lines become one reviewable case.",TEAL,True)
card(d,1080,437,355,135,"No silent rewrite","New evidence is appended; prior receipt revisions remain inspectable.",ORANGE,True)
card(d,1080,601,355,135,"Derived total","The client cannot assert a different aggregate than its verified lines.",MINT,True)
footer(d,5,True); save(im,5)

# 6
im,d=canvas(); title(d,"Reviewer workflow","A recommendation is visible—but never the decision.","Reviewers see deterministic evidence, cited policy, and bounded AI advice before taking a human action.")
screenshot(im,IMAGES/"assets5.png",(82,242,785,680),20)
screenshot(im,IMAGES/"assets6.png",(816,242,1518,680),20)
text(d,82,715,"Checks and citations",20,INK,True)
text(d,816,715,"Approve, reject, or request information",20,INK,True)
text(d,82,751,"A request for information keeps the case open so the employee can append the missing evidence rather than restart the report.",18,MUTED,False,1350)
footer(d,6); save(im,6)

# 7
im,d=canvas(); title(d,"After approval","Accounting handoff with a traceable record.","ClearSpend produces an accountant-ready CSV only after a reviewer confirms coding; it does not execute payment.")
screenshot(im,IMAGES/"assets7.png",(82,242,785,670),20)
screenshot(im,IMAGES/"assets8.png",(816,242,1518,670),20)
text(d,82,708,"Human-confirmed coding and line-level CSV",19,INK,True)
text(d,816,708,"Operating signals and hash-linked audit events",19,INK,True)
text(d,82,748,"“Exported” means CSV generated—not ERP acceptance, reimbursement payment, or book close.",18,MUTED,False,1360)
footer(d,7); save(im,7)

# 8
im,d=canvas(True); title(d,"Trust by design—within the MVP boundary","Controls make the workflow inspectable; they do not turn this into a production payments platform.",None,True)
text(d,82,243,"Implemented for the synthetic MVP",19,MINT,True)
text(d,822,243,"Explicit boundary and next gate",19,ORANGE,True)
items_left=["Encrypted quarantine and fail-closed malware scan before parsing","Receipt evidence revisions, policy pinning, deterministic-first checks","Reviewer-owned decisions, CSV export record, hash-linked audit trail"]
items_right=["No banking, card, payment, or ERP connection","Demo identities are not production authentication; live use needs OIDC/MFA and hardened access controls","Customer validation, OCR accuracy, and live-model quality remain unproven"]
for i,item in enumerate(items_left): card(d,82,285+i*145,620,112,"",item,TEAL,True)
for i,item in enumerate(items_right): card(d,822,285+i*145,620,112,"",item,ORANGE,True)
text(d,82,755,"Discovery boundary: use only synthetic or customer-created de-identified cases until the required pilot security controls are accepted.",20,"#D4E5E7",False,1320)
footer(d,8,True); save(im,8)

# 9
im,d=canvas(); title(d,"Initial beachhead and alternatives","A focused workflow for INR-only, multi-receipt reimbursement review.","Initial hypothesis: India-based finance teams still managing receipt-based claims through email, spreadsheets, tickets, or generic expense forms.")
card(d,82,280,425,310,"Current workaround","Evidence distributed across inboxes, attachments, spreadsheets, tickets, and policy documents.",ORANGE)
card(d,588,280,425,310,"ClearSpend wedge","A human-reviewed evidence packet with policy context, decision trace, and CSV handoff.",TEAL)
card(d,1094,280,425,310,"What it does not replace","ERP, payment, AP, procurement, cards, or an organization’s complete approval hierarchy.",RED)
text(d,82,674,"Positioning",18,TEAL,True)
text(d,82,710,"Start with the narrow task of reaching a defensible reimbursement decision—not a claim to be a full finance platform.",24,INK,False,1320)
footer(d,9); save(im,9)

# 10
im,d=canvas(True); title(d,"Commercial model and current evidence","Paid discovery before scale.","The commercial package and customer-value claims remain hypotheses until the precommitted tests are run.",True)
rounded(d,(82,255,695,667),"#10384A",24)
text(d,120,295,"PAID DESIGN-PARTNER PILOT",17,MINT,True)
text(d,120,340,"INR 25,000",48,WHITE,True)
text(d,120,414,"Paid in advance • 30 calendar days • one organization • up to 10 active reviewers",21,"#D4E5E7",False,510,1.35)
text(d,120,535,"Includes configured reimbursement-policy workflow and CSV accounting handoff.",18,"#D4E5E7",False,510,1.3)
text(d,120,610,"Excludes custom ERP integration, payment execution, SSO, and production-security commitments beyond MVP scope.",16,ORANGE,False,510,1.25)
for y,h,b in [(275,"Engineering evidence","A reproducible synthetic workflow, controls, and risk-path verification."),(420,"Qualitative evidence","Five consent-safe interview summaries; direct product feedback is limited."),(565,"Validation still required","Measured reviewer behavior, decision quality, and paid commitments.")]:
    card(d,790,y,650,112,h,b,TEAL if y==275 else ORANGE if y==420 else RED,True)
text(d,82,741,"No free pilot, verbal interest, or non-binding LOI counts as willingness to pay.",19,MINT,True)
footer(d,10,True); save(im,10)

# 11
im,d=canvas(); title(d,"Evidence-gated roadmap and ask","Validate the wedge before broadening the product.","Feature expansion follows demonstrated workflow value, safety, and paid commitment—not a finance-platform wish list.")
for x,h,b,col in [(82,"NOW","Observe five contextual reviews and run counterbalanced usability tasks. Gate: ≥20% lower median active review time, no error increase.",TEAL),(588,"NEXT","Offer the same paid pilot to five qualified buyers. Gate: ≥2 paid commitments; complete pilot access and data-readiness controls.",ORANGE),(1094,"LATER","Harden the proven workflow, then add one requested integration or variant only when evidence makes it the adoption constraint.",MINT)]:
    rounded(d,(x,278,x+425,560),"#F4F9F9",22)
    d.rectangle((x,y:=278,x+425,y+9),fill=col)
    text(d,x+28,322,h,22,INK,True)
    text(d,x+28,376,b,18,MUTED,False,365,1.35)
rounded(d,(82,642,1518,790),NAVY,24)
text(d,120,678,"THE ASK",17,MINT,True)
text(d,120,713,"Introduce us to finance reviewers and economic buyers willing to test a de-identified reimbursement-review workflow—and, if the evidence clears, become paid design partners.",22,WHITE,False,1300,1.25)
footer(d,11); save(im,11)

# Build PDF from rendered PNGs.
writer = PdfWriter()
for path in sorted(OUT.glob("*.png")):
    pdf_path = path.with_suffix(".pdf")
    Image.open(path).convert("RGB").save(pdf_path, "PDF", resolution=144.0)
    writer.append(str(pdf_path))
with (ROOT / "pitch-deck" / "ClearSpend_Pitch_Deck.pdf").open("wb") as f:
    writer.write(f)
for pdf in OUT.glob("*.pdf"):
    pdf.unlink()
print(f"Created {ROOT / 'pitch-deck' / 'ClearSpend_Pitch_Deck.pdf'}")
