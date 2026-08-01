import { useEffect, useState } from 'react';
import axios from 'axios';

export default function RevenueOS() {
  const [signals, setSignals] = useState([]);
  
  useEffect(() => {
    axios.get('http://localhost:8000/api/v1/intelligence/signals')
      .then(res => setSignals(res.data.signals || []))
      .catch(err => console.error("API Connection Failed", err));
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Revenue OS Pipeline</h1>
      <div className="grid grid-cols-3 gap-6">
        <div className="glass-card p-6 rounded-xl bg-white/5 border border-white/10">
          <h3 className="font-bold mb-4">Intent Signals</h3>
          {signals.length === 0 ? <p className="text-white/40 text-sm">Waiting for live data...</p> : null}
          {signals.map((s: any, i) => <div key={i} className="p-2 bg-white/5 rounded text-sm mb-2">{s.name}</div>)}
        </div>
        <div className="glass-card p-6 rounded-xl bg-white/5 border border-white/10">
          <h3 className="font-bold mb-4">Autonomous Pipeline</h3>
          <p className="text-white/40 text-sm">No active opportunities.</p>
        </div>
        <div className="glass-card p-6 rounded-xl bg-white/5 border border-white/10">
          <h3 className="font-bold mb-4">Prediction Engine</h3>
          <p className="text-white/40 text-sm">Analyzing Knowledge Graph...</p>
        </div>
      </div>
    </div>
  );
}
