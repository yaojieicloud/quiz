/* 学情分析共享组件（admin 与学员端复用）
 * 依赖：echarts（页面需引入 vendor/echarts.min.js）、esc/toast/API（common.js 提供）
 * 提供：多选下拉工具、掌握度全景渲染、最近刷题动态渲染
 */
const TYPE_NAME = { choice:'选择', judge:'判断', calc:'计算', fill:'填空', essay:'应用', match:'连线', sort:'排序', code:'编程', reading:'阅读' };
const MASTERY_BADGE = {
  not_started: ['st-not_started', '未开始'], practicing: ['st-practicing', '练习中'],
  passed: ['st-passed', '通过'], mastered: ['st-mastered', '精通'], review: ['st-review', '需复习'],
};
const ANA_PALETTE = ['#74c0fc','#ffa94d','#69db7c','#b197fc','#ff8787','#ffd43b','#63e6be','#a5d8ff'];
const _sharedCharts = {};  // echarts 实例缓存（按 domId）

function rateBadge(rate) {
  const cls = rate >= 80 ? 'rate-good' : (rate >= 60 ? 'rate-mid' : 'rate-bad');
  return `<span class="rate-badge ${cls}">${rate}%</span>`;
}
function masteryBadge(status) {
  const b = MASTERY_BADGE[status] || ['st-not_started', status || ''];
  return `<span class="st-badge ${b[0]}" style="font-size:11px;padding:1px 7px;">${b[1]}</span>`;
}

// ============ 多选下拉工具 ============
function toggleMultiSelect(containerId) {
  const dd = document.querySelector(`#${containerId} .multi-select-dropdown`);
  if (dd) dd.classList.toggle('show');
}
function populateMultiSelect(containerId, items, selectAll) {
  const dd = document.querySelector(`#${containerId} .multi-select-dropdown`);
  if (!dd) return;
  dd.innerHTML = items.map(it => `
    <label class="multi-select-item">
      <input type="checkbox" value="${it.id}" ${selectAll ? 'checked' : ''} onchange="updateMultiSelectLabel('${containerId}')">
      <span>${esc(it.name)}</span>
    </label>`).join('');
  updateMultiSelectLabel(containerId);
}
function updateMultiSelectLabel(containerId) {
  const wrap = document.getElementById(containerId);
  const btn = wrap.querySelector('.multi-select-btn');
  const checked = [...wrap.querySelectorAll('input:checked')];
  const all = wrap.querySelectorAll('input');
  if (checked.length === 0) btn.textContent = '未选科目';
  else if (checked.length === all.length) btn.textContent = '全部科目';
  else btn.textContent = `已选 ${checked.length} 科`;
}
function getMultiSelectValues(containerId) {
  const wrap = document.getElementById(containerId);
  return [...wrap.querySelectorAll('input:checked')].map(i => parseInt(i.value));
}

// ============ 科目 chip 组（与组题界面一致的多选效果） ============
// 渲染科目 chip 组，defaultNames 为默认选中的科目名数组（不传/空数组=默认全不选）；onChange 为点击后的回调（函数名字符串）
function populateSubjectChips(containerId, items, defaultNames, onChange) {
  const box = document.getElementById(containerId);
  if (!box) return;
  const defSet = new Set(defaultNames || []);
  box.innerHTML = items.map(s => `
    <span class="chip${defSet.has(s.name) ? ' active' : ''}" data-sid="${s.id}" onclick="toggleSubjectChip(this, '${containerId}'${onChange ? ", '" + onChange + "'" : ''})">${esc(s.name)}</span>
  `).join('');
}
function toggleSubjectChip(el, containerId, onChange) {
  el.classList.toggle('active');
  if (onChange && typeof window[onChange] === 'function') window[onChange]();
}
// 获取 chip 组选中的科目 ID 列表（全选时返回空数组=不过滤）
function getSubjectChipValues(containerId) {
  const box = document.getElementById(containerId);
  const all = [...box.querySelectorAll('.chip')];
  const checked = all.filter(c => c.classList.contains('active'));
  // 全选 = 不传过滤（返回空数组）
  if (checked.length === all.length) return [];
  return checked.map(c => parseInt(c.dataset.sid));
}
document.addEventListener('click', e => {
  if (!e.target.closest('.multi-select')) {
    document.querySelectorAll('.multi-select-dropdown.show').forEach(d => d.classList.remove('show'));
  }
});

