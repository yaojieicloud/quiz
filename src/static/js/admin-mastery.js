const user = requireAuth();
if (!user) throw new Error('redirect');
document.getElementById('topbar').innerHTML = renderTopbar('admin');

const subjSel = document.getElementById('subjSel');
const tierSel = document.getElementById('tierSel');
const CLS = {
  passed: 'c-passed', mastered: 'c-mastered', review: 'c-review',
  practicing: 'c-practicing', not_started: 'c-not_started',
};
const LABEL = {
  mastered: '精通',
};

async function init() {
  const subjects = await API.get('/api/subjects');
  subjSel.innerHTML = subjects.map(s => `<option value="${s.id}">${esc(s.name)}</option>`).join('');
  subjSel.onchange = load;
  tierSel.onchange = load;
  if (subjects.length) load();
}

async function load() {
  const sid = subjSel.value;
  if (!sid) return;
  const tier = tierSel.value;
  const data = await API.get(`/api/admin/mastery?subject_id=${sid}&tier=${tier}`);
  tierSel.value = String(data.tier || tier);
  render(data);
}

function render(data) {
  const ts = data.topics || [];
  const students = data.students || [];
  const total = data.total_students || 0;
  const tier = data.tier;            // 当前选中的难度档位
  const tierName = data.tier_name || '';

  // 顶部汇总
  let masteredSum = 0;
  ts.forEach(t => {
    masteredSum += t.counts.mastered;
  });
  const avgMaster = (total && ts.length) ? Math.round(masteredSum / (total * ts.length) * 100) : 0;
  document.getElementById('summary').innerHTML = `
    <div class="kpi"><div class="v">${students.length}</div><div class="l">学员人数</div></div>
    <div class="kpi"><div class="v">${ts.length}</div><div class="l">课程数</div></div>
    <div class="kpi"><div class="v">${tierName}</div><div class="l">当前档位</div></div>
    <div class="kpi"><div class="v">${avgMaster}%</div><div class="l">平均精通率</div></div>
    <div class="kpi"><div class="v">${students.map(s => esc(s.name)).join('、') || '-'}</div><div class="l">学员</div></div>`;

  // 表头：单元 / 课程 / 每位学员一列
  document.getElementById('thead').innerHTML = `<tr>
    <th>单元</th><th>课程</th>
    ${students.map(s => `<th class="stu"><span class="stu-name">${esc(s.name)}</span><br><small style="color:#adb5bd;font-weight:normal;">#${s.id}</small></th>`).join('')}
  </tr>`;

  // 表体：每一课一行，每格 = 该学员此课（当前档位）状态
  document.getElementById('tbody').innerHTML = ts.map(t => {
    const cells = students.map(s => {
      const c = (t.cells[s.id] && t.cells[s.id][tier]) || { status: 'not_started', rate: 0, coverage: 0 };
      const st = c.status;
      // 计算精通度百分比
      const masteryPct = (c.rate || 0) >= 90 && (c.coverage || 0) >= 80 && (c.total || 0) >= Math.max(Math.floor((t.topic_total || 0) * 0.8), 10) ? 100 : 
                          (c.rate || 0) > 0 ? Math.min(Math.round((c.coverage || 0) / 80 * 100), 99) : 0;
      const displayText = st === 'mastered' ? '精通' : (masteryPct > 0 ? masteryPct + '%' : '—');
      return `<td class="stu">
        <a class="mcell ${CLS[st]}" title="${esc(t.name)}（${tierName}） · ${esc(s.name)}：${displayText}（正确率 ${c.rate}% / 覆盖 ${c.coverage}%）"
           href="mastery.html?student_id=${s.id}&topic=${t.topic_id}&tier=${tier}" target="_blank">
          ${displayText}<small>正确率 ${c.rate}%</small>
        </a>
      </td>`;
    }).join('');
    return `<tr>
      <td>${esc(t.unit || '-')}</td>
      <td>${esc(t.name)}</td>
      ${cells}
    </tr>`;
  }).join('');
}

init();
