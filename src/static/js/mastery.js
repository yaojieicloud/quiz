const user = requireAuth();
if (!user) throw new Error('redirect');

const STATUS_TEXT = {
  mastered: '精通',
};

// URL 深链参数：管理员从薄弱分析跳转过来查看某学员、并定位某课、并定位某档位
const URL_PARAMS = new URLSearchParams(location.search);
const DEEP_STUDENT = URL_PARAMS.get('student_id');   // 管理员深链指定学员
const DEEP_TOPIC = URL_PARAMS.get('topic') ? parseInt(URL_PARAMS.get('topic'), 10) : null;
const DEEP_TIER = URL_PARAMS.get('tier') ? parseInt(URL_PARAMS.get('tier'), 10) : null;

const TIERS = [1, 2, 3];
const TIER_NAMES = { 1: '初级', 2: '进阶', 3: '挑战' };

let childId = null;
let selectedTier = 1;   // 当前选中的难度档位
let currentSub = null;  // 当前展示的科目（用于切换档位时局部重渲染）

async function loadChildrenAndData() {
  const box = document.getElementById('childBox');
  // 管理员深链：直接查看指定学员，不显示家长孩子切换
  if (user.role === 'admin' && DEEP_STUDENT) {
    childId = parseInt(DEEP_STUDENT, 10);
    const stu = await API.get(`/api/admin/students`).catch(() => []);
    const info = stu.find(s => s.id === childId);
    box.innerHTML = `<div class="deep-note">👀 管理员视图：正在查看 <b>${esc(info ? (info.nickname || info.username) : ('学员#' + childId))}</b> 的精通度（与薄弱分析联动）</div>`;
    loadData();
    return;
  }
  if (user.role === 'parent') {
    const children = await API.get('/api/parent/children');
    if (children.length) {
      childId = children[0].id;
      const sel = document.createElement('div');
      sel.style.margin = '4px 0 14px';
      sel.innerHTML = '查看孩子：' + children.map(c =>
        `<span class="chip" data-cid="${c.id}" style="cursor:pointer;margin-right:8px;display:inline-block;padding:5px 12px;border-radius:12px;background:#f1edf7;color:#6b5b8a;font-weight:bold">${esc(c.nickname || c.username)}</span>`
      ).join('');
      box.appendChild(sel);
      sel.querySelectorAll('[data-cid]').forEach(el => {
        el.onclick = () => {
          childId = parseInt(el.dataset.cid);
          sel.querySelectorAll('[data-cid]').forEach(x => x.style.background = '#f1edf7');
          el.style.background = '#7b5cc4';
          el.style.color = '#fff';
          loadData();
        };
      });
      sel.querySelector('[data-cid]').style.background = '#7b5cc4';
      sel.querySelector('[data-cid]').style.color = '#fff';
    }
  }
  loadData();
}

async function loadData() {
  let url = '/api/mastery/me';
  if (user.role === 'admin' && childId) {
    url += `?student_id=${childId}`;
  } else if (user.role === 'parent' && childId) {
    url += `?student_id=${childId}`;
  }
  const data = await API.get(url);
  // 选中档位：优先用深链 tier，否则用后端默认选中档位
  selectedTier = DEEP_TIER || data.selected_tier || TIERS[0];
  render(data);
  // 管理员深链：标注正位于薄弱榜的课，形成双向联动
  if (user.role === 'admin' && childId) markWeakTopics(childId);
}

let weakTopicIds = new Set();
async function markWeakTopics(studentId) {
  try {
    const d = await API.get(`/api/admin/analytics/weakness?student_id=${studentId}&tier=${selectedTier}`);
    weakTopicIds = new Set((d.weak_topics || []).map(t => t.topic_id));
    document.querySelectorAll('.topic-card').forEach(card => {
      const tid = parseInt(card.dataset.tid || '0', 10);
      if (weakTopicIds.has(tid)) {
        const tag = document.createElement('span');
        tag.className = 'weak-flag';
        tag.textContent = '⚠ 在薄弱榜';
        tag.title = '该课当前同时出现在薄弱分析中';
        card.querySelector('.tname').appendChild(tag);
        card.classList.add('in-weak');
      }
    });
  } catch (e) { /* 忽略 */ }
}

