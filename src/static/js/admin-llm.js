// ============ 管理员 · LLM 调用日志查看 ============
const user = requireAuth();
if (!user) throw new Error('redirect');
if (user.role !== 'admin') { location.href = 'home.html'; }

document.getElementById('topbar').innerHTML = renderTopbar('llm');

let page = 1;
const PAGE_SIZE = 30;

function buildQuery() {
  const s = document.getElementById('fScenario').value;
  const p = document.getElementById('fProvider').value;
  const st = document.getElementById('fStatus').value;
  const params = new URLSearchParams({ page, page_size: PAGE_SIZE });
  if (s) params.append('scenario', s);
  if (p) params.append('provider', p);
  if (st) params.append('status', st);
  return params.toString();
}

async function doQuery() {
  page = 1;
  await loadLogs();
}

function changePage(delta) {
  const next = page + delta;
  if (next < 1) return;
  page = next;
  loadLogs();
}

async function loadLogs() {
  const body = document.getElementById('logBody');
  body.innerHTML = '<tr><td colspan="10">加载中…</td></tr>';
  try {
    const d = await API.get('/api/admin/llm-calls?' + buildQuery());
    document.getElementById('pageInfo').textContent = `第 ${d.page} 页 / 共 ${d.total} 条`;
    if (!d.items.length) {
      body.innerHTML = '<tr><td colspan="10" style="color:#888">暂无记录</td></tr>';
      document.getElementById('stats').innerHTML = '';
      return;
    }
    body.innerHTML = d.items.map(it => `
      <tr>
        <td>${fmtTime(it.created_at)}</td>
        <td>${esc(scenarioText(it.scenario))}</td>
        <td>${esc(it.provider)}</td>
        <td>${esc(it.model)}</td>
        <td>${it.prompt_tokens ?? '-'}</td>
        <td>${it.completion_tokens ?? '-'}</td>
        <td><b>${it.total_tokens ?? '-'}</b></td>
        <td class="${it.status === 'success' ? 'ok' : 'fail'}">${it.status === 'success' ? '成功' : '失败'}</td>
        <td>${it.latency_ms ?? '-'}</td>
        <td class="err" title="${esc(it.error || '')}">${esc(it.error || '')}</td>
      </tr>`).join('');
    // 简单统计（当前页）
    const ok = d.items.filter(x => x.status === 'success').length;
    const fail = d.items.length - ok;
    const toks = d.items.reduce((a, x) => a + (x.total_tokens || 0), 0);
    document.getElementById('stats').innerHTML =
      `<span class="pill">本页成功 ${ok}</span><span class="pill">失败 ${fail}</span><span class="pill">本页消耗 Token ${toks}</span>`;
  } catch (e) {
    body.innerHTML = `<tr><td colspan="10" style="color:#c0392b">加载失败：${esc(e.message)}</td></tr>`;
  }
}

function scenarioText(s) {
  if (s === 'code_grade') return '编程题评分';
  if (s === 'weekly_report') return 'AI 周报';
  return s;
}

loadLogs();
