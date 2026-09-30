// Render paper JSON -> .docx (US Letter, Times New Roman 12 pt, 1.5 line spacing, numbered sections, IEEE refs).
const fs = require("fs");
const d = require("docx");
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType,
        ImageRun, BorderStyle, ShadingType, PageNumber, Footer, TabStopType, LevelFormat, PageBreak } = d;

const [,, inPath, outPath] = process.argv;
const P = JSON.parse(fs.readFileSync(inPath, "utf8"));
const FONT = "Times New Roman", SIZE = 24, LINE = 360;   // 12 pt, 1.5 spacing

function runs(text, base = {}) {
  // inline markup: **bold**, *italic*, ^sup^, ~sub~, `code`
  const out = []; const re = /(\*\*[^*]+\*\*|\*[^*]+\*|\^[^^]+\^|~[^~]+~|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, size: base.size || SIZE, ...base }));
    const s = m[0];
    const o = { font: FONT, size: base.size || SIZE, ...base };
    if (s.startsWith("**")) out.push(new TextRun({ ...o, text: s.slice(2, -2), bold: true }));
    else if (s.startsWith("*")) out.push(new TextRun({ ...o, text: s.slice(1, -1), italics: true }));
    else if (s.startsWith("^")) out.push(new TextRun({ ...o, text: s.slice(1, -1), superScript: true }));
    else if (s.startsWith("~")) out.push(new TextRun({ ...o, text: s.slice(1, -1), subScript: true }));
    else out.push(new TextRun({ ...o, text: s.slice(1, -1), font: "Courier New", size: (base.size || SIZE) - 2 }));
    last = m.index + s.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, size: base.size || SIZE, ...base }));
  return out;
}

const children = [];
const para = (text, opt = {}) => new Paragraph({ children: runs(text, opt.run || {}), alignment: opt.align || AlignmentType.JUSTIFIED,
  spacing: { line: opt.line || LINE, after: opt.after ?? 120, before: opt.before || 0 }, indent: opt.indent, keepNext: opt.keepNext,
  numbering: opt.numbering });

// ---- title block
children.push(para(P.meta.title, { align: AlignmentType.CENTER, run: { bold: true, size: 32 }, after: 240, line: 300 }));
for (const l of P.meta.authors) children.push(para(l, { align: AlignmentType.CENTER, after: 40, line: 276 }));
children.push(para("", { after: 120 }));

let fig = 0, tab = 0;
for (const b of P.blocks) {
  if (b.type === "h1" || b.type === "h2" || b.type === "h3") {
    const lvl = { h1: HeadingLevel.HEADING_1, h2: HeadingLevel.HEADING_2, h3: HeadingLevel.HEADING_3 }[b.type];
    const sz = { h1: 28, h2: 26, h3: 24 }[b.type];
    children.push(new Paragraph({ heading: lvl, keepNext: true, spacing: { before: b.type === "h1" ? 300 : 200, after: 120, line: 300 },
      children: [new TextRun({ text: b.text, bold: true, italics: b.type === "h3", font: FONT, size: sz })] }));
  } else if (b.type === "p") {
    children.push(para(b.text, { indent: b.noindent ? undefined : { firstLine: 0 } }));
  } else if (b.type === "abstract") {
    children.push(para("**Abstract.** " + b.text, { indent: { left: 360, right: 360 } }));
  } else if (b.type === "keywords") {
    children.push(para("**Keywords:** " + b.text, { indent: { left: 360, right: 360 }, after: 240 }));
  } else if (b.type === "list") {
    for (const it of b.items) children.push(para(it, { numbering: { reference: b.ordered ? "num" : "bul", level: 0,
      instance: b.instance || 0 }, after: 60 }));
  } else if (b.type === "algo") {
    children.push(para("**" + b.title + "**", { align: AlignmentType.LEFT, keepNext: true, after: 60 }));
    b.lines.forEach((l, i) => children.push(new Paragraph({ spacing: { line: 276, after: 20 }, indent: { left: 360 },
      keepNext: i < b.lines.length - 1, children: runs(l, { size: 21 }) })));
    children.push(para("", { after: 60 }));
  } else if (b.type === "figure") {
    fig += 1;
    const img = fs.readFileSync(b.path); const w = b.width || 6.2;  // inches
    const [pw, ph] = b.px;  // pixel size for aspect ratio
    children.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
      children: [new ImageRun({ type: "png", data: img, transformation: { width: w * 96, height: w * 96 * ph / pw } })] }));
    children.push(para(`**Fig. ${fig}.** ` + b.caption, { align: AlignmentType.JUSTIFIED, run: { size: 21 }, line: 276, after: 200 }));
  } else if (b.type === "table") {
    tab += 1;
    children.push(para(`**Table ${tab}.** ` + b.caption, { align: AlignmentType.LEFT, run: { size: 21 }, line: 276, keepNext: true, after: 80 }));
    const total = 9360; const ws = b.widths || b.header.map(() => 1);
    const sum = ws.reduce((a, c) => a + c, 0); const cw = ws.map(x => Math.floor(total * x / sum));
    cw[cw.length - 1] += total - cw.reduce((a, c) => a + c, 0);
    const fs_ = b.size || 18;
    const border = { style: BorderStyle.SINGLE, size: 4, color: "999999" };
    const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
    const mk = (txt, i, head, rowi) => new TableCell({ width: { size: cw[i], type: WidthType.DXA },
      shading: head ? { type: ShadingType.CLEAR, fill: "EDEDEA", color: "auto" } : (b.highlight && b.highlight.includes(rowi) ?
        { type: ShadingType.CLEAR, fill: "E8F0FB", color: "auto" } : undefined),
      margins: { top: 40, bottom: 40, left: 70, right: 70 },
      borders: { top: head ? border : none, bottom: border, left: none, right: none },
      children: [new Paragraph({ alignment: i === 0 || (b.leftcols || 1) > i ? AlignmentType.LEFT : AlignmentType.CENTER,
        keepNext: rowi < b.rows.length - 1,
        spacing: { line: 240, after: 0 }, children: runs(String(txt), { size: fs_, bold: head }) })] });
    const rows = [new TableRow({ tableHeader: true, children: b.header.map((h, i) => mk(h, i, true, -1)) })];
    b.rows.forEach((r, ri) => rows.push(new TableRow({ cantSplit: true, children: r.map((c, i) => mk(c, i, false, ri)) })));
    children.push(new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: cw, rows }));
    if (b.note) children.push(para(b.note, { run: { size: 18 }, line: 240, after: 200, align: AlignmentType.LEFT }));
    else children.push(para("", { after: 120 }));
  } else if (b.type === "refs") {
    b.items.forEach((r, i) => children.push(new Paragraph({ alignment: AlignmentType.LEFT, spacing: { line: 276, after: 60 },
      indent: { left: 540, hanging: 540 }, children: runs(`[${i + 1}]\t` + r, { size: 21 }),
      tabStops: [{ type: TabStopType.LEFT, position: 540 }] })));
  } else if (b.type === "pagebreak") {
    children.push(new Paragraph({ children: [new PageBreak()] }));
  }
}

const doc = new Document({
  creator: P.meta.creator || "", title: P.meta.title,
  styles: { default: { document: { run: { font: FONT, size: SIZE } } } },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] }] },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 })] })] }) },
    children }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(outPath, buf); console.log("wrote", outPath); });