function render(data) {
  const tabs = document.getElementById('subjTabs');
  const content = document.getElementById('content');
  tabs.innerHTML = '';
  content.innerHTML = '';
  if (!data.subjects || !data.subjects.length) {
    content.innerHTML = '<p style="color:#999">还没有任何答题记录哦～</p>';
    return;
  }
  data.subjects.forEach((sub, i) => {
    const chip = document.createElement('span');
    chip.className = 'chip' + (i === 0 ? ' active' : '');
    chip.textContent = sub.name;
    chip.onclick = () => {
      tabs.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      showSubject(sub);
    };
    tabs.appendChild(chip);
  });
  renderTierTabs();
  showSubject(data.subjects[0]);
  // 深链定位到某课：滚动并高亮
  if (DEEP_TOPIC) {
    setTimeout(() => {
      const card = document.querySelector(`.topic-card[data-tid="${DEEP_TOPIC}"]`);
      if (card) {
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        card.classList.add('deep-highlight');
      }
    }, 200);
  }
}

function renderTierTabs() {
  const wrap = document.getElementById('tierTabs');
  wrap.innerHTML = '';
  TIERS.forEach(t => {
    const chip = document.createElement('span');
    chip.className = 'chip' + (t === selectedTier ? ' active' : '');
    chip.textContent = TIER_NAMES[t];
    chip.onclick = () => {
      selectedTier = t;
      wrap.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      if (currentSub) showSubject(currentSub);
    };
    wrap.appendChild(chip);
  });
}

function showSubject(sub) {
  currentSub = sub;
  const content = document.getElementById('content');
  // 按 unit 分组
  const groups = {};
  sub.topics.forEach(t => {
    const u = t.unit || '其他';
    (groups[u] = groups[u] || []).push(t);
  });
  let html = `<div class="subj-block"><div class="subj-title">${esc(sub.name)} · 共 ${sub.topics.length} 课</div>`;
  Object.keys(groups).forEach(u => {
    html += `<div class="unit-title">${esc(u)}</div><div class="topic-grid">`;
    groups[u].forEach(t => { html += topicCard(t); });
    html += '</div>';
  });
  html += '</div>';
  content.innerHTML = html;
}

// 计算综合精通度百分比（与 home.html calcMasteryPercent 算法完全一致）
function calcMasteryPct(d) {
  if (!d || d.status === 'not_started') return null;
  if (d.status === 'mastered') return 100;
  const covRatio = (d.coverage || 0) / 80;
  const rateRaw = (d.rate || 0) / 100;
  const rateRatio = rateRaw < 0.90 ? rateRaw / 0.90 : 0.999;
  const thrN = Math.max(Math.floor((d.topic_total || 0) * 0.8), 10);
  const nRatio = (d.total || 0) / thrN;
  return Math.min(covRatio, rateRatio, nRatio, 1) * 100;
}

function topicCard(t) {
  const d = t.tiers[selectedTier] || t.tiers[TIERS[0]];
  const st = d.status;
  const rateColor = d.rate >= 90 ? '#2b8a3e' : d.rate >= 60 ? '#1c7ed6' : '#e03131';
  const covColor = d.coverage >= 80 ? '#2b8a3e' : d.coverage >= 50 ? '#1c7ed6' : '#e03131';
  const masteryPct = calcMasteryPct(d);
  const masteryColor = st === 'mastered' ? '#e67700' : masteryPct >= 80 ? '#e67700' : '#667eea';
  return `<div class="topic-card" data-tid="${t.topic_id}" style="border-left-color:${barColor(st)}">
    <div class="tname"><span>${esc(t.name)}</span>
      <span class="st-badge st-${st}">${st === 'mastered' ? '精通' : (masteryPct ? Math.round(masteryPct) + '%' : '—')}</span></div>
    <div class="bar-row fi-mastery">
      <div class="bar-label"><span>精通度</span><b style="color:${masteryColor}">${st === 'mastered' ? '100%' : (masteryPct ? Math.round(masteryPct) + '%' : '—')}</b></div>
      <div class="bar"><i style="width:${masteryPct ? Math.min(100, Math.round(masteryPct)) : 0}%"></i></div>
    </div>
    <div class="bar-row fi-rate">
      <div class="bar-label"><span>近期正确率</span><b style="color:${rateColor}">${d.rate}%</b></div>
      <div class="bar"><i style="width:${Math.min(100, d.rate)}%"></i></div>
    </div>
    <div class="bar-row fi-cov">
      <div class="bar-label"><span>知识点覆盖</span><b style="color:${covColor}">${d.coverage}%</b></div>
      <div class="bar"><i style="width:${Math.min(100, d.coverage)}%"></i></div>
    </div>
    <div class="meta">近期 ${d.total} 题 · 对 ${d.correct} 题 · ${d.sessions} 次做题 · 本课共 ${d.topic_total} 题</div>
  </div>`;
}

function barColor(st) {
  return { not_started: '#ced4da', practiced: '#1c7ed6', passed: '#2b8a3e',
           mastered: '#e67700', review: '#e03131' }[st] || '#ced4da';
}

document.getElementById('topbar').innerHTML = renderTopbar('mastery');
loadChildrenAndData();