// ============ 掌握度全景渲染 ============
/* d: { tier, topics: [{name, subject_name, topic_total, cells: {sid: {tier: {status, coverage}} }}], students: [{id, name}] } */
// 横向柱状图（REQ-1-1）：复刻 qyn_mastery_chart.html——标签单独一行在柱上方，柱子粗 20px 占满整行。
function renderMasteryCoverageChart(domId, d) {
  const el = document.getElementById(domId);
  if (!el) return;
  const tier = String(d.tier || 1);
  // 每课覆盖度（精通度）＝所选学员平均覆盖度（保留原聚合逻辑）
  const avgs = d.topics.map(t => {
    const students = d.students || [];
    if (!students.length) return 0;
    let sum = 0;
    students.forEach(s => {
      const cell = (t.cells[s.id] || {})[tier] || {};
      sum += (cell.coverage || 0);
    });
    return +(sum / students.length).toFixed(1);
  });
  const colors = avgs.map(v =>
    v >= 80 ? '#e67700' : v >= 50 ? '#69db7c' : v >= 20 ? '#74c0fc' : '#dee2e6'
  );
  if (!d.topics.length) {
    el.innerHTML = '<div class="hbar-emptytip">该科目暂无课时</div>';
    return;
  }
  // 生成横向柱 HTML：每课 = 标签行(hbar-head) + 柱行(hbar-track)
  const rows = d.topics.map((t, i) => {
    const v = avgs[i];
    const name = t.subject_name ? `${t.subject_name}·${t.name}` : t.name;
    return `
    <div class="hbar-row">
      <div class="hbar-head">
        <span class="hbar-label">${esc(name)}</span>
        <span class="hbar-meta">题库 ${t.topic_total} 题</span>
      </div>
      <div class="hbar-track">
        <span class="hbar-fill" style="width:${Math.min(v, 100)}%;background:${colors[i]};"></span>
        <span class="hbar-masterline" title="精通覆盖度门槛 80%"></span>
        <span class="hbar-val">${Math.round(v)}%</span>
      </div>
    </div>`;
  }).join('');
  el.innerHTML = `<div class="hbar-list">${rows}</div>`;
}

function renderMasteryMatrix(boxId, d) {
  const box = document.getElementById(boxId);
  if (!d.topics.length) { box.innerHTML = '<div class="empty"><p>该科目暂无课时</p></div>'; return; }
  const tier = String(d.tier || 1);
  let html = `<table class="ana-table" style="table-layout:auto;"><thead><tr><th style="text-align:left;">课时</th><th>题库</th>`;
  d.students.forEach(s => { html += `<th>${esc(s.name)}</th>`; });
  html += `</tr></thead><tbody>`;
  d.topics.forEach(t => {
    const tname = t.subject_name ? `<span style="color:#9c8bb5;font-size:12px;">${esc(t.subject_name)}</span><br>${esc(t.name)}` : esc(t.name);
    html += `<tr><td style="text-align:left;font-weight:500;">${tname}</td><td>${t.topic_total}题</td>`;
    d.students.forEach(s => {
      const cell = (t.cells[s.id] || {})[tier] || { status: 'not_started' };
      const st = cell.status || 'not_started';
      const cov = cell.coverage != null ? ` (${Math.round(cell.coverage)}%)` : '';
      html += `<td>${masteryBadge(st)}${cov ? `<span style="font-size:10px;color:#9c8bb5;">${cov}</span>` : ''}</td>`;
    });
    html += `</tr>`;
  });
  html += `</tbody></table>`;
  box.innerHTML = html;
}

// ============ 最近刷题动态渲染 ============
/* d: { by_topic: [{student, subject, topic, answers, rate}], sessions: [{...}] } */
// 横向柱状图（REQ-1-1）：复刻 qyn_mastery_chart.html——标签单独一行在柱上方，柱子粗 20px 占满整行。
function renderRecentTopicChart(domId, d) {
  const el = document.getElementById(domId);
  if (!el) return;
  const items = (d.by_topic || []).slice(0, 20);
  if (!items.length) {
    el.innerHTML = '<div class="hbar-emptytip">暂无答题数据</div>';
    return;
  }
  // 相对柱长：以最大答题量归一化（保留原 bar 语义）
  const maxA = Math.max(...items.map(r => r.answers)) || 1;
  const rows = items.map(r => {
    const w = Math.round(r.answers / maxA * 100);
    const name = `${r.student}·${r.subject}·${r.topic}`;
    return `
    <div class="hbar-row">
      <div class="hbar-head">
        <span class="hbar-label">${esc(name)}</span>
        <span class="hbar-meta">正确率 ${r.rate}%</span>
      </div>
      <div class="hbar-track">
        <span class="hbar-fill" style="width:${Math.min(w, 100)}%;background:#74c0fc;"></span>
        <span class="hbar-val">${r.answers}题</span>
      </div>
    </div>`;
  }).join('');
  el.innerHTML = `<div class="hbar-list">${rows}</div>`;
}

function renderRecentSessions(boxId, d) {
  const box = document.getElementById(boxId);
  if (!d.sessions.length) { box.innerHTML = '<div class="empty"><div class="icon">📭</div><p>该时间段内暂无答题记录</p></div>'; return; }
  let html = `<table class="ana-table"><thead><tr><th>时间</th><th>学员</th><th>科目</th><th>所刷课时</th><th>题数</th><th>得分</th><th>档位</th></tr></thead><tbody>`;
  d.sessions.forEach(s => {
    const time = s.started_at ? new Date(s.started_at).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) : '';
    const topics = s.topics.map(t => `${esc(t.topic)}(${t.answers}题)`).join('、') || '-';
    html += `<tr><td style="font-size:12px;color:#7a6c8c;white-space:nowrap;">${time}</td><td>${esc(s.student)}</td><td>${esc(s.subject)}</td><td style="max-width:340px;">${topics}</td><td>${s.total}</td><td>${rateBadge(s.score)}</td><td>${['', '初级', '进阶', '挑战'][s.tier] || s.tier}</td></tr>`;
  });
  html += `</tbody></table>`;
  box.innerHTML = html;
}
