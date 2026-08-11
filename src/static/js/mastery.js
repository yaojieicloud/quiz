const user = requireAuth();
if (!user) throw new Error('redirect');

const STATUS_TEXT = {
  not_started: '未开始', practicing: '练习中', passed: '通过',
  mastered: '精通', review: '需复习',
};

// URL 深链参数：管理员从薄弱分析跳转过来查看某学员、并定位某课
const URL_PARAMS = new URLSearchParams(location.search);
const DEEP_STUDENT = URL_PARAMS.get('student_id');   // 管理员深链指定学员
const DEEP_TOPIC = URL_PARAMS.get('topic') ? parseInt(URL_PARAMS.get('topic'), 10) : null;

let childId = null;

async function loadChildrenAndData() {
  const box = document.getElementById('childBox');
  // 管理员深链：直接查看指定学员，不显示家长孩子切换
  if (user.role === 'admin' && DEEP_STUDENT) {
    childId = parseInt(DEEP_STUDENT, 10);
    const stu = await API.get(`/api/admin/students`).catch(() => []);
    const info = stu.find(s => s.id === childId);
    box.innerHTML = `<div class="deep-note">👀 管理员视图：正在查看 <b>${esc(info ? (info.nickname || info.username) : ('学员#' + childId))}</b> 的掌握度（与薄弱分析联动）</div>`;
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
  render(data);
  // 管理员深链：标注正位于薄弱榜的课，形成双向联动
  if (user.role === 'admin' && childId) markWeakTopics(childId);
}

let weakTopicIds = new Set();
async function markWeakTopics(studentId) {
  try {
    const d = await API.get(`/api/admin/analytics/weakness?student_id=${studentId}`);
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

function showSubject(sub) {
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

function topicCard(t) {
  const st = t.status;
  const rateColor = t.rate >= 90 ? '#2b8a3e' : t.rate >= 60 ? '#1c7ed6' : '#e03131';
  return `<div class="topic-card" data-tid="${t.topic_id}" style="border-left-color:${barColor(st)}">
    <div class="tname"><span>${esc(t.name)}</span>
      <span class="st-badge st-${st}">${STATUS_TEXT[st]}</span></div>
    <div class="bar-row fi-rate">
      <div class="bar-label"><span>近期正确率</span><b style="color:${rateColor}">${t.rate}%</b></div>
      <div class="bar"><i style="width:${Math.min(100, t.rate)}%"></i></div>
    </div>
    <div class="bar-row fi-cov">
      <div class="bar-label"><span>知识点覆盖</span><b>${t.coverage}%</b></div>
      <div class="bar"><i style="width:${Math.min(100, t.coverage)}%"></i></div>
    </div>
    <div class="meta">近期 ${t.total} 题 · 对 ${t.correct} 题 · ${t.sessions} 次练习 · 本课共 ${t.topic_total} 题</div>
  </div>`;
}

function barColor(st) {
  return { not_started: '#ced4da', practicing: '#1c7ed6', passed: '#2b8a3e',
           mastered: '#e67700', review: '#e03131' }[st] || '#ced4da';
}

document.getElementById('topbar').innerHTML = renderTopbar('mastery');
loadChildrenAndData();
