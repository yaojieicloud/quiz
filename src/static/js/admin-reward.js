// ============ 管理员奖励管理页 ============
const user = requireAuth();
if (!user) throw new Error('redirect');
if (user.role !== 'admin') { location.href = 'home.html'; }

document.getElementById('topbar').innerHTML = renderTopbar('reward');

// 科目列表（积分矩阵的「科目」列用）：id → 名称
let subjectMap = {};

loadAll();

async function loadAll() {
  await loadSubjects();
  await loadStudentOptions();
  await loadPending();
  await loadConfig();
  await loadEntity('rules');
  await loadEntity('wheel');
  await loadEntity('items');
}

async function loadSubjects() {
  try {
    const list = await API.get('/api/subjects');
    subjectMap = {};
    list.forEach(s => { subjectMap[s.id] = s.name; });
  } catch (e) {
    subjectMap = {};
  }
}

// 学员卡片选择器（积分调整用，移动端友好）+ 待核销筛选学员下拉
let selectedAdjId = null;
let pendingCache = [];
let pendSrcFilter = '';

async function loadStudentOptions() {
  const picker = document.getElementById('adjStudents');
  const sel = document.getElementById('pendStudent');
  const me = getUser();
  try {
    const list = await API.get('/api/admin/students');
    studentsCache = list;
    // 积分调整：学员卡片（含管理员自己）
    const cards = [];
    if (me && me.id) {
      cards.push({ id: me.id, nickname: '👑 ' + (me.nickname || me.username || '管理员'), exam_count: 0, balance: null, me: true });
    }
    list.forEach(s => cards.push(s));
    picker.innerHTML = cards.map(s => `
      <div class="stu-card" data-id="${s.id}" onclick="pickStudent(this, ${s.id})">
        <div class="sc-name">${esc(s.nickname || s.username || ('学员#' + s.id))}</div>
        <div class="sc-info">${s.me ? '我自己' : '答题 ' + (s.exam_count || 0) + ' 次'}</div>
      </div>`).join('') || '<p style="color:#888">暂无学员</p>';
    // 待核销筛选：学员下拉
    sel.innerHTML = '<option value="">全部学员</option>' +
      list.map(s => `<option value="${s.id}">${esc(s.nickname || s.username || ('学员#' + s.id))}</option>`).join('');
  } catch (e) {
    picker.innerHTML = `<p style="color:#c0392b">加载学员失败：${esc(e.message)}</p>`;
  }
}

function pickStudent(el, id) {
  document.querySelectorAll('.stu-card').forEach(c => c.classList.remove('sel'));
  el.classList.add('sel');
  selectedAdjId = id;
}

function pickSrc(el) {
  document.querySelectorAll('.psc').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
  pendSrcFilter = el.dataset.src || '';
  renderPending();
}

async function loadPending() {
  const el = document.getElementById('pendingList');
  try {
    const d = await API.get('/api/admin/redeem/pending');
    pendingCache = d.items || [];
    renderPending();
  } catch (e) {
    el.innerHTML = '<p style="color:#c0392b">加载失败：' + esc(e.message) + '</p>';
  }
}

function renderPending() {
  const el = document.getElementById('pendingList');
  const stuFilter = document.getElementById('pendStudent').value;
  let items = pendingCache;
  if (stuFilter) items = items.filter(it => String(it.student_id) === String(stuFilter));
  if (pendSrcFilter) items = items.filter(it => it.source === pendSrcFilter);
  if (!items.length) {
    el.innerHTML = '<p style="color:#888">没有符合条件的待核销记录</p>';
    return;
  }
  el.innerHTML = items.map(it => `
    <div class="pend-card ${it.source === 'direct' ? 'src-direct' : ''}">
      <div>
        <div class="pend-name">
          <span class="pend-badge ${it.source === 'play' ? 'play' : 'direct'}">${it.source === 'play' ? '🎡 转盘' : '🎁 直兑'}</span>
          ${esc(it.name)}
        </div>
        <div class="pend-meta">${esc(it.student_name)}（#${it.student_id}） · ${fmtTime(it.created_at)}</div>
      </div>
      <button class="btn btn-green btn-sm" onclick="approve('${it.source}',${it.id})">核销</button>
    </div>`).join('');
}

async function approve(source, id) {
  if (!confirm('确认核销该实物奖品？')) return;
  try {
    await API.post('/api/admin/redeem/approve', { source, id });
    toast('已核销');
    loadPending();
  } catch (e) {
    showError('请求失败', e.message);
  }
}

async function doAdjust() {
  const sid = selectedAdjId;
  const delta = parseInt(document.getElementById('adjDelta').value, 10);
  const reason = document.getElementById('adjReason').value || 'admin_adjust';
  if (!sid) { toast('请先点选一名学员（上方卡片）', 'error'); return; }
  if (!delta) { toast('请填写增减值', 'error'); return; }
  try {
    const r = await API.post('/api/admin/points/adjust', { student_id: sid, delta, reason });
    toast('调整后余额 ' + r.balance);
  } catch (e) {
    showError('请求失败', e.message);
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
  } catch (e) { showError('请求失败', e.message); }
}

// 精通奖励测试：调预览接口（只读），弹同款烟花弹窗
async function testMasteryReward() {
  try {
    const d = await API.post('/api/admin/test-mastery-reward', {});
    showMasteryRewardPopup(d.nickname, d.rewards);
  } catch (e) { showError('请求失败', e.message); }
}

// ================= 可编辑配置（积分矩阵 / 转盘奖品 / 直兑商城） =================
const dataCache = { rules: [], wheel: [], items: [] };

const ENTITIES = {
  rules: {
    title: '积分矩阵', el: 'rulesTbl', api: '/api/admin/scoring-rules',
    headers: ['科目', '题数', '得分段', '积分', '启用', '操作'],
    cols: r => [
      r.subject_id ? (subjectMap[r.subject_id] || ('科目#' + r.subject_id)) : '全局默认',
      r.question_count == 0 ? '任意/兜底' : r.question_count,
      r.score_band, r.points, r.is_active ? '✅' : '—'],
    fields: [
      { key: 'subject_id', label: '科目(空=全局默认)', type: 'subject', def: null },
      { key: 'question_count', label: '题数档位(0=兜底)', type: 'number', def: 0 },
      { key: 'score_band', label: '得分段(≤该分命中)', type: 'number', def: 100 },
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
  else if (f.type === 'subject') {
    const opts = ['<option value="">全局默认（所有科目）</option>'];
    for (const id in subjectMap)
      opts.push(`<option value="${id}" ${String(val) === String(id) ? 'selected' : ''}>${esc(subjectMap[id])}</option>`);
    ctrl = `<select id="mf_${f.key}">` + opts.join('') + `</select>`;
  }
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
    else if (f.type === 'subject') data[f.key] = el.value ? parseInt(el.value, 10) : null;
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
  } catch (e) { showError('请求失败', e.message); }
}

async function delItem(key, id) {
  if (!confirm('确认删除该条配置？')) return;
  const cfg = ENTITIES[key];
  try {
    await API.del(`${cfg.api}/${id}`);
    toast('已删除');
    loadEntity(key);
  } catch (e) { showError('请求失败', e.message); }
}

function closeModal() {
  const m = document.getElementById('cfgModal');
  if (m) m.style.display = 'none';
}
