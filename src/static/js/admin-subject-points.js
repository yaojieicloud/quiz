// 科目课程积分设置
let SUBJECTS = [];

function esc(s) { return (s == null ? '' : String(s)).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function toast(msg, type = 'info') { /* 轻量提示 */
  const el = document.getElementById('batchMsg');
  if (el) { el.textContent = msg; el.style.color = type === 'error' ? '#c0392b' : '#2e8b57'; }
}

document.addEventListener('DOMContentLoaded', async () => {
  if (!localStorage.getItem('quiz_token')) { location.href = 'index.html'; return; }
  document.getElementById('topbar').innerHTML = renderTopbar('subjectPoints');
  await loadList();
});

async function loadList() {
  try {
    const data = await API.get('/api/admin/subject-points');
    SUBJECTS = data.items || [];
    const body = document.getElementById('listBody');
    if (!SUBJECTS.length) { body.innerHTML = '<tr><td colspan="8">暂无科目</td></tr>'; return; }
    body.innerHTML = SUBJECTS.map(s => {
      const set = s.has_override;
      const cur = set ? `<span class="badge-set">已自定义</span>` : `<span class="badge-default">默认(5/4/3)</span>`;
      return `<tr id="row-${s.subject_id}" class="${set ? '' : ''}">
        <td><input type="checkbox" class="chk" value="${s.subject_id}"></td>
        <td class="name">${esc(s.subject_name)}</td>
        <td>${s.category === 'programming' ? '编程' : '文化'}</td>
        <td>${cur}</td>
        <td>${set ? s.p100 : '—'}</td>
        <td>${set ? s.p90 : '—'}</td>
        <td>${set ? s.p80 : '—'}</td>
        <td>${set ? `<button class="btn btn-sm btn-red" onclick="resetOne(${s.subject_id})">恢复默认</button>` : '—'}</td>
      </tr>`;
    }).join('');
  } catch (e) { toast(e.message, 'error'); }
}

function toggleAll(src) {
  document.querySelectorAll('.chk').forEach(c => c.checked = src.checked);
}

function selectedIds() {
  return Array.from(document.querySelectorAll('.chk:checked')).map(c => parseInt(c.value, 10));
}

async function batchSet() {
  const ids = selectedIds();
  if (!ids.length) { toast('请先勾选科目', 'error'); return; }
  const p100 = parseInt(document.getElementById('p100').value, 10);
  const p90 = parseInt(document.getElementById('p90').value, 10);
  const p80 = parseInt(document.getElementById('p80').value, 10);
  if ([p100, p90, p80].some(v => isNaN(v) || v < 0)) { toast('积分须为非负整数', 'error'); return; }
  try {
    const r = await API.post('/api/admin/subject-points/batch', { subject_ids: ids, p100, p90, p80 });
    toast(`已设置 ${r.updated} 个科目`, 'info');
    await loadList();
  } catch (e) { toast(e.message, 'error'); }
}

async function resetOne(id) {
  try {
    await API.del(`/api/admin/subject-points/${id}`);
    toast('已恢复默认', 'info');
    await loadList();
  } catch (e) { toast(e.message, 'error'); }
}
