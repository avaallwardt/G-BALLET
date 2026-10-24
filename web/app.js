import { analyzeImage, message, ready } from "./engine.js";

const $ = (id) => document.getElementById(id);
const fileInput = $("file");
const dropzone = $("dropzone");
const photo = $("photo");
const overlay = $("overlay");
let lastResult = null;
let activeShapes = null;
let items = [];

// Skeleton lines between MediaPipe landmark indices
const BONES = [
  [11, 12], [11, 23], [12, 24], [23, 24],           // torso
  [11, 13], [13, 15], [15, 19], [12, 14], [14, 16], [16, 20], // arms
  [23, 25], [25, 27], [27, 29], [29, 31], [27, 31], // left leg + foot
  [24, 26], [26, 28], [28, 30], [30, 32], [28, 32], // right leg + foot
  [7, 0], [0, 8],                                   // ear - nose - ear
];
const WORKING = {
  left: new Set([23, 25, 27, 29, 31]),
  right: new Set([24, 26, 28, 30, 32]),
};

const ICON = {
  good: '<svg class="icon good" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9" fill="currentColor" opacity=".12"/><path d="M6 10.4l2.6 2.6L14 7.6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  na: '<svg class="icon na" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9" fill="currentColor" opacity=".12"/><path d="M6.5 10h7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
  chev: '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
};
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

// ---------- Upload ----------
fileInput.addEventListener("change", () => fileInput.files[0] && run(fileInput.files[0]));
["dragenter", "dragover"].forEach((e) =>
  dropzone.addEventListener(e, (ev) => { ev.preventDefault(); dropzone.classList.add("drag"); }));
["dragleave", "drop"].forEach((e) =>
  dropzone.addEventListener(e, (ev) => { ev.preventDefault(); dropzone.classList.remove("drag"); }));
dropzone.addEventListener("drop", (ev) => ev.dataTransfer.files[0] && run(ev.dataTransfer.files[0]));
$("again").addEventListener("click", () => {
  fileInput.value = "";
  $("results").hidden = true;
  $("again").hidden = true;
  $("upload").hidden = false;
  $("what").hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
});
$("example").addEventListener("click", async () => {
  const url = $("example").querySelector("img").src;
  const blob = await (await fetch(url)).blob();
  run(new File([blob], "example-arabesque.jpg", { type: blob.type || "image/jpeg" }));
});
window.addEventListener("resize", () => lastResult && draw(lastResult));

async function run(file) {
  lastResult = null;
  activeShapes = null;
  items = [];
  $("geo-caption").textContent = "";
  $("upload").hidden = true;
  $("what").hidden = true;
  $("results").hidden = false;
  $("again").hidden = false;
  ["summary", "corrections-section", "criteria-section", "na-section"].forEach((id) => ($(id).hidden = true));
  setStatus('<span class="spinner"></span>Analyzing your arabesque…');
  clearCanvas();
  window.scrollTo({ top: 0 });

  let result;
  try {
    // load the photo into the page, then run the analysis on it
    photo.src = URL.createObjectURL(file);
    try {
      await photo.decode();
    } catch {
      setStatus(`<strong>Couldn't open this photo</strong>${escapeHtml(await message("unreadable"))}`, "not-arabesque");
      return;
    }
    if (!engineLoaded) setStatus('<span class="spinner"></span>Loading the analysis (first time only)…');
    await ready;
    setStatus('<span class="spinner"></span>Analyzing your arabesque…');
    result = await analyzeImage(photo);
  } catch (err) {
    console.error(err);
    setStatus(`<strong>Couldn't analyze this photo</strong>Something went wrong. Try again?`, "not-arabesque");
    return;
  }

  lastResult = result;
  if (!result.is_arabesque) {
    setStatus(`<strong>Not an arabesque</strong>${escapeHtml(result.message)}`, "not-arabesque");
  } else {
    setStatus("");
    renderReport(result);
  }
  draw(result);
}

