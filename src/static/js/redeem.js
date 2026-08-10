// ============ 兑换商城 + 我的奖品 ============
const user = requireAuth();
if (!user) throw new Error('redirect');
document.getElementById('topbar').innerHTML = renderTopbar('redeem');
initPoints();
maybeShowLaunchPopup();

async function init() {
  await loadBalance();
  await loadMall();
  await loadMine();
}
init();

async function loadBalance() {
  try {
    const d = await API.get('/api/points/balance');
    document.getElementById('balance').textContent = d.balance;
  } catch (e) {
    document.getElementById('balance').textContent = '—';
  }
}

async function loadMall() {
  const grid = document.getElementById('mallGrid');
  try {
    const items = await API.get('/api/redeem/items');
    if (!items.length) {
      grid.innerHTML = '<div style="color:#9c8bb5;">商城暂未上架商品</div>';
      return;
    }
    grid.innerHTML = items.map(it => `
      <div class="reward-card">
        <div class="rc-name">${esc(it.name)}</div>
        <div class="rc-cost">💎 ${it.cost} 积分</div>
        <button class="btn btn-green btn-sm" onclick="redeem(${it.id}, ${it.cost})">立即兑换</button>
      </div>`).join('');
  } catch (e) {
    grid.innerHTML = '<div style="color:#c92a2a;">加载失败</div>';
  }
}

async function loadMine() {
  const box = document.getElementById('mineList');
  try {
    const data = await API.get('/api/redeem/mine');
    const items = data.items || [];
    if (!items.length) {
      box.innerHTML = '<div style="color:#9c8bb5;text-align:center;padding:20px;">还没有奖品，去转转盘或兑换吧～</div>';
      return;
    }
    box.innerHTML = items.map(m => {
      const badge = statusBadge(m.status);
      const hint = m.is_physical && m.status === 'pending'
        ? '<span style="font-size:12px;color:#e67700;">找管理员核销领取</span>'
        : '';
      return `<div class="mine-item">
        <div>
          <div class="mi-name">${esc(m.name)}</div>
          <div style="font-size:12px;color:#9c8bb5;">${m.source === 'wheel' ? '🎡 大转盘' : '🛍️ 兑换'} · ${fmtTime(m.created_at)}</div>
        </div>
        <div style="text-align:right;">${badge}<div>${hint}</div></div>
      </div>`;
    }).join('');
  } catch (e) {
    box.innerHTML = '<div style="color:#c92a2a;">加载失败</div>';
  }
}

function statusBadge(status) {
  if (status === 'pending') return '<span class="badge badge-pending">待核销</span>';
  if (status === 'redeemed') return '<span class="badge badge-redeemed">已领取</span>';
  return '<span class="badge badge-granted">已发放</span>';
}

async function redeem(itemId, cost) {
  if (!confirm(`确定消耗 ${cost} 积分兑换吗？`)) return;
  try {
    const res = await API.post('/api/redeem/direct', { item_id: itemId });
    const tip = res.is_physical ? '兑换成功！找管理员核销领取～' : '兑换成功！';
    toast(tip, 'success');
    loadBalance();
    initPoints();
    loadMine();
  } catch (e) {
    toast(e.message, 'error');
  }
}
