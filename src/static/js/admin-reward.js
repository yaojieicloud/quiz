// ============ 管理员奖励管理页 ============
const user = requireAuth();
if (!user) throw new Error('redirect');
if (user.role !== 'admin') { location.href = 'home.html'; }

document.getElementById('topbar').innerHTML = renderTopbar('reward');

loadAll();

async function loadAll() {
  await loadStudentOptions();
  await loadPending();
  await loadConfig();
  await loadEntity('rules');
  await loadEntity('wheel');
  await loadEntity('items');
}

// 积分调整：学员下拉（学员列表 + 当前管理员自己）
async function loadStudentOptions() {
  const sel = document.getElementById('adjId');
  const me = getUser();
  try {
    const list = await API.get('/api/admin/students');
    const opts = ['<option value="">— 请选择 —</option>'];
    if (me && me.id) opts.push(`<option value="${me.id}">👑 ${esc(me.nickname || me.username || '管理员')}（我自己 #${me.id}）</option>`);
    list.forEach(s => {
      opts.push(`<option value="${s.id}">${esc(s.nickname || s.username)}（#${s.id}）· 答题${s.exam_count}次</option>`);
    });
    sel.innerHTML = opts.join('');
  } catch (e) {
    sel.innerHTML = `<option value="">加载学员失败：${esc(e.message)}</option>`;
  }
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
          <div style="font-size:12px;color:#888">${esc(it.student_name)}（#${it.student_id}） · ${it.source === 'play' ? '转盘' : '直兑'} · ${fmtTime(it.created_at)}</div>
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
  if (!sid) { toast('请选择学员', 'error'); return; }
  if (!delta) { toast('请填写增减值', 'error'); return; }
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

// ================= 可编辑配置（积分矩阵 / 转盘奖品 / 直兑商城） =================
const dataCache = { rules: [], wheel: [], items: [] };

const ENTITIES = {
  rules: {
    title: '积分矩阵', el: 'rulesTbl', api: '/api/admin/scoring-rules',
    headers: ['题数', '得分段', '积分', '启用', '操作'],
    cols: r => [r.question_count == 0 ? '任意题数' : r.question_count, r.score_band, r.points, r.is_active ? '✅' : '—'],
    fields: [
      { key: 'question_count', label: '题数(0=任意)', type: 'number', def: 0 },
      { key: 'score_band', label: '得分段', type: 'number', def: 100 },
      { key: 'points', label: '发放积分', type: 'number', def: 5 },
      { key: 'is_active', label: '启用', type: 'checkbox', def: true },
    ],
  },
  wheel: {
    title: '转盘奖品', el: 'prizesTbl', api: '/api/admin/wheel-prizes',
    headers: ['名称', '类型', '权重', '启用', '操作'],
    cols: r => [r.name, r.type === 'physical' ? '实物' : '虚拟', r.weight, r.is_active ? '✅' : '—'],
    fields: [
      { key: 'mode', label: '模式', type: 'hidden', def: 'wheel' },
      { key: 'name', label: '奖品名称', type: 'text', def: '' },
      { key: 'type', label: '类型', type: 'select', options: [['physical', '实物'], ['virtual', '虚拟']], def: 'physical' },
      { key: 'weight', label: '权重(越大越易中)', type: 'number', def: 10 },
      { key: 'sort_order', label: '排序', type: 'number', def: 0 },
      { key: 'virtual_payload', label: '虚拟载荷(可选,如 +2积分)', type: 'text', def: '' },
      { key: 'is_active', label: '启用', type: 'checkbox', def: true },
    ],
  },
  items: {
    title: '直兑商城', el: 'itemsTbl', api: '/api/admin/redeem-items',
    headers: ['名称', '类型', '兑换积分', '启用', '操作'],
    cols: r => [r.name, r.type === 'physical' ? '实物' : '虚拟', r.cost, r.is_active ? '✅' : '—'],
    fields: [
      { key: 'name', label: '商品名称', type: 'text', def: '' },
      { key: 'type', label: '类型', type: 'select', options: [['physical', '实物'], ['virtual', '虚拟']], def: 'physical' },
      { key: 'cost', label: '兑换所需积分', type: 'number', def: 100 },
      { key: 'sort_order', label: '排序', type: 'number', def: 0 },
      { key: 'virtual_payload', label: '虚拟载荷(可选,如 +2积分)', type: 'text', def: '' },
      { key: 'is_active', label: '启用', type: 'checkbox', def: true },
    ],
  },
};

async function loadEntity(key) {
  const cfg = ENTITIES[key];
  try {
    const list = await API.get(cfg.api);
    dataCache[key] = list;
    renderEditable(key, list);
  } catch (e) {
    document.getElementById(cfg.el).innerHTML = '<p style="color:#c0392b">加载失败：' + esc(e.message) + '</p>';
  }
}

function renderEditable(key, list) {
  const cfg = ENTITIES[key];
  const head = cfg.headers.map(h => `<th>${h}</th>`).join('');
  const body = list.map(r => {
    const cells = cfg.cols(r).map(c => `<td>${esc(c)}</td>`).join('');
    const actions = `<td>
      <button class="btn btn-sm btn-yellow" onclick="openModal('${key}',${r.id})">编辑</button>
      <button class="btn btn-sm btn-red" onclick="delItem('${key}',${r.id})">删除</button>
    </td>`;
    return `<tr>${cells}${actions}</tr>`;
  }).join('');
  const empty = list.length ? '' : `<tr><td colspan="${cfg.headers.length}" style="color:#999">暂无数据</td></tr>`;
  document.getElementById(cfg.el).innerHTML =
    `<div style="margin-bottom:8px"><button class="btn btn-sm btn-green" onclick="openModal('${key}',null)">+ 新增</button></div>
     <table class="cfg-table"><thead><tr>${head}</tr></thead><tbody>${body || empty}</tbody></table>`;
}

// ---------------- 弹窗 ----------------
let modalState = null;

function ensureModal() {
  if (document.getElementById('cfgModal')) return;
  const html = `
    <div id="cfgModal" class="cfg-modal-mask" style="display:none">
      <div class="cfg-modal">
        <h3 id="cfgModalTitle"></h3>
        <div id="cfgModalBody"></div>
        <div class="cfg-modal-actions">
          <button class="btn-gray" onclick="closeModal()">取消</button>
          <button class="btn btn-green" onclick="submitModal()">保存</button>
        </div>
      </div>
    </div>`;
  document.body.insertAdjacentHTML('beforeend', html);
}

function openModal(key, id) {
  const cfg = ENTITIES[key];
  const rec = id != null ? dataCache[key].find(r => r.id === id) : null;
  modalState = { key, id };
  ensureModal();
  document.getElementById('cfgModalTitle').textContent = (id ? '编辑' : '新增') + cfg.title;
  document.getElementById('cfgModalBody').innerHTML =
    cfg.fields.map(f => fieldRow(f, rec ? rec[f.key] : f.def)).join('');
  document.getElementById('cfgModal').style.display = 'flex';
}

function fieldRow(f, val) {
  if (f.type === 'hidden') return '';
  let ctrl = '';
  if (f.type === 'number') ctrl = `<input type="number" id="mf_${f.key}" value="${val ?? ''}">`;
  else if (f.type === 'text') ctrl = `<input type="text" id="mf_${f.key}" value="${esc(val ?? '')}">`;
  else if (f.type === 'select')
    ctrl = `<select id="mf_${f.key}">` +
      f.options.map(o => `<option value="${o[0]}" ${String(val) === String(o[0]) ? 'selected' : ''}>${o[1]}</option>`).join('') +
      `</select>`;
  else if (f.type === 'checkbox')
    ctrl = `<input type="checkbox" id="mf_${f.key}" ${val ? 'checked' : ''}>`;
  return `<div class="form-row"><label>${f.label}</label>${ctrl}</div>`;
}

function collectModal() {
  const cfg = ENTITIES[modalState.key];
  const data = {};
  for (const f of cfg.fields) {
    if (f.type === 'hidden') { data[f.key] = f.def; continue; }
    const el = document.getElementById('mf_' + f.key);
    if (f.type === 'checkbox') data[f.key] = el.checked;
    else if (f.type === 'number') data[f.key] = parseInt(el.value, 10) || 0;
    else data[f.key] = el.value;
  }
  return data;
}

async function submitModal() {
  const { key, id } = modalState;
  const cfg = ENTITIES[key];
  const data = collectModal();
  try {
    if (id) await API.put(`${cfg.api}/${id}`, data);
    else await API.post(cfg.api, data);
    toast('已保存');
    closeModal();
    loadEntity(key);
  } catch (e) { toast(e.message, 'error'); }
}

async function delItem(key, id) {
  if (!confirm('确认删除该条配置？')) return;
  const cfg = ENTITIES[key];
  try {
    await API.del(`${cfg.api}/${id}`);
    toast('已删除');
    loadEntity(key);
  } catch (e) { toast(e.message, 'error'); }
}

function closeModal() {
  const m = document.getElementById('cfgModal');
  if (m) m.style.display = 'none';
}