let engineLoaded = false;
ready.then(() => (engineLoaded = true)).catch((err) => console.error("Analysis failed to load", err));

function setStatus(html, cls = "") {
  const el = $("status");
  el.className = "status " + cls;
  el.innerHTML = html;
}

// ---------- Report ----------
function measureTable(math) {
  if (!math || !math.length) return "";
  return `<table class="measure"><tbody>${math.map(([k, v]) =>
    `<tr class="${k === "Target" ? "target" : ""}"><th>${escapeHtml(k)}</th><td>${escapeHtml(v)}</td></tr>`).join("")}</tbody></table>`;
}

function renderReport(result) {
  // flatten every criterion, remembering which element it belongs to
  items = result.elements.flatMap((e) => e.constraints.map((c) => ({ ...c, element: e.title, elementKey: e.key })));
  items.forEach((c, i) => (c.i = i));
  const scored = items.filter((c) => c.score !== "na");
  const fixes = items.filter((c) => c.score === "moderate" || c.score === "major")
    .sort((a, b) => (a.score === "major" ? 0 : 1) - (b.score === "major" ? 0 : 1) || a.i - b.i);
  const met = items.filter((c) => c.score === "good");
  const na = items.filter((c) => c.score === "na");
  const s = result.summary;

  // Summary
  $("summary").hidden = false;
  $("summary").innerHTML = `
    <div class="chips">
      <span class="chip">${chipHtml(s.working_leg)}</span>
      <span class="chip">${chipHtml(s.arm_position)}</span>
    </div>
    <div class="score-line">
      <span class="score-num">${s.good} <small>of ${s.scored}</small></span>
      <span class="score-label">criteria met</span>
    </div>
    <div class="bar">${scored.map((c) => `<i class="${c.score}"></i>`).join("")}</div>
    <div class="score-meta">
      <span class="m-good">${met.length} met</span>
      <span class="m-fix">${fixes.length} correction${fixes.length === 1 ? "" : "s"}</span>
      ${na.length ? `<span class="m-na">${na.length} not scored</span>` : ""}
    </div>`;

  // Corrections
  $("corrections-section").hidden = false;
  $("corrections-count").textContent = fixes.length;
  $("corrections-count").hidden = fixes.length === 0;
  $("corrections").innerHTML = fixes.length ? fixes.map((c) => `
    <article class="card correction ${c.score}" data-i="${c.i}" tabindex="0" role="button">
      <div class="corr-top">
        <span class="corr-where">${escapeHtml(c.element)}</span>
        <span class="tag ${c.score}">${escapeHtml(cap(c.score_label))}</span>
      </div>
      <p class="corr-text">${escapeHtml(c.feedback)}</p>
      <p class="corr-criteria">${escapeHtml(c.constraint)}</p>
      ${measureTable(c.geometry.math)}
      ${c.note ? `<p class="note">${escapeHtml(c.note)}</p>` : ""}
    </article>`).join("")
    : `<div class="card empty-state">${ICON.good} No corrections. Every scored criteria was met.</div>`;

  // Criteria met, by category
  const cats = result.elements
    .map((e) => ({ e, rows: met.filter((c) => c.elementKey === e.key), scoredCount: scored.filter((c) => c.elementKey === e.key).length }))
    .filter((x) => x.rows.length);
  $("criteria-section").hidden = cats.length === 0;
  $("categories").innerHTML = cats.map(({ e, rows, scoredCount }) => `
    <section class="card category">
      <header class="cat-head"><h3>${escapeHtml(e.title)}</h3><span class="cat-count">${rows.length} of ${scoredCount} met</span></header>
      ${rows.map((c) => `
        <div class="row" data-i="${c.i}">
          <button class="row-btn" type="button" aria-expanded="false">
            ${ICON.good}
            <span class="row-name">${escapeHtml(c.constraint)}</span>
            <span class="row-value">${escapeHtml(c.geometry.math.length ? c.geometry.math[0][1] : "")}</span>
            ${ICON.chev}
          </button>
          <div class="row-detail" hidden>
            <p class="row-feedback">${escapeHtml(c.feedback)}</p>
            ${measureTable(c.geometry.math)}
            ${c.note ? `<p class="note">${escapeHtml(c.note)}</p>` : ""}
          </div>
        </div>`).join("")}
    </section>`).join("");

  // Not scored, grouped by reason
  const groups = new Map();
  na.forEach((c) => {
    if (!groups.has(c.feedback)) groups.set(c.feedback, []);
    groups.get(c.feedback).push(`${c.element}: ${c.constraint}`);
  });
  $("na-section").hidden = groups.size === 0;
  $("not-scored").innerHTML = [...groups].map(([reason, names]) => `
    <div class="row">
      <div class="row-btn">
        ${ICON.na}
        <span><span class="row-name">${escapeHtml(reason)}</span><br><span class="row-sub">${names.map(escapeHtml).join(" · ")}</span></span>
        <span></span>
      </div>
    </div>`).join("");

  // Interactions
  document.querySelectorAll(".correction").forEach((card) => {
    card.addEventListener("click", () => select(+card.dataset.i));
    card.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); select(+card.dataset.i); } });
  });
  document.querySelectorAll("#categories .row").forEach((row) => {
    row.querySelector(".row-btn").addEventListener("click", () => {
      const open = !row.classList.contains("open");
      row.classList.toggle("open", open);
      row.querySelector(".row-detail").hidden = !open;
      row.querySelector(".row-btn").setAttribute("aria-expanded", open);
      select(+row.dataset.i, false);
    });
  });

  // start by showing the first correction (or the first criteria met)
  const first = fixes[0] || met[0];
  if (first) select(first.i, false);
}

