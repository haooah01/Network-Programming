import React, { useEffect, useMemo, useRef, useState } from "react";

// =============================================================
// TCP Simulator — React (TSX) • Teaching Edition (clear & visual)
// =============================================================
// Goals:
// 1) Hiển thị rõ mô thức hoạt động TCP: 3-way handshake, sliding window, ACK, RTO/RETX.
// 2) Bảng trạng thái thời gian thực + giải thích từng bước (Explain Mode).
// 3) Biểu đồ nhỏ: cwnd (congestion window) & throughput theo thời gian (SVG, không lib ngoài).
// 4) Preset “test cases” để chạy kịch bản điển hình (LAN/WAN/Mobile/Loss/Nagle vs TCP_NODELAY).
// 5) Mã thuần React + Tailwind classes (tuỳ chọn), không phụ thuộc thư viện UI.

// ---------- Types ----------
type Endpoint = "Client" | "Server";

type WireEvent = {
  id: number;
  t: number; // ms (absolute in-sim time)
  from: Endpoint;
  to: Endpoint;
  kind: "SYN" | "SYN-ACK" | "ACK" | "DATA" | "ACK-DATA" | "RETX" | "FIN" | "FIN-ACK";
  seq?: number;
  ack?: number;
  len?: number; // payload size
  lost?: boolean;
  note?: string;
};

