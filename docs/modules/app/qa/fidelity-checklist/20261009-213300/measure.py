"""One measuring function for the Today screens (S1, S2, and the S1 underneath M1). Runs in the page; returns plain data.
Scratch, read-only on the product. It reads geometry and computed styles only and changes nothing on the page.
"""

MEASURE_JS = r"""
() => {
  const round = (v, d = 2) => Math.round(v * 10 ** d) / 10 ** d;
  const q = (s, r = document) => r.querySelector(s);
  const qa = (s, r = document) => Array.from(r.querySelectorAll(s));
  const R = (el) => { const r = el.getBoundingClientRect();
    return { x: round(r.x), y: round(r.y), w: round(r.width), h: round(r.height), r: round(r.right), b: round(r.bottom) }; };
  const C = (el, p, ps) => getComputedStyle(el, ps).getPropertyValue(p);
  const T = (el) => (el.textContent || "").trim();
  const A = (el) => Object.fromEntries(Array.from(el.attributes).map((a) => [a.name, a.value]));
  const cvs = document.createElement("canvas").getContext("2d");
  function baseline(el) {
    const cs = getComputedStyle(el);
    cvs.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    const m = cvs.measureText("Hg");
    const lh = parseFloat(cs.lineHeight);
    return round(el.getBoundingClientRect().top + (lh - (m.fontBoundingBoxAscent + m.fontBoundingBoxDescent)) / 2 + m.fontBoundingBoxAscent);
  }
  const font = (el) => ({ size: C(el, "font-size"), lh: C(el, "line-height"), weight: C(el, "font-weight"), color: C(el, "color"),
    ls: C(el, "letter-spacing"), align: C(el, "text-align"), tabular: C(el, "font-variant-numeric") });
  const out = {};

  const rootStyle = getComputedStyle(document.documentElement);
  out.tokens = { todayRing: rootStyle.getPropertyValue("--today-ring").trim(), dotRing: rootStyle.getPropertyValue("--dot-ring").trim() };

  const body = document.body;
  out.body = { bg: C(body, "background-color"), color: C(body, "color"), family: C(body, "font-family"), size: C(body, "font-size"),
    lh: C(body, "line-height"), weight: C(body, "font-weight"), margin: C(body, "margin") };

  const sprite = q("body > svg");
  out.sprite = sprite ? { rect: R(sprite), position: C(sprite, "position"), attrs: A(sprite),
    symbols: qa("symbol", sprite).map((s) => ({ id: s.id, viewBox: s.getAttribute("viewBox"), d: s.querySelector("path").getAttribute("d") })) } : null;
  out.visibleSvgs = qa("svg").filter((s) => { const r = s.getBoundingClientRect(); const cs = getComputedStyle(s);
    return r.width > 0 && r.height > 0 && cs.display !== "none" && cs.visibility !== "hidden"; }).length;

  const page = q(".page");
  out.page = { rect: R(page), maxWidth: C(page, "max-width"), padding: C(page, "padding"), margin: C(page, "margin-left") };
  const header = q("header.top");
  out.header = { rect: R(header), display: C(header, "display"), alignItems: C(header, "align-items"), justify: C(header, "justify-content"),
    gap: C(header, "gap"), paddingBottom: C(header, "padding-bottom") };
  const brand = q("h1.brand"), date = q("p.date"), time = q("p.date > time");
  out.brand = { tag: brand.tagName, text: T(brand), rect: R(brand), font: font(brand), baseline: baseline(brand) };
  out.date = { tag: date.tagName, text: T(date), rect: R(date), font: font(date), baseline: baseline(date), timeTag: time ? time.tagName : null,
    datetime: time ? time.getAttribute("datetime") : null, timeText: time ? T(time) : null };

  const layout = q("main.layout"), colMain = q(".col-main"), heat = q("section.heat");
  out.layout = { rect: R(layout), display: C(layout, "display"), cols: C(layout, "grid-template-columns"), colGap: C(layout, "column-gap"),
    alignItems: C(layout, "align-items"), colMain: R(colMain), heat: R(heat) };

  const h2 = q("#habits-title");
  out.hiddenHeading = { tag: h2.tagName, cls: h2.className, text: T(h2), rect: R(h2), position: C(h2, "position"), overflow: C(h2, "overflow"),
    clip: C(h2, "clip"), sectionTag: h2.parentElement.tagName, sectionLabelledby: h2.parentElement.getAttribute("aria-labelledby") };

  const ul = q("ul.habits");
  out.list = ul ? { rect: R(ul), listStyle: C(ul, "list-style-type"), padding: C(ul, "padding"), margin: C(ul, "margin"), display: C(ul, "display"),
    rowGap: C(ul, "row-gap"), rows: qa(":scope > li", ul).map(R) } : null;

  const dayInfo = (d) => {
    const wd = q(".wd", d), dm = q(".dm", d), slot = q(".slot", d), bead = q(".bead", d), svg = q("svg", bead), use = q("use", svg);
    const ps = (sel) => { const cs = getComputedStyle(slot, sel);
      return { display: cs.display, height: cs.height, marginTop: cs.marginTop, top: cs.top, left: cs.left, right: cs.right, width: cs.width,
        bgImage: cs.backgroundImage, bgColor: cs.backgroundColor, bgSize: cs.backgroundSize, bgPos: cs.backgroundPosition, bgRepeat: cs.backgroundRepeat }; };
    return { date: d.getAttribute("data-date"), pressed: d.getAttribute("aria-pressed"), current: d.getAttribute("aria-current"),
      label: d.getAttribute("aria-label"), type: d.getAttribute("type"), rect: R(d), padding: C(d, "padding"), gap: C(d, "gap"),
      radius: C(d, "border-radius"), bgColor: C(d, "background-color"),
      wd: { text: T(wd), ...font(wd) }, dm: { text: T(dm), ...font(dm) }, slot: R(slot), bead: R(bead),
      beadBorder: `${C(bead, "border-top-width")} ${C(bead, "border-top-style")} ${C(bead, "border-top-color")}`, beadBg: C(bead, "background-color"),
      beadShadow: C(bead, "box-shadow"), beadRadius: C(bead, "border-radius"),
      check: { rect: R(svg), opacity: C(svg, "opacity"), fill: C(svg, "fill"), transform: C(svg, "transform"), href: use.getAttribute("href") },
      before: ps("::before"), after: ps("::after") };
  };

  out.rows = qa("ul.habits > li").map((li) => {
    const head = q(".habit-head", li), name = q(".habit-name", li), btn = q(".icon-btn", li), svg = q("svg", btn), use = q("use", svg);
    const streak = q(".streak", li), cur = q(".cur", streak), best = q(".best", streak), strip = q(".strip", li);
    return {
      li: R(li), head: R(head),
      name: { tag: name.tagName, id: name.id, text: T(name), rect: R(name), paddingTop: C(name, "padding-top"), wrap: C(name, "overflow-wrap"), ...font(name) },
      btn: { rect: R(btn), label: btn.getAttribute("aria-label"), type: btn.getAttribute("type"), radius: C(btn, "border-radius"), bg: C(btn, "background-color"),
        color: C(btn, "color"), display: C(btn, "display"), svg: R(svg), svgFill: C(svg, "fill"), href: use.getAttribute("href"), cursor: C(btn, "cursor") },
      streak: { rect: R(streak), live: streak.getAttribute("aria-live"), tabular: C(streak, "font-variant-numeric"), gap: C(streak, "gap"),
        cur: { text: T(cur), cls: cur.className, rect: R(cur), ...font(cur) },
        best: best ? { text: T(best), cls: best.className, rect: R(best), ...font(best) } : null },
      strip: { rect: R(strip), role: strip.getAttribute("role"), labelledby: strip.getAttribute("aria-labelledby"), runContinues: strip.hasAttribute("data-run-continues"),
        marginTop: C(strip, "margin-top"), cols: C(strip, "grid-template-columns") },
      days: qa(".day", strip).map(dayInfo),
    };
  });

  const form = q("form.add"), label = q("label.add-label"), input = q("#new-habit"), addBtn = q(".add .btn"), msg = q("#new-habit-msg");
  out.form = { rect: R(form), novalidate: form.hasAttribute("novalidate"), marginTop: C(form, "margin-top"),
    label: { tag: label.tagName, htmlFor: label.getAttribute("for"), text: T(label), rect: R(label), display: C(label, "display"), mb: C(label, "margin-bottom"), ...font(label) },
    row: R(q(".add-row")),
    input: { rect: R(input), attrs: A(input), height: C(input, "height"), radius: C(input, "border-radius"), border: `${C(input, "border-top-width")} ${C(input, "border-top-style")} ${C(input, "border-top-color")}`,
      bg: C(input, "background-color"), padding: C(input, "padding"), disabled: input.disabled, value: input.value, size: C(input, "font-size"), color: C(input, "color") },
    btn: { rect: R(addBtn), text: T(addBtn), type: addBtn.getAttribute("type"), disabled: addBtn.disabled, bg: C(addBtn, "background-color"), color: C(addBtn, "color"),
      radius: C(addBtn, "border-radius"), ...font(addBtn) },
    msg: { tag: msg.tagName, id: msg.id, cls: msg.className, live: msg.getAttribute("aria-live"), text: msg.textContent, display: C(msg, "display"), rect: R(msg) } };

  const empty = q("p.empty");
  out.empty = empty ? { rect: R(empty), text: empty.textContent, innerHTML: empty.innerHTML, ...font(empty),
    strong: { text: T(q("strong", empty)), display: C(q("strong", empty), "display"), rect: R(q("strong", empty)), mb: C(q("strong", empty), "margin-bottom"), ...font(q("strong", empty)) } } : null;

  const gridEl = q(".heat-grid"), cellsEl = q(".cells"), wd = q(".wdays"), mo = q(".months"), title = q(".heat-title"), lg = q(".legend");
  const dot = (el) => { const b = getComputedStyle(el, "::before"), a = getComputedStyle(el, "::after");
    return { bw: b.width, bh: b.height, bbg: b.backgroundColor, bshadow: b.boxShadow, bradius: b.borderRadius,
             aw: a.width, ah: a.height, aborder: `${a.borderTopWidth} ${a.borderTopStyle} ${a.borderTopColor}`, aradius: a.borderRadius, acontent: a.content }; };
  out.heat = { rect: R(heat), tag: heat.tagName, labelledby: heat.getAttribute("aria-labelledby"), bg: C(heat, "background-color"), radius: C(heat, "border-radius"),
    padding: C(heat, "padding"), position: C(heat, "position"), top: C(heat, "top"), marginTop: C(heat, "margin-top"),
    title: { tag: title.tagName, id: title.id, text: T(title), rect: R(title), mb: C(title, "margin-bottom"), ...font(title) },
    grid: R(gridEl), cellsRect: R(cellsEl), cellsCols: C(cellsEl, "grid-template-columns"), cellsFlow: C(cellsEl, "grid-auto-flow"),
    months: { ariaHidden: mo.getAttribute("aria-hidden"), spans: qa("span", mo).map((s) => ({ text: T(s), col: s.style.gridColumn, rect: R(s), ...font(s) })) },
    wdays: { ariaHidden: wd.getAttribute("aria-hidden"), rect: R(wd), spans: qa("span", wd).map((s) => ({ text: T(s), rect: R(s), ...font(s) })), colGap: C(gridEl, "column-gap") },
    cells: qa(".cells > .hc").map((c) => ({ date: c.getAttribute("data-date"), cls: c.className, role: c.getAttribute("role"), label: c.getAttribute("aria-label"),
      ariaHidden: c.getAttribute("aria-hidden"), current: c.getAttribute("aria-current"), rect: R(c), ...dot(c) })),
    legend: { rect: R(lg), ariaHidden: lg.getAttribute("aria-hidden"), justify: C(lg, "justify-content"), gap: C(lg, "gap"), mt: C(lg, "margin-top"), ...font(lg),
      kids: Array.from(lg.children).map((c) => ({ text: T(c), cls: c.className, rect: R(c), ...(c.classList.contains("hc") ? dot(c) : {}), color: C(c, "color"), size: C(c, "font-size") })) } };

  const controls = qa("a[href], button, input, select, textarea, [tabindex], summary, [contenteditable]");
  out.controls = controls.map((c) => ({ tag: c.tagName.toLowerCase(), cls: c.className, label: c.getAttribute("aria-label") || T(c) || c.id,
    visible: c.getBoundingClientRect().width > 0 && getComputedStyle(c).display !== "none" }));
  out.innerText = document.body.innerText;
  out.nodes = { note: !!q(".note"), dialog: q("dialog") ? { open: q("dialog").open, display: C(q("dialog"), "display") } : null,
    img: qa("img, canvas, video, iframe, object, embed, audio").length, scripts: qa("body script").length };
  out.scroll = [document.documentElement.scrollWidth, document.documentElement.scrollHeight];
  return out;
}
"""