function chipHtml(text) {
  const [k, ...v] = text.split(":");
  return v.length ? `${escapeHtml(k)}: <b>${escapeHtml(v.join(":").trim())}</b>` : escapeHtml(text);
}

function select(i, scroll = true) {
  const c = items[i];
  if (!c || !c.geometry.shapes.length) return;
  document.querySelectorAll(".correction.active, .row.active").forEach((el) => el.classList.remove("active"));
  document.querySelectorAll(`[data-i="${i}"]`).forEach((el) => el.classList.add("active"));
  activeShapes = c.geometry.shapes;
  $("geo-caption").textContent = `${c.element}: ${c.constraint}`;
  if (lastResult) draw(lastResult);
  if (scroll && window.innerWidth <= 900) photo.scrollIntoView({ behavior: "smooth", block: "center" });
}

function clearCanvas() {
  overlay.getContext("2d").clearRect(0, 0, overlay.width, overlay.height);
}

function draw(result) {
  if (!result.landmarks) return clearCanvas();
  // The image is drawn with object-fit: contain, so work out where it actually sits inside its box
  const box = photo.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  overlay.width = box.width * dpr;
  overlay.height = box.height * dpr;
  const ctx = overlay.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, box.width, box.height);

  const scale = Math.min(box.width / photo.naturalWidth, box.height / photo.naturalHeight);
  const w = photo.naturalWidth * scale, h = photo.naturalHeight * scale;
  const ox = (box.width - w) / 2, oy = (box.height - h) / 2;
  const pt = (i) => [ox + result.landmarks[i].x * w, oy + result.landmarks[i].y * h];
  const working = WORKING[result.working_leg] || new Set();
  const accent = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim();
  const lw = Math.max(2, Math.min(w, h) / 160);

  ctx.lineCap = "round";
  for (const [a, b] of BONES) {
    const isWork = working.has(a) && working.has(b);
    ctx.globalAlpha = activeShapes ? 0.45 : 1;
    ctx.strokeStyle = isWork ? accent : "rgba(255,255,255,.9)";
    ctx.lineWidth = isWork ? lw * 1.6 : lw;
    ctx.shadowColor = "rgba(0,0,0,.35)";
    ctx.shadowBlur = 3;
    ctx.beginPath();
    ctx.moveTo(...pt(a));
    ctx.lineTo(...pt(b));
    ctx.stroke();
  }
  ctx.shadowBlur = 0;
  ctx.globalAlpha = activeShapes ? 0.45 : 1;
  const used = new Set(BONES.flat());
  for (const i of used) {
    const [x, y] = pt(i);
    ctx.fillStyle = working.has(i) ? accent : "#fff";
    ctx.beginPath();
    ctx.arc(x, y, lw * 1.3, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
  if (activeShapes) drawShapes(ctx, activeShapes, pt, lw, Math.min(w, h));
}

// ---- Geometry overlay: draws the angle / line / triangle that was measured ----
const GEO = "#ffc83d";

function drawShapes(ctx, shapes, pt, lw, size) {
  const P = (idx) => {
    const ps = idx.map(pt);
    return [ps.reduce((a, p) => a + p[0], 0) / ps.length, ps.reduce((a, p) => a + p[1], 0) / ps.length];
  };
  const len = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1]);
  const line = (a, b, opts = {}) => {
    ctx.save();
    ctx.strokeStyle = opts.color || GEO;
    ctx.lineWidth = opts.width || lw * 1.4;
    ctx.setLineDash(opts.dash ? [lw * 3, lw * 2.5] : []);
    ctx.shadowColor = "rgba(0,0,0,.5)"; ctx.shadowBlur = 4;
    ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...b); ctx.stroke();
    ctx.restore();
  };
  const dot = (p, r = lw * 2.2) => {
    ctx.save();
    ctx.fillStyle = GEO; ctx.strokeStyle = "#1e1b1f"; ctx.lineWidth = lw * 0.6;
    ctx.beginPath(); ctx.arc(...p, r, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    ctx.restore();
  };
  const label = (text, p) => {
    if (!text) return;
    ctx.save();
    const fs = Math.max(12, Math.min(20, size / 22));
    ctx.font = `600 ${fs}px "DM Mono", ui-monospace, monospace`;
    const tw = ctx.measureText(text).width, pad = fs * 0.4;
    const x = Math.min(Math.max(p[0] - tw / 2 - pad, 2), ctx.canvas.width / (window.devicePixelRatio || 1) - tw - pad * 2 - 2);
    const y = Math.max(p[1] - fs / 2 - pad, 2);
    ctx.fillStyle = "rgba(30,27,31,.88)";
    ctx.beginPath(); ctx.roundRect(x, y, tw + pad * 2, fs + pad * 2, 6); ctx.fill();
    ctx.fillStyle = GEO; ctx.textBaseline = "top";
    ctx.fillText(text, x + pad, y + pad * 1.05);
    ctx.restore();
  };
  // arc at vertex v from direction of a to direction of c (short way), label on the bisector
  const arc = (v, a, c, text) => {
    const ta = Math.atan2(a[1] - v[1], a[0] - v[0]);
    const tc = Math.atan2(c[1] - v[1], c[0] - v[0]);
    let d = tc - ta;
    while (d > Math.PI) d -= 2 * Math.PI;
    while (d <= -Math.PI) d += 2 * Math.PI;
    const r = Math.max(14, Math.min(len(v, a), len(v, c), size * 0.25) * 0.35);
    ctx.save();
    ctx.fillStyle = "rgba(255,200,61,.25)"; ctx.strokeStyle = GEO; ctx.lineWidth = lw;
    ctx.beginPath(); ctx.moveTo(...v); ctx.arc(...v, r, ta, ta + d, d < 0); ctx.closePath(); ctx.fill();
    ctx.beginPath(); ctx.arc(...v, r, ta, ta + d, d < 0); ctx.stroke();
    ctx.restore();
    const mid = ta + d / 2;
    const fs = Math.max(12, Math.min(20, size / 22));
    const lr = Math.max(r * 1.9, fs * 2.6);
    let lp = [v[0] + Math.cos(mid) * lr, v[1] + Math.sin(mid) * lr];
    if (Math.abs(d) < 0.5) {
      // narrow angle: the label would sit on the lines, so nudge it off to the side
      let n = [-Math.sin(mid), Math.cos(mid)];
      if (n[1] > 0) n = [-n[0], -n[1]];
      lp = [lp[0] + n[0] * fs * 2, lp[1] + n[1] * fs * 2];
    }
    label(text, lp);
  };

  for (const s of shapes) {
    const p = s.points.map(P);
    if (s.type === "angle") {
      line(p[1], p[0]); line(p[1], p[2]);
      arc(p[1], p[0], p[2], s.label);
      p.forEach((q) => dot(q));
    } else if (s.type === "triangle") {
      ctx.save();
      ctx.fillStyle = "rgba(255,200,61,.35)"; ctx.strokeStyle = GEO; ctx.lineWidth = lw * 1.2;
      ctx.beginPath(); ctx.moveTo(...p[0]); ctx.lineTo(...p[1]); ctx.lineTo(...p[2]); ctx.closePath();
      ctx.fill(); ctx.stroke();
      ctx.restore();
      p.forEach((q) => dot(q, lw * 1.6));
    } else if (s.type === "perp") {
      const [h, a, b] = p;
      const ab = [b[0] - a[0], b[1] - a[1]];
      const t = ((h[0] - a[0]) * ab[0] + (h[1] - a[1]) * ab[1]) / (ab[0] ** 2 + ab[1] ** 2);
      const foot = [a[0] + t * ab[0], a[1] + t * ab[1]];
      const ext = (k) => [a[0] + k * ab[0], a[1] + k * ab[1]];
      line(ext(-0.6), ext(1.3), { dash: true, width: lw });
      line(h, foot);
      [h, a, b].forEach((q) => dot(q, lw * 1.6));
    } else if (s.type === "segment") {
      line(p[0], p[1], { width: lw * 2 });
      p.forEach((q) => dot(q));
      // put the label beside the segment, away from the body midline
      const fs = Math.max(12, Math.min(20, size / 22));
      const m = [(p[0][0] + p[1][0]) / 2, (p[0][1] + p[1][1]) / 2];
      label(s.label, [m[0] + fs * 3.2, m[1] - fs * 0.5]);
    } else if (s.type === "reference") {
      line(p[0], p[1], { dash: true, width: lw, color: "rgba(255,255,255,.95)" });
    } else if (s.type === "ray") {
      line(p[0], p[1], { dash: true, width: lw, color: "rgba(255,255,255,.95)" });
      dot(p[1], lw * 1.6);
    } else if (s.type === "from_vertical" || s.type === "from_horizontal") {
      const L = Math.max(len(p[0], p[1]), size * 0.12);
      const ref = s.type === "from_vertical" ? [p[0][0], p[0][1] - L] : [p[0][0] + (s.facing || 1) * L, p[0][1]];
      // short lines (like head -> nose) are extended so the angle is visible
      const k = L / Math.max(len(p[0], p[1]), 1e-6);
      const end = [p[0][0] + (p[1][0] - p[0][0]) * k, p[0][1] + (p[1][1] - p[0][1]) * k];
      line(p[0], ref, { dash: true, width: lw, color: "rgba(255,255,255,.95)" });
      line(p[0], end);
      arc(p[0], ref, end, s.label);
      dot(p[0]); dot(p[1]);
    } else if (s.type === "level") {
      const [sh, wr] = p;
      const L = size * 0.18;
      line([sh[0] - L, sh[1]], [sh[0] + L, sh[1]], { dash: true, width: lw, color: "rgba(255,255,255,.95)" });
      line(wr, [wr[0], sh[1]], { dash: true, width: lw });
      dot(sh); dot(wr);
    }
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
