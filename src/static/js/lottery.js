// ============ 大转盘逻辑 ============
// 概率由后端决定，前端仅播放转动动画并展示结果。
const user = requireAuth();
if (!user) throw new Error('redirect');
document.getElementById('topbar').innerHTML = renderTopbar('lottery');
initPoints();
maybeShowLaunchPopup();

let prizes = [];
let spinning = false;
let currentRotation = 0;
const SEG_COLORS = ['#ffd6e7','#fff3bf','#d3f9d8','#d0ebff','#ffec99','#f3d9fa','#ffe8cc','#e6fcf5'];

async function init() {
  try {
    const meta = await API.get('/api/meta');
    document.getElementById('cost').textContent = meta.wheel_cost;
  } catch (e) {}
  await loadBalance();
  await loadPrizes();
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

async function loadPrizes() {
  try {
    prizes = await API.get('/api/wheel/prizes');
  } catch (e) {
    prizes = [];
  }
  renderWheel();
  document.getElementById('prizeList').innerHTML =
    prizes.map(p => `<span class="pill">${esc(p.name)}</span>`).join('');
}

function renderWheel() {
  const n = prizes.length || 1;
  const seg = 360 / n;
  const stops = [];
  for (let i = 0; i < n; i++) {
    const c = SEG_COLORS[i % SEG_COLORS.length];
    stops.push(`${c} ${i * seg}deg ${(i + 1) * seg}deg`);
  }
  document.getElementById('wheel').style.background = `conic-gradient(${stops.join(',')})`;
  const radius = 100;
  document.getElementById('wheelLabels').innerHTML = prizes.map((p, i) => {
    const mid = i * seg + seg / 2;
    return `<div class="wheel-label" style="transform:rotate(${mid}deg) translateY(-${radius}px) rotate(${-mid}deg)">${esc(p.name)}</div>`;
  }).join('');
}

async function spin() {
  if (spinning) return;
  const btn = document.getElementById('spinBtn');
  btn.disabled = true;
  spinning = true;

  let res;
  try {
    res = await API.post('/api/wheel/spin', { mode: 'wheel' });
  } catch (e) {
    showError('请求失败', e.message);
    btn.disabled = false;
    spinning = false;
    return;
  }

  // 找到中奖奖品在列表中的索引，转动使其停在指针处
  let idx = prizes.findIndex(p => p.name === res.prize_name);
  if (idx < 0) idx = 0;
  const n = prizes.length || 1;
  const seg = 360 / n;
  const theta = idx * seg + seg / 2;            // 该段中心相对顶部的顺时针角
  const targetMod = (360 - theta) % 360;         // 使其中心转到指针（顶部）
  const base = currentRotation % 360;
  let delta = targetMod - base;
  if (delta < 0) delta += 360;
  currentRotation += 360 * 5 + delta;           // 至少转 5 圈
  document.getElementById('wheelWrap').style.transform = `rotate(${currentRotation}deg)`;

  setTimeout(() => {
    showResult(res);
    btn.disabled = false;
    spinning = false;
    loadBalance();
    initPoints();
  }, 4300);
}

function showResult(res) {
  const physical = res.is_physical;
  const emoji = physical ? '🎁' : (res.prize_name === '谢谢参与' ? '🙂' : '✨');
  const sub = physical
    ? '实物奖品请找管理员叔叔/阿姨核销领取哦～'
    : (res.prize_name === '谢谢参与' ? '下次一定中大奖！' : '已放入你的奖品库～');
  const html = `
    <div class="result-mask" onclick="this.remove()">
      <div class="result-card" onclick="event.stopPropagation()">
        <div class="result-emoji">${emoji}</div>
        <div class="result-title">${esc(res.prize_name)}</div>
        <div class="result-sub">${sub}</div>
        <button class="btn btn-green" onclick="location.href='redeem.html'">查看我的奖品 🎁</button>
        <div style="margin-top:10px;"><button class="btn btn-yellow btn-sm" onclick="this.closest('.result-mask').remove()">继续抽奖 🎡</button></div>
      </div>
    </div>`;
  document.body.insertAdjacentHTML('beforeend', html);
}