// ---------- Pure helpers (testable) ----------
export function rngSeeded(seed = 42) {
  // Mulberry32 deterministic PRNG
  return function () {
    let t = (seed += 0x6D2B79F5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function computeTimelineX(nowMs: number, eventTimeMs: number, windowMs = 3000) {
  // Maps event time to a 0..100 percentage windowed to the last windowMs
  const left = Math.max(0, eventTimeMs - Math.max(0, nowMs - windowMs));
  const x = Math.min(100, (left / windowMs) * 100);
  return x;
}

export function ceilDiv(a: number, b: number) {
  return Math.floor((a + b - 1) / b);
}

// ---------- Component ----------
export default function TcpSimulator() {
  // --- Sim parameters
  const [rtt, setRtt] = useState<number>(120);
  const [lossPct, setLossPct] = useState<number>(0);
  const [mss, setMss] = useState<number>(512);
  const [cwnd, setCwnd] = useState<number>(4);
  const [nagle, setNagle] = useState<boolean>(true);
  const [tcpNoDelay, setTcpNoDelay] = useState<boolean>(false);
  const [rwnd, setRwnd] = useState<number>(65535); // receive window (bytes) — minh hoạ flow control
  const [explain, setExplain] = useState<boolean>(true);

  // --- Sim state
  const [running, setRunning] = useState<boolean>(false);
  const [connected, setConnected] = useState<boolean>(false);
  const [phase, setPhase] = useState<string>("IDLE");
  const [clientSeq, setClientSeq] = useState<number>(1000);
  const [serverSeq, setServerSeq] = useState<number>(5000);
  const [timeMs, setTimeMs] = useState<number>(0);
  const [wire, setWire] = useState<WireEvent[]>([]);
  const [log, setLog] = useState<string[]>([]);
  const [nextId, setNextId] = useState<number>(1);

  // Metrics history (for charts)
  const [cwndHistory, setCwndHistory] = useState<Array<{ t: number; v: number }>>([]);
  const [tpHistory, setTpHistory] = useState<Array<{ t: number; bytes: number }>>([]); // bytes ACKed per tick
  const [retxCount, setRetxCount] = useState<number>(0);

  // refs
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const rng = useMemo(() => rngSeeded(42), []);

  // clock
  useEffect(() => {
    if (!running) return;
    timerRef.current = setInterval(() => setTimeMs((t) => t + 10), 10);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      timerRef.current = null;
    };
  }, [running]);

  const addLog = (s: string) => setLog((L) => [s, ...L].slice(0, 300));
  const maybeLose = () => rng() * 100 < lossPct;

  const schedule = (delay: number, ev: Omit<WireEvent, "id" | "t">) => {
    setWire((prev) => {
      const id = nextId;
      setNextId(id + 1);
      const t = timeMs + delay;
      return [...prev, { id, t, ...ev } as WireEvent];
    });
  };

  const resetAll = () => {
    setRtt(120); setLossPct(0); setMss(512); setCwnd(4);
    setNagle(true); setTcpNoDelay(false); setRwnd(65535);
    setRunning(false); setConnected(false); setPhase("IDLE");
    setClientSeq(1000); setServerSeq(5000);
    setTimeMs(0); setWire([]); setLog([]); setNextId(1);
    setCwndHistory([]); setTpHistory([]); setRetxCount(0);
  };

  // ---------- Handshake ----------
  const runHandshake = () => {
    if (connected) { addLog("Already connected."); return; }
    setPhase("HANDSHAKE");
    addLog("Start 3-way handshake: SYN → SYN-ACK → ACK");
    const synLost = maybeLose();
    schedule(0,   { from: "Client", to: "Server", kind: "SYN", seq: clientSeq, lost: synLost });
    schedule(rtt/2, { from: "Server", to: "Client", kind: "SYN-ACK", seq: serverSeq, ack: clientSeq + 1, lost: synLost ? true : maybeLose() });
    schedule(rtt, { from: "Client", to: "Server", kind: "ACK", seq: clientSeq + 1, ack: serverSeq + 1, lost: false });
    // Mark connected after RTT (optimistic)
    setTimeout(() => {
      setConnected(true);
      setPhase("ESTABLISHED");
      addLog("Connection established.");
      setClientSeq((s) => s + 1);
      setServerSeq((s) => s + 1);
    }, rtt + 5);
  };

  // ---------- Data transfer ----------
  const sendBurst = (bytesTotal = 4096) => {
    if (!connected) { addLog("Not connected yet. Run handshake first."); return; }
    setPhase("TRANSFER");
    const segLen = Math.min(mss, rwnd); // cannot exceed receive window for demo
    const totalSegs = ceilDiv(bytesTotal, segLen);
    let sent = 0;
    let inFlight = 0;
    const baseSeq = clientSeq;

    const trySend = () => {
      while (sent < totalSegs && inFlight < cwnd && segLen > 0) {
        if (nagle && !tcpNoDelay && inFlight > 0 && segLen < mss) {
          addLog("Nagle holds small packet until ACK.");
          break;
        }
        const seq = baseSeq + sent * segLen;
        const lost = maybeLose();
        if (lost) setRetxCount((c) => c + 1);
        schedule(0, { from: "Client", to: "Server", kind: lost ? "RETX" : "DATA", seq, len: segLen, lost });
        inFlight++;
        sent++;
        // model delayed ACK ~40ms beyond one-way delay
        const ackDelay = 40;
        const ackAt = rtt / 2 + ackDelay;
        const ackNum = seq + segLen;
        schedule(ackAt, { from: "Server", to: "Client", kind: "ACK-DATA", ack: ackNum, note: lost ? "(ghost ACK—lost)" : undefined, lost });
        if (lost) {
          const rto = Math.max(200, rtt * 1.5);
          schedule(rto, { from: "Client", to: "Server", kind: "RETX", seq, len: segLen, note: "RTO" });
          schedule(rto + rtt / 2 + ackDelay, { from: "Server", to: "Client", kind: "ACK-DATA", ack: ackNum });
        }
      }
    };

    trySend();

    const tick = Math.max(50, Math.floor(rtt / 4));
    const ackTicker = setInterval(() => {
      // Throughput calc per tick
      const bytesAcked = wire
        .filter((ev) => ev.kind === "ACK-DATA" && !ev.lost && ev.t > timeMs - tick && ev.t <= timeMs)
        .map((ev) => ev.ack ?? 0);

      // Record throughput as number of bytes progressed (approx)
      if (bytesAcked.length > 0) {
        setTpHistory((H) => [...H, { t: timeMs, bytes: bytesAcked.length * segLen }].slice(-300));
      } else {
        setTpHistory((H) => [...H, { t: timeMs, bytes: 0 }].slice(-300));
      }

      // Handle ACK arrivals & cwnd growth
      setWire((events) => {
        const arrivedAcks = events.filter((ev) => ev.kind === "ACK-DATA" && !ev.lost && ev.t <= timeMs);
        const uniq = new Set(arrivedAcks.map((a) => a.ack));
        const acksCount = uniq.size;
        inFlight = Math.max(0, inFlight - acksCount);
        if (acksCount > 0) {
          setCwnd((c) => Math.min(64, c + 1));
          trySend();
        }
        if (sent >= totalSegs && inFlight === 0) {
          clearInterval(ackTicker);
          setClientSeq(baseSeq + totalSegs * segLen);
          addLog(`Transfer complete: ${bytesTotal} bytes.`);
          setPhase("ESTABLISHED");
        }
        return events;
      });

      // Record cwnd
      setCwndHistory((H) => [...H, { t: timeMs, v: cwnd }].slice(-300));
    }, tick);
  };

  // ---------- Preset Scenarios (act like test cases) ----------
  const runScenario = (name: string) => {
    resetAll();
    setRunning(true);
    switch (name) {
      case "LAN_CLEAN":
        setRtt(10); setLossPct(0); setMss(1460); setCwnd(8);
        setTimeout(runHandshake, 0);
        setTimeout(() => sendBurst(32 * 1024), 100);
        break;
      case "WAN_LOSSY":
        setRtt(120); setLossPct(10); setMss(1200); setCwnd(4);
        setTimeout(runHandshake, 0);
        setTimeout(() => sendBurst(32 * 1024), 100);
        break;
      case "MOBILE_HIGH_RTT":
        setRtt(300); setLossPct(2); setMss(900); setCwnd(4);
        setTimeout(runHandshake, 0);
        setTimeout(() => sendBurst(64 * 1024), 100);
        break;
      case "HANDSHAKE_LOSS":
        setRtt(80); setLossPct(30); setMss(512); setCwnd(2);
        setTimeout(runHandshake, 0);
        break;
      case "NAGLE_VS_NODELAY":
        setRtt(80); setLossPct(0); setMss(256); setCwnd(2); setNagle(true); setTcpNoDelay(false);
        setTimeout(runHandshake, 0);
        setTimeout(() => sendBurst(2048), 100);
        break;
      default:
        break;
    }
  };

  // ---------- Render ----------
  const eventsSorted = useMemo(() => [...wire].sort((a, b) => a.t - b.t), [wire]);

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-4">
      <header className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12h20"/><path d="M7 12v7"/><path d="M17 12v7"/><path d="M12 2v10"/></svg>
          <h1 className="text-2xl font-bold">TCP Simulator — Teaching Edition</h1>
        </div>
        <div className="text-sm text-slate-600 flex items-center gap-3">
          <span className="px-2 py-0.5 rounded bg-slate-100">{connected ? "ESTABLISHED" : phase}</span>
          <span className="px-2 py-0.5 rounded bg-slate-100">t={timeMs}ms</span>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Controls */}
        <section className="border rounded-2xl p-4 space-y-4">
          <h2 className="font-semibold text-lg">Controls</h2>

          <Range label={`RTT: ${rtt} ms`} min={20} max={600} step={10} value={rtt} onChange={setRtt} />
          <Range label={`Loss: ${lossPct}%`} min={0} max={50} step={1} value={lossPct} onChange={setLossPct} />
          <Range label={`MSS: ${mss} bytes`} min={128} max={1460} step={32} value={mss} onChange={setMss} />
          <Range label={`cwnd: ${cwnd} seg`} min={1} max={64} step={1} value={cwnd} onChange={setCwnd} />
          <Range label={`rwnd: ${rwnd} bytes`} min={1024} max={65535} step={512} value={rwnd} onChange={setRwnd} />

          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={nagle && !tcpNoDelay} onChange={(e) => { setNagle(e.target.checked); if (e.target.checked) setTcpNoDelay(false); }} />
              <span>Nagle</span>
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={tcpNoDelay} onChange={(e) => { setTcpNoDelay(e.target.checked); if (e.target.checked) setNagle(false); }} />
              <span>TCP_NODELAY</span>
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={explain} onChange={(e) => setExplain(e.target.checked)} />
              <span>Explain Mode</span>
            </label>
          </div>

          <div className="flex gap-2 flex-wrap pt-1">
            <button className="px-3 py-2 rounded-xl bg-slate-900 text-white text-sm" onClick={() => { setRunning(true); runHandshake(); }}>3‑way handshake</button>
            <button className="px-3 py-2 rounded-xl bg-slate-200 text-sm" onClick={() => sendBurst(4096)}>Send 4 KB</button>
            <button className="px-3 py-2 rounded-xl bg-slate-100 text-sm" onClick={() => setRunning((r) => !r)}>{running ? "Pause" : "Run"}</button>
            <button className="px-3 py-2 rounded-xl bg-rose-600 text-white text-sm" onClick={resetAll}>Reset</button>
          </div>

          {/* Preset scenarios (test cases) */}
          <div className="pt-2">
            <div className="text-sm font-semibold mb-1">Preset Scenarios (Test Cases)</div>
            <div className="flex flex-wrap gap-2">
              <button className="px-2 py-1 rounded bg-slate-100 text-sm" onClick={() => runScenario("LAN_CLEAN")}>LAN clean</button>
              <button className="px-2 py-1 rounded bg-slate-100 text-sm" onClick={() => runScenario("WAN_LOSSY")}>WAN 10% loss</button>
              <button className="px-2 py-1 rounded bg-slate-100 text-sm" onClick={() => runScenario("MOBILE_HIGH_RTT")}>Mobile high RTT</button>
              <button className="px-2 py-1 rounded bg-slate-100 text-sm" onClick={() => runScenario("HANDSHAKE_LOSS")}>Handshake loss</button>
              <button className="px-2 py-1 rounded bg-slate-100 text-sm" onClick={() => runScenario("NAGLE_VS_NODELAY")}>Nagle vs NoDelay</button>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 pt-2 text-sm">
            <KV label="State" value={connected ? "ESTABLISHED" : phase} />
            <KV label="Time" value={`${timeMs} ms`} />
            <KV label="Client SEQ" value={`${clientSeq}`} />
            <KV label="Server SEQ" value={`${serverSeq}`} />
            <KV label="RETX count" value={`${retxCount}`} />
          </div>
        </section>

        {/* Wire & Explain */}
        <section className="lg:col-span-2 grid grid-rows-[auto_auto] gap-4">
          {/* Sequence timeline */}
          <div className="border rounded-2xl p-4">
            <div className="font-semibold mb-2">Wire (timeline)</div>
            <div className="overflow-x-auto border rounded-xl p-4">
              <div className="grid grid-cols-12 text-xs font-semibold text-slate-500 mb-2">
                <div className="col-span-2">Client</div>
                <div className="col-span-8 text-center">Time → (last 3s)</div>
                <div className="col-span-2 text-right">Server</div>
              </div>
              <div className="space-y-2">
                {[...wire].sort((a,b)=>a.t-b.t).map((ev) => {
                  const x = computeTimelineX(timeMs, ev.t, 3000);
                  const color = ev.lost ? "bg-red-500" : ev.kind.includes("ACK") ? "bg-green-500" : ev.kind === "RETX" ? "bg-yellow-500" : "bg-blue-500";
                  const title = `t=${ev.t}ms ${ev.kind} seq=${ev.seq ?? ''} ack=${ev.ack ?? ''} len=${ev.len ?? ''} ${ev.note ?? ''}`;
                  return (
                    <div key={ev.id} className="relative h-8">
                      <div className={`absolute top-3 w-2 h-2 rounded-full ${color} ${ev.from === 'Client' ? 'left-0' : 'right-0'}`} />
                      <div className="absolute inset-x-0 top-3 h-0.5 bg-slate-200" />
                      <div className={`absolute top-2 text-[10px] ${ev.from === 'Client' ? 'left-0' : 'right-0'}`}>{ev.from}</div>
                      <div className={`absolute top-2 text-[10px] ${ev.to === 'Client' ? 'left-0' : 'right-0'}`}>{ev.to}</div>
                      <div className="absolute top-0 left-0 right-0 h-8">
                        <div className="absolute top-1/2 -translate-y-1/2" style={{ left: `${x}%`, width: "2px" }}>
                          <div title={title} className={`h-6 w-32 -ml-16 text-center text-[10px] px-1 py-0.5 rounded ${color} text-white shadow`}>
                            {ev.kind}{ev.seq ? ` #${ev.seq}` : ''}{ev.ack ? ` →ACK ${ev.ack}` : ''}{ev.len ? ` (${ev.len})` : ''}{ev.lost ? ' ✖' : ''}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Explain Mode */}
          {explain && (
            <div className="border rounded-2xl p-4">
              <div className="font-semibold mb-2">Explain Mode — What is happening now?</div>
              <ol className="list-decimal pl-6 text-sm leading-6">
                {phase === "IDLE" && <li>Idle. Chưa có kết nối. Bấm <b>3‑way handshake</b> để bắt đầu.</li>}
                {phase === "HANDSHAKE" && (
                  <>
                    <li><b>SYN</b> (client → server) mở phiên, chứa ISN (Initial Sequence Number) = {clientSeq}.</li>
                    <li><b>SYN‑ACK</b> (server → client) xác nhận ISN của client và gửi ISN của server = {serverSeq}.</li>
                    <li><b>ACK</b> (client → server) xác nhận ISN của server. Trạng thái chuyển sang <b>ESTABLISHED</b>.</li>
                  </>
                )}
                {phase === "ESTABLISHED" && <li>Kênh đã sẵn sàng. Hãy bấm <b>Send 4 KB</b> để quan sát <b>sliding window</b> và <b>ACK</b>.</li>}
                {phase === "TRANSFER" && (
                  <>
                    <li>Client gửi từng segment kích thước <code>MSS={mss}</code> trong giới hạn <code>cwnd={cwnd}</code> và <code>rwnd={rwnd}</code>.</li>
                    <li>Server gửi <b>ACK</b> sau mỗi lượt nhận (có <i>delayed ACK</i> ~40ms). Mất gói ⇒ không thấy ACK, client sẽ <b>RTO + RETX</b>.</li>
                    <li>Với mỗi đợt ACK, <b>cwnd</b> tăng (AIMD). Thử tăng <b>Loss</b> để xem ảnh hưởng.</li>
                    <li>Bật <b>TCP_NODELAY</b> để bỏ Nagle (gửi ngay gói nhỏ), hoặc bật <b>Nagle</b> để gộp gói khi còn dữ liệu chưa ACK.</li>
                  </>
                )}
              </ol>
            </div>
          )}
        </section>
      </div>

      {/* Charts */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Chart title="cwnd (segments)" data={cwndHistory.map(p=>({x:p.t,y:p.v}))} yLabel="seg" height={160} />
        <Chart title="Throughput (bytes/tick)" data={tpHistory.map(p=>({x:p.t,y:p.bytes}))} yLabel="B/tick" height={160} />
      </section>

      {/* Event Log */}
      <section className="border rounded-2xl p-4">
        <div className="font-semibold mb-2">Event Log</div>
        <div className="h-40 overflow-auto font-mono text-xs border rounded-xl p-2 bg-slate-50 text-slate-700">
          {log.length === 0 ? (
            <div className="text-slate-400">(no events yet)</div>
          ) : (
            log.map((l, i) => <div key={i}>• {l}</div>)
          )}
        </div>
      </section>

      <footer className="text-xs text-slate-500 pt-2">© TCP teaching demo — React version. Simplified for pedagogy (no SACK/FastRetransmit/RTT estimator đầy đủ).</footer>
    </div>
  );
}

// ---------- Small UI helpers ----------
function Range({ label, min, max, step, value, onChange }: { label: string; min: number; max: number; step: number; value: number; onChange: (n: number) => void; }) {
  return (
    <div>
      <div className="flex justify-between text-sm"><span>{label}</span></div>
      <input className="w-full" type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(+e.target.value)} />
    </div>
  );
}

function KV({ label, value }: { label: string; value: string; }) {
  return (
    <div className="flex items-center gap-2"><span className="text-slate-500">{label}</span><span className="px-2 py-0.5 rounded bg-slate-100">{value}</span></div>
  );
}

function Chart({ title, data, yLabel, height = 160 }: { title: string; data: Array<{ x: number; y: number }>; yLabel: string; height?: number; }) {
  const width = 460;
  const padding = 28;
  const xs = data.length ? data.map(d=>d.x) : [0,1];
  const ys = data.length ? data.map(d=>d.y) : [0,1];
  const xMin = Math.min(...xs), xMax = Math.max(...xs);
  const yMin = Math.min(...ys), yMax = Math.max(...ys);
  const rngX = xMax - xMin || 1;
  const rngY = yMax - yMin || 1;
  const toX = (x:number)=> padding + ((x - xMin) / rngX) * (width - padding * 2);
  const toY = (y:number)=> height - padding - ((y - yMin) / rngY) * (height - padding * 2);
  const path = data.length ? data.map((d,i)=> `${i? 'L':'M'} ${toX(d.x)} ${toY(d.y)}`).join(' ') : '';
  return (
    <div className="border rounded-2xl p-3">
      <div className="text-sm font-semibold mb-1">{title}</div>
      <svg width={width} height={height} className="w-full">
        <rect x={0} y={0} width={width} height={height} fill="none" stroke="#e5e7eb" />
        {/* axes */}
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#9ca3af" />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#9ca3af" />
        {/* label */}
        <text x={padding} y={padding - 8} fontSize={10} fill="#6b7280">{yLabel}</text>
        {/* series */}
        <path d={path} fill="none" stroke="#2563eb" strokeWidth={2} />
      </svg>
    </div>
  );
}

// =============================================
// Lightweight runtime tests (no framework needed)
// =============================================
(function runRuntimeTests(){
  try {
    const r1 = rngSeeded(1), r2 = rngSeeded(1);
    const seq1 = [r1(), r1(), r1()].join(",");
    const seq2 = [r2(), r2(), r2()].join(",");
    console.assert(seq1 === seq2, "rngSeeded determinism failed");
    console.assert(computeTimelineX(0, 0, 3000) === 0, "timeline at t0 should be 0%");
    const v1 = computeTimelineX(3000, 3000, 3000); console.assert(v1 === 100, "window edge 100%");
    console.assert(ceilDiv(513, 512) === 2, "ceilDiv boundary");
    console.log("[TCP Simulator] Runtime tests passed.");
  } catch (e) {
    console.error("[TCP Simulator] Runtime tests failed:", e);
  }
})();
