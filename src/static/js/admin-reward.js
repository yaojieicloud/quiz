// ============ 管理员奖励管理页 ============
const user = requireAuth();
if (!user) throw new Error('redirect');
if (user.role !== 'admin') { location.href = 'home.html'; }

document.getElementById('topbar').innerHTML = renderTopbar('reward');

// 默认把当前管理员自己的 ID 预填到积分调整
document.addEventListener('DOMContentLoaded', () => {
  const me = getUser();
  if (me) document.getElementById('adjId').value = me.id;
});

loadAll();

async function loadAll() {
  await loadPending();
  await loadConfig();
  await loadRules();
  await loadWheel();
  await loadItems();
}

async function loadPending() {
  const el = document.getElementById('pendingList');
  try {
    const d = await API.get('/api/admin/redeem/pending');
    if (!d.items.length) { el.innerHTML = '<p style="color:#888">暂无待核销</p>'; return; }
    el.innerHTML = d.items.map(it => `
      <div class="mine-item">
        <div>
          <div class="mi-name">${esc(it.name)}</div>
          <div style="font-size:12px;color:#888">学员#${it.student_id} · ${it.source === 'play' ? '转盘' : '直兑'} · ${fmtTime(it.created_at)}</div>
        </div>
        <button class="btn btn-green btn-sm" onclick="approve('${it.source}',${it.id})">核销</button>
      </div>`).join('');
  } catch (e) {
    el.innerHTML = '<p style="color:#c0392b">加载失败：' + esc(e.message) + '</p>';
  }
}

async function approve(source, id) {
  if (!confirm('确认核销该实物奖品？')) return;
  try {
    await API.post('/api/admin/redeem/approve', { source, id });
    toast('已核销');
    loadPending();
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function doAdjust() {
  const sid = parseInt(document.getElementById('adjId').value, 10);
  const delta = parseInt(document.getElementById('adjDelta').value, 10);
  const reason = document.getElementById('adjReason').value || 'admin_adjust';
  if (!sid || !delta) { toast('请填写学员ID和增减值', 'error'); return; }
  try {
    const r = await API.post('/api/admin/points/adjust', { student_id: sid, delta, reason });
    toast('调整后余额 ' + r.balance);
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function loadConfig() {
  try {
    const d = await API.get('/api/admin/config');
    document.getElementById('cfgCost').value = d.wheel_cost || 20;
    document.getElementById('cfgVer').textContent = d.launch_popup_version || '-';
  } catch (e) {}
}

async function saveCfg() {
  const v = document.getElementById('cfgCost').value;
  try {
    await API.put('/api/admin/config/wheel_cost', { value: String(v) });
    toast('已保存');
  } catch (e) { toast(e.message, 'error'); }
}

async function loadRules() {
  try {
    const rs = await API.get('/api/admin/scoring-rules');
    renderTable('rulesTbl', ['题数', '得分段', '积分', '启用'],
      rs.map(r => [r.question_count, r.score_band, r.points, r.is_active ? '✅' : '—']));
  } catch (e) {}
}

async function loadWheel() {
  try {
    const rs = await API.get('/api/admin/wheel-prizes');
    renderTable('prizesTbl', ['名称', '类型', '权重', '启用'],
      rs.map(r => [r.name, r.type === 'physical' ? '实物' : '虚拟', r.weight, r.is_active ? '✅' : '—']));
  } catch (e) {}
}

async function loadItems() {
  try {
    const rs = await API.get('/api/admin/redeem-items');
    renderTable('itemsTbl', ['名称', '类型', '积分', '启用'],
      rs.map(r => [r.name, r.type === 'physical' ? '实物' : '虚拟', r.cost, r.is_active ? '✅' : '—']));
  } catch (e) {}
}

function renderTable(elId, headers, rows) {
  const html = `<table class="cfg-table"><thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>` +
    `<tbody>${rows.map(r => `<tr>${r.map(c => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
  document.getElementById(elId).innerHTML = html;
}
