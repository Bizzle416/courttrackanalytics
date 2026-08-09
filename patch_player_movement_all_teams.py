"""
patch_player_movement_all_teams.py
====================================
Patches the four-bucket Player Movement v2.0 model into:
  - eltham-121/index.html      (Eltham 12.1 · 7-min stop-clock · 28 min)
  - dv-121/index.html          (DV 12.1 · 7-min stop-clock · 28 min)
  - eltham-122/index.html      (Eltham 12.2 · 10-min running-clock · 40 min)
  - darebin-121/index.html     (Darebin 12.1 · 7-min stop-clock · 28 min)
  - courttrack_coach_TEMPLATE.html  (template updated for future teams)

Run from the repo root:
    python patch_player_movement_all_teams.py

Backup (.bak) written beside each file before any change.
Each file is anchor-checked (must match exactly once) before patching.
"""

import sys, shutil, pathlib

REPO = pathlib.Path(r"D:\JB Stuff\Court_Track\Court_Track_Website")

TEAMS = [
    # NOTE: Eltham 12.1 was already patched locally — anchor no longer matches OLD_BLOCK.
    # It is NOT in this list. Push it manually alongside the others after local check.
    {
        "file":       REPO / "dv-121" / "index.html",
        "quarter_sec": 420,
        "clock_mode":  "stopped",
        "quarters":    4,
        "label":       "DV 12.1",
    },
    {
        "file":       REPO / "eltham-122" / "index.html",
        "quarter_sec": 600,
        "clock_mode":  "running",
        "quarters":    4,
        "label":       "Eltham 12.2",
    },
    {
        "file":       REPO / "darebin-121" / "index.html",
        "quarter_sec": 420,
        "clock_mode":  "stopped",
        "quarters":    4,
        "label":       "Darebin 12.1",
    },
]

# The template lives wherever the user keeps it — adjust path if needed
TEMPLATE = REPO / "courttrack_coach_TEMPLATE.html"

# ── Pre-flight check ─────────────────────────────────────────────────────────
print(f"Repo root: {REPO}")
print(f"Template:  {TEMPLATE}")
if not REPO.exists():
    sys.exit(f"ERROR: Repo root not found at {REPO}\nRun this script from any directory — the path is hardcoded.")
if not TEMPLATE.exists():
    sys.exit(f"ERROR: Template not found at {TEMPLATE}\nCheck the file is in the repo root and hasn't been renamed.")

# ── ANCHOR — same in every file ───────────────────────────────────────────────
OLD_BLOCK = r"""  // player movement — dual window (3g + 5g)
  const sp=seasonPlayers(d).filter(a=>{
    // count games played within the filtered set
    const pgInFilter=gs.filter(g=>g.summary&&g.summary.minutes&&(g.summary.minutes[a.pid]||0)>0).length;
    return pgInFilter>=4;
  });
  if(sp.length){
    // Build per-player signal using filtered games
    const entries=[];
    sp.forEach(a=>{
      const pid=a.pid;
      const ptsVals=gs.map(g=>(g.summary.stats[pid]||{}).pts||0);
      const minVals=gs.map(g=>+(g.summary.minutes[pid]||0).toFixed(1));
      const tovVals=gs.map(g=>(g.summary.stats[pid]||{}).tov||0);
      const rebVals=gs.map(g=>{const s=g.summary.stats[pid]||{};return(s.oreb||0)+(s.dreb||0);});
      const astVals=gs.map(g=>(g.summary.stats[pid]||{}).ast||0);
      const signals=[];
      // pts
      const pts3=metricArc(ptsVals,3),pts5=metricArc(ptsVals,5);
      if(pts3&&pts3.dir!=='flat'){const conf=pts5&&pts5.dir===pts3.dir;signals.push({cat:pts3.dir==='up'?'up':'down',text:'scoring '+(pts3.dir==='up'?'up':'down')+' '+pts3.early+'→'+pts3.late+(conf?' ✓':''),conf});}
      // minutes
      const min3=metricArc(minVals,3),min5=metricArc(minVals,5);
      if(min3&&min3.dir!=='flat'){const conf=min5&&min5.dir===min3.dir;signals.push({cat:min3.dir==='up'?'up':'down',text:'minutes '+(min3.dir==='up'?'climbing':'dipping')+(conf?' ✓':''),conf});}
      // turnovers (down = good)
      const tov3=metricArc(tovVals,3),tov5=metricArc(tovVals,5);
      if(tov3&&tov3.dir!=='flat'){const good=tov3.dir==='down';const conf=tov5&&tov5.dir===tov3.dir;signals.push({cat:good?'up':'down',text:good?'turnovers down '+tov3.early+'→'+tov3.late+(conf?' ✓':''):'turnover rate up '+tov3.early+'→'+tov3.late+(conf?' ✓':''),conf});}
      // assists
      const ast3=metricArc(astVals,3),ast5=metricArc(astVals,5);
      if(ast3&&ast3.dir!=='flat'){const conf=ast5&&ast5.dir===ast3.dir;signals.push({cat:ast3.dir==='up'?'up':'down',text:'assists '+(ast3.dir==='up'?'up '+ast3.early+'→'+ast3.late:'down '+ast3.early+'→'+ast3.late)+(conf?' ✓':''),conf});}
      entries.push({name:pnum(d.names,pid)+' '+pname(d.names,pid),signals,pid});
    });
    const rising=entries.filter(e=>e.signals.some(s=>s.cat==='up'));
    const monitor=entries.filter(e=>e.signals.some(s=>s.cat==='down'));
    h+='<div class="card"><div class="sec-h">Player movement &nbsp;·&nbsp; <span style="font-weight:400;text-transform:none;letter-spacing:0;font-size:11px;color:var(--muted);">3g + 5g rolling windows · ✓ = confirmed across both · players with 4+ games in this filter</span></div>';
    h+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">';
    h+='<div><div style="font-size:12px;font-weight:700;color:var(--windk);margin-bottom:8px;">▲ Moving forward</div>';
    if(rising.length){
      rising.forEach(r=>{
        const ups=r.signals.filter(s=>s.cat==='up');
        h+='<div style="font-size:12.5px;color:var(--ink2);margin-bottom:8px;"><strong>'+r.name+'</strong><br><span style="font-size:11.5px;">'+ups.map(s=>'<span style="color:'+(s.conf?'var(--windk)':'var(--ink2)')+';">'+s.text+'</span>').join(' · ')+'</span></div>';
      });
    }else h+='<div style="color:var(--muted);font-size:12px;">No clear upward movers in this window.</div>';
    h+='</div>';
    h+='<div><div style="font-size:12px;font-weight:700;color:var(--lossdk);margin-bottom:8px;">▼ Monitor closely</div>';
    if(monitor.length){
      monitor.forEach(r=>{
        const downs=r.signals.filter(s=>s.cat==='down');
        h+='<div style="font-size:12.5px;color:var(--ink2);margin-bottom:8px;"><strong>'+r.name+'</strong><br><span style="font-size:11.5px;">'+downs.map(s=>'<span style="color:'+(s.conf?'var(--lossdk)':'var(--ink2)')+';">'+s.text+'</span>').join(' · ')+'</span></div>';
      });
    }else h+='<div style="color:var(--muted);font-size:12px;">Nothing flagged — group holding steady.</div>';
    h+='</div></div>';
    h+='<div style="font-size:11px;color:var(--muted);margin-top:12px;padding-top:10px;border-top:1px solid var(--line2);">Signal, not verdict. Small samples move fast. Cross-check minutes played and matchup strength before acting on single-window flags.</div>';
    h+='</div>';
  }
  return h;
}"""

# ── NEW BLOCK GENERATOR ───────────────────────────────────────────────────────
# quarterLenSec and clockMode differ per team — generated per file.
# The template gets REPLACE_ placeholders so future teams set it correctly.

def new_block(quarter_sec, clock_mode, quarters, label):
    avail_min = (quarter_sec * quarters) // 60
    gmin_abs  = avail_min * 0.25
    return f"""  // ── PLAYER MOVEMENT v2.0 — four-bucket model (coach only) ──────────────────
  // Config: {label} · {quarter_sec//60}-min {clock_mode}-clock × {quarters}Q = {avail_min} min available
  // All thresholds dimensionless (% of team avg / available min).
  // Same parameter set auto-calibrates to any VJBL team via PM_CFG.
  const PM_CFG={{
    quarterLenSec:{quarter_sec}, clockMode:'{clock_mode}', quarters:{quarters}, equalTimeRule:false,
    minGames:4,
    bandPct:0.15,          // 15% of player's own baseline
    floorPct:{{pts:0.04, reb:0.04, ast:0.06, tov:0.04, mins:0.07}},
    gMinPct:0.25,          // contribution gate: 25% of available min
    gImpPct:0.08,          // contribution gate: 8% of team impact share
    minBase:1.0,           // suppress metric if player baseline below this
    cBand:2                // "within N pts" consistency label
  }};
  const PM_AVAIL_MIN=(PM_CFG.quarterLenSec*PM_CFG.quarters)/60;

  // Derive team averages from filtered games
  function pmTeamAvg(games,key){{
    if(!games.length)return 1;
    const totals=games.map(g=>{{
      let t=0;
      Object.keys(g.summary.stats||{{}}).forEach(pid=>{{
        const s=g.summary.stats[pid]||{{}};
        if(key==='reb') t+=(s.oreb||0)+(s.dreb||0);
        else if(key==='mins') t+=g.summary.minutes[pid]||0;
        else t+=s[key]||0;
      }});
      return t;
    }});
    return totals.reduce((a,v)=>a+v,0)/totals.length||1;
  }}

  // Split-half windows — non-overlapping, correct for ≤8 games
  function pmWindows(n){{
    const half=Math.floor(n/2);
    return{{base:[...Array(half).keys()], rec:[...Array(n).keys()].slice(-half)}};
  }}

  function pmMean(arr){{ return arr.length?arr.reduce((s,v)=>s+v,0)/arr.length:0; }}
  function pmR1(n){{ const v=Math.round(n*10)/10; return Number.isInteger(v)?v.toFixed(0):v.toFixed(1); }}

  function pmClassify(pid,games,teamAvg,teamImpactPG){{
    const n=games.length;
    if(n<PM_CFG.minGames) return{{bucket:'unclassified',n,signals:[],strength:0,impact:0,impShare:0,minShare:0,inBand:0}};
    const w=pmWindows(n);
    const METRICS=[
      {{k:'pts', dir:+1, vals:games.map(g=>(g.summary.stats[pid]||{{}}).pts||0), tavgKey:'pts'}},
      {{k:'reb', dir:+1, vals:games.map(g=>{{const s=g.summary.stats[pid]||{{}};return(s.oreb||0)+(s.dreb||0);}}), tavgKey:'reb'}},
      {{k:'ast', dir:+1, vals:games.map(g=>(g.summary.stats[pid]||{{}}).ast||0), tavgKey:'ast'}},
      {{k:'tov', dir:-1, vals:games.map(g=>(g.summary.stats[pid]||{{}}).tov||0), tavgKey:'tov'}},
      {{k:'mins',dir:+1, vals:games.map(g=>g.summary.minutes[pid]||0), tavgKey:'mins'}}
    ];
    let gains=0,losses=0;
    const signals=[];
    METRICS.forEach(m=>{{
      const base=pmMean(w.base.map(i=>m.vals[i]));
      const rec =pmMean(w.rec.map(i=>m.vals[i]));
      const delta=rec-base;
      const absFloor=(m.tavgKey==='mins'?PM_AVAIL_MIN:teamAvg[m.tavgKey])*PM_CFG.floorPct[m.k];
      const relFloor=base*PM_CFG.bandPct;
      const thr=Math.max(absFloor,relFloor,0.01);
      const suppressed=base<PM_CFG.minBase;
      const material=!suppressed&&Math.abs(delta)>=thr;
      const good=m.dir>0?delta>0:delta<0;
      signals.push({{k:m.k,base,rec,delta,thr,material,good,suppressed,
        label:{{pts:'scoring',reb:'rebounds',ast:'assists',tov:'turnovers',mins:'minutes'}}[m.k]}});
      if(material){{ good?gains++:losses++; }}
    }});
    const allAvg={{}};
    METRICS.forEach(m=>allAvg[m.k]=pmMean(m.vals));
    const impact=allAvg.pts+0.7*allAvg.reb+1.5*allAvg.ast-0.5*allAvg.tov;
    const impShare=teamImpactPG>0?(impact/teamImpactPG*100):0;
    const minShare=(allAvg.mins/PM_AVAIL_MIN)*100;
    const ptsAll=METRICS.find(m=>m.k==='pts').vals;
    const inBand=ptsAll.filter(v=>Math.abs(v-allAvg.pts)<=PM_CFG.cBand).length;
    const mixed=gains>0&&losses>0;
    let bucket;
    if     (gains>0&&losses===0) bucket='fwd';
    else if(losses>0&&gains===0) bucket='mon';
    else if(mixed)               bucket='mon';
    else bucket=(minShare>=PM_CFG.gMinPct*100&&impShare>=PM_CFG.gImpPct*100)?'hold':'low';
    const strength=signals.filter(s=>s.material).reduce((t,s)=>t+Math.abs(s.delta)/Math.max(s.thr,0.01),0);
    return{{bucket,n,signals,gains,losses,mixed,strength,impact,impShare,minShare,inBand,allAvg}};
  }}

  // Build four-bucket panel
  const PM_ROSTER=Object.keys(d.team.roster||{{}}).map(Number);
  const pmGames=gs;
  const pmN=pmGames.length;

  if(pmN>=2){{
    const pmTA={{
      pts:pmTeamAvg(pmGames,'pts'), reb:pmTeamAvg(pmGames,'reb'),
      ast:pmTeamAvg(pmGames,'ast'), tov:pmTeamAvg(pmGames,'tov'),
      mins:PM_AVAIL_MIN
    }};
    let pmTIpg=0;
    pmGames.forEach(g=>{{
      let gi=0;
      Object.keys(g.summary.stats||{{}}).forEach(pid=>{{
        const s=g.summary.stats[pid]||{{}};
        gi+=(s.pts||0)+0.7*((s.oreb||0)+(s.dreb||0))+1.5*(s.ast||0)-0.5*(s.tov||0);
      }});
      pmTIpg+=gi;
    }});
    pmTIpg=pmTIpg/pmGames.length||1;

    const pmResults=[];
    const allPids=new Set([
      ...PM_ROSTER,
      ...pmGames.flatMap(g=>Object.keys(g.summary.stats||{{}}).map(Number))
    ]);
    allPids.forEach(pid=>{{
      const gamesPlayed=pmGames.filter(g=>(g.summary.minutes[pid]||0)>0).length;
      if(gamesPlayed===0) return;
      const res=pmClassify(pid,pmGames,pmTA,pmTIpg);
      res.pid=pid;
      res.displayName=pnum(d.names,pid)+' '+pname(d.names,pid);
      res.gamesPlayed=gamesPlayed;
      pmResults.push(res);
    }});

    const classified=pmResults.filter(r=>r.bucket!=='unclassified');
    const unclassified=pmResults.filter(r=>r.bucket==='unclassified');
    const counts={{fwd:0,hold:0,mon:0,low:0}};
    classified.forEach(r=>counts[r.bucket]++);
    if(classified.length!==(counts.fwd+counts.hold+counts.mon+counts.low))
      console.warn('[PM v2] Coverage assertion failed');

    function pmSignalLine(res){{
      const matSigs=res.signals.filter(s=>s.material);
      if(!matSigs.length){{
        return'within '+PM_CFG.cBand+' pts of avg in '+res.inBand+'/'+res.n+' games · '+pmR1(res.allAvg.mins)+'min/g';
      }}
      return matSigs.map(s=>{{
        const goodCol=s.good?'var(--windk)':'var(--lossdk)';
        return'<span style="color:'+goodCol+';font-weight:600;">'+s.label+' '+(s.delta>0?'up':'down')+' '+pmR1(s.base)+'→'+pmR1(s.rec)+'</span>';
      }}).join(' · ')+(res.mixed?' <span style="font-size:10px;font-weight:700;background:var(--lossbg);color:var(--lossdk);padding:1px 5px;border-radius:3px;margin-left:4px;">MIXED</span>':'');
    }}

    function pmCard(res){{
      return'<div style="padding:9px 12px;border-bottom:1px solid var(--line2);">'+
        '<div style="font-weight:700;font-size:13px;">'+res.displayName+'</div>'+
        '<div style="font-size:11.5px;color:var(--ink2);margin-top:3px;line-height:1.5;">'+pmSignalLine(res)+'</div>'+
        '</div>';
    }}

    const PM_COLS=[
      {{k:'fwd',  color:'var(--windk)',   bg:'var(--winbg)',   brd:'rgba(26,158,114,.25)', ttl:'▲ Moving forward',   desc:'Material gains, no material declines.'}},
      {{k:'hold', color:'var(--vjbl)',    bg:'var(--vjblbg)',  brd:'rgba(45,111,181,.2)',  ttl:'● Holding standard', desc:'Steady at level — reliable, coachable.'}},
      {{k:'mon',  color:'var(--lossdk)', bg:'var(--lossbg)',  brd:'rgba(217,65,63,.2)',   ttl:'▼ Monitor closely',  desc:'Material declines or conflicting signals.'}},
      {{k:'low',  color:'var(--amber)',  bg:'var(--amberbg)', brd:'rgba(200,125,26,.2)',  ttl:'◆ Steady and low',   desc:'Below contribution gate — rotation flag.'}}
    ];

    h+='<div class="card">';
    h+='<div class="sec-h">Player movement &nbsp;·&nbsp; <span style="font-weight:400;text-transform:none;letter-spacing:0;font-size:11px;color:var(--muted);">v2.0 · split-half (G1–'+Math.floor(pmN/2)+' vs G'+(pmN-Math.floor(pmN/2)+1)+'–'+pmN+') · one verdict per player · 4+ games required</span></div>';
    h+='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-bottom:14px;">';
    PM_COLS.forEach(col=>{{
      const list=classified.filter(r=>r.bucket===col.k)
                           .sort((a,b)=>b.strength-a.strength||b.impact-a.impact);
      h+='<div style="border:1px solid '+col.brd+';border-radius:8px;overflow:hidden;background:#fff;">';
      h+='<div style="padding:9px 12px;background:'+col.bg+';border-bottom:1px solid '+col.brd+';">';
      h+='<div style="font-size:13px;font-weight:700;color:'+col.color+';display:flex;justify-content:space-between;align-items:center;">';
      h+=col.ttl+'<span style="font-size:11px;font-weight:700;padding:2px 7px;border-radius:9px;background:rgba(0,0,0,.06);color:'+col.color+';">'+list.length+'</span></div>';
      h+='<div style="font-size:11px;color:var(--muted);margin-top:2px;">'+col.desc+'</div>';
      h+='</div>';
      if(list.length){{
        list.forEach(res=>{{ h+=pmCard(res); }});
      }}else{{
        h+='<div style="padding:12px;font-size:12px;color:var(--muted);font-style:italic;">No players at current thresholds.</div>';
      }}
      h+='</div>';
    }});
    h+='</div>';
    if(unclassified.length){{
      h+='<div style="font-size:11.5px;color:var(--muted);padding:8px 2px;border-top:1px solid var(--line2);">';
      h+='<strong style="color:var(--ink2);">Not yet classified</strong> (fewer than '+PM_CFG.minGames+' games): ';
      h+=unclassified.map(r=>r.displayName+' ('+r.gamesPlayed+'g)').join(', ')+'.';
      h+='</div>';
    }}
    h+='<div style="font-size:11px;color:var(--muted);margin-top:10px;padding-top:8px;border-top:1px solid var(--line2);">One verdict per player · 15% relative band · team-normalised floors · minutes gate: '+pmR1(PM_AVAIL_MIN*PM_CFG.gMinPct)+'min avg · impact gate: '+pmR1(PM_CFG.gImpPct*100)+'% team share</div>';
    h+='</div>';
  }}

  return h;
}}"""


def template_block():
    """Template version — uses REPLACE_ placeholders for quarter/clock config."""
    return """  // ── PLAYER MOVEMENT v2.0 — four-bucket model (coach only) ──────────────────
  // BUILD:PM_CONFIG — set quarterLenSec and clockMode to match this team's competition format.
  // quarterLenSec: 420 = 7-min stop-clock (VC Reserve), 600 = 10-min running (standard VJBL)
  // clockMode: 'stopped' or 'running'
  // quarters: always 4 for VJBL
  // equalTimeRule: set true if competition mandates equal playing time (disables minutes signal)
  const PM_CFG={
    quarterLenSec:REPLACE_QUARTER_LENGTH_SEC,
    clockMode:'REPLACE_CLOCK_MODE',
    quarters:4,
    equalTimeRule:false,
    minGames:4,
    bandPct:0.15,
    floorPct:{pts:0.04, reb:0.04, ast:0.06, tov:0.04, mins:0.07},
    gMinPct:0.25,
    gImpPct:0.08,
    minBase:1.0,
    cBand:2
  };
  const PM_AVAIL_MIN=(PM_CFG.quarterLenSec*PM_CFG.quarters)/60;

  function pmTeamAvg(games,key){
    if(!games.length)return 1;
    const totals=games.map(g=>{
      let t=0;
      Object.keys(g.summary.stats||{}).forEach(pid=>{
        const s=g.summary.stats[pid]||{};
        if(key==='reb') t+=(s.oreb||0)+(s.dreb||0);
        else if(key==='mins') t+=g.summary.minutes[pid]||0;
        else t+=s[key]||0;
      });
      return t;
    });
    return totals.reduce((a,v)=>a+v,0)/totals.length||1;
  }

  function pmWindows(n){
    const half=Math.floor(n/2);
    return{base:[...Array(half).keys()], rec:[...Array(n).keys()].slice(-half)};
  }

  function pmMean(arr){ return arr.length?arr.reduce((s,v)=>s+v,0)/arr.length:0; }
  function pmR1(n){ const v=Math.round(n*10)/10; return Number.isInteger(v)?v.toFixed(0):v.toFixed(1); }

  function pmClassify(pid,games,teamAvg,teamImpactPG){
    const n=games.length;
    if(n<PM_CFG.minGames) return{bucket:'unclassified',n,signals:[],strength:0,impact:0,impShare:0,minShare:0,inBand:0};
    const w=pmWindows(n);
    const METRICS=[
      {k:'pts', dir:+1, vals:games.map(g=>(g.summary.stats[pid]||{}).pts||0), tavgKey:'pts'},
      {k:'reb', dir:+1, vals:games.map(g=>{const s=g.summary.stats[pid]||{};return(s.oreb||0)+(s.dreb||0);}), tavgKey:'reb'},
      {k:'ast', dir:+1, vals:games.map(g=>(g.summary.stats[pid]||{}).ast||0), tavgKey:'ast'},
      {k:'tov', dir:-1, vals:games.map(g=>(g.summary.stats[pid]||{}).tov||0), tavgKey:'tov'},
      {k:'mins',dir:+1, vals:games.map(g=>g.summary.minutes[pid]||0), tavgKey:'mins'}
    ];
    let gains=0,losses=0;
    const signals=[];
    METRICS.forEach(m=>{
      const base=pmMean(w.base.map(i=>m.vals[i]));
      const rec =pmMean(w.rec.map(i=>m.vals[i]));
      const delta=rec-base;
      const absFloor=(m.tavgKey==='mins'?PM_AVAIL_MIN:teamAvg[m.tavgKey])*PM_CFG.floorPct[m.k];
      const relFloor=base*PM_CFG.bandPct;
      const thr=Math.max(absFloor,relFloor,0.01);
      const suppressed=base<PM_CFG.minBase;
      const material=!suppressed&&Math.abs(delta)>=thr;
      const good=m.dir>0?delta>0:delta<0;
      signals.push({k:m.k,base,rec,delta,thr,material,good,suppressed,
        label:{pts:'scoring',reb:'rebounds',ast:'assists',tov:'turnovers',mins:'minutes'}[m.k]});
      if(material){ good?gains++:losses++; }
    });
    const allAvg={};
    METRICS.forEach(m=>allAvg[m.k]=pmMean(m.vals));
    const impact=allAvg.pts+0.7*allAvg.reb+1.5*allAvg.ast-0.5*allAvg.tov;
    const impShare=teamImpactPG>0?(impact/teamImpactPG*100):0;
    const minShare=(allAvg.mins/PM_AVAIL_MIN)*100;
    const ptsAll=METRICS.find(m=>m.k==='pts').vals;
    const inBand=ptsAll.filter(v=>Math.abs(v-allAvg.pts)<=PM_CFG.cBand).length;
    const mixed=gains>0&&losses>0;
    let bucket;
    if     (gains>0&&losses===0) bucket='fwd';
    else if(losses>0&&gains===0) bucket='mon';
    else if(mixed)               bucket='mon';
    else bucket=(minShare>=PM_CFG.gMinPct*100&&impShare>=PM_CFG.gImpPct*100)?'hold':'low';
    const strength=signals.filter(s=>s.material).reduce((t,s)=>t+Math.abs(s.delta)/Math.max(s.thr,0.01),0);
    return{bucket,n,signals,gains,losses,mixed,strength,impact,impShare,minShare,inBand,allAvg};
  }

  const PM_ROSTER=Object.keys(d.team.roster||{}).map(Number);
  const pmGames=gs;
  const pmN=pmGames.length;

  if(pmN>=2){
    const pmTA={
      pts:pmTeamAvg(pmGames,'pts'), reb:pmTeamAvg(pmGames,'reb'),
      ast:pmTeamAvg(pmGames,'ast'), tov:pmTeamAvg(pmGames,'tov'),
      mins:PM_AVAIL_MIN
    };
    let pmTIpg=0;
    pmGames.forEach(g=>{
      let gi=0;
      Object.keys(g.summary.stats||{}).forEach(pid=>{
        const s=g.summary.stats[pid]||{};
        gi+=(s.pts||0)+0.7*((s.oreb||0)+(s.dreb||0))+1.5*(s.ast||0)-0.5*(s.tov||0);
      });
      pmTIpg+=gi;
    });
    pmTIpg=pmTIpg/pmGames.length||1;

    const pmResults=[];
    const allPids=new Set([
      ...PM_ROSTER,
      ...pmGames.flatMap(g=>Object.keys(g.summary.stats||{}).map(Number))
    ]);
    allPids.forEach(pid=>{
      const gamesPlayed=pmGames.filter(g=>(g.summary.minutes[pid]||0)>0).length;
      if(gamesPlayed===0) return;
      const res=pmClassify(pid,pmGames,pmTA,pmTIpg);
      res.pid=pid;
      res.displayName=pnum(d.names,pid)+' '+pname(d.names,pid);
      res.gamesPlayed=gamesPlayed;
      pmResults.push(res);
    });

    const classified=pmResults.filter(r=>r.bucket!=='unclassified');
    const unclassified=pmResults.filter(r=>r.bucket==='unclassified');
    const counts={fwd:0,hold:0,mon:0,low:0};
    classified.forEach(r=>counts[r.bucket]++);
    if(classified.length!==(counts.fwd+counts.hold+counts.mon+counts.low))
      console.warn('[PM v2] Coverage assertion failed');

    function pmSignalLine(res){
      const matSigs=res.signals.filter(s=>s.material);
      if(!matSigs.length){
        return'within '+PM_CFG.cBand+' pts of avg in '+res.inBand+'/'+res.n+' games · '+pmR1(res.allAvg.mins)+'min/g';
      }
      return matSigs.map(s=>{
        const goodCol=s.good?'var(--windk)':'var(--lossdk)';
        return'<span style="color:'+goodCol+';font-weight:600;">'+s.label+' '+(s.delta>0?'up':'down')+' '+pmR1(s.base)+'→'+pmR1(s.rec)+'</span>';
      }).join(' · ')+(res.mixed?' <span style="font-size:10px;font-weight:700;background:var(--lossbg);color:var(--lossdk);padding:1px 5px;border-radius:3px;margin-left:4px;">MIXED</span>':'');
    }

    function pmCard(res){
      return'<div style="padding:9px 12px;border-bottom:1px solid var(--line2);">'+
        '<div style="font-weight:700;font-size:13px;">'+res.displayName+'</div>'+
        '<div style="font-size:11.5px;color:var(--ink2);margin-top:3px;line-height:1.5;">'+pmSignalLine(res)+'</div>'+
        '</div>';
    }

    const PM_COLS=[
      {k:'fwd',  color:'var(--windk)',   bg:'var(--winbg)',   brd:'rgba(26,158,114,.25)', ttl:'▲ Moving forward',   desc:'Material gains, no material declines.'},
      {k:'hold', color:'var(--vjbl)',    bg:'var(--vjblbg)',  brd:'rgba(45,111,181,.2)',  ttl:'● Holding standard', desc:'Steady at level — reliable, coachable.'},
      {k:'mon',  color:'var(--lossdk)', bg:'var(--lossbg)',  brd:'rgba(217,65,63,.2)',   ttl:'▼ Monitor closely',  desc:'Material declines or conflicting signals.'},
      {k:'low',  color:'var(--amber)',  bg:'var(--amberbg)', brd:'rgba(200,125,26,.2)',  ttl:'◆ Steady and low',   desc:'Below contribution gate — rotation flag.'}
    ];

    h+='<div class="card">';
    h+='<div class="sec-h">Player movement &nbsp;·&nbsp; <span style="font-weight:400;text-transform:none;letter-spacing:0;font-size:11px;color:var(--muted);">v2.0 · split-half (G1–'+Math.floor(pmN/2)+' vs G'+(pmN-Math.floor(pmN/2)+1)+'–'+pmN+') · one verdict per player · 4+ games required</span></div>';
    h+='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-bottom:14px;">';
    PM_COLS.forEach(col=>{
      const list=classified.filter(r=>r.bucket===col.k)
                           .sort((a,b)=>b.strength-a.strength||b.impact-a.impact);
      h+='<div style="border:1px solid '+col.brd+';border-radius:8px;overflow:hidden;background:#fff;">';
      h+='<div style="padding:9px 12px;background:'+col.bg+';border-bottom:1px solid '+col.brd+';">';
      h+='<div style="font-size:13px;font-weight:700;color:'+col.color+';display:flex;justify-content:space-between;align-items:center;">';
      h+=col.ttl+'<span style="font-size:11px;font-weight:700;padding:2px 7px;border-radius:9px;background:rgba(0,0,0,.06);color:'+col.color+';">'+list.length+'</span></div>';
      h+='<div style="font-size:11px;color:var(--muted);margin-top:2px;">'+col.desc+'</div>';
      h+='</div>';
      if(list.length){
        list.forEach(res=>{ h+=pmCard(res); });
      }else{
        h+='<div style="padding:12px;font-size:12px;color:var(--muted);font-style:italic;">No players at current thresholds.</div>';
      }
      h+='</div>';
    });
    h+='</div>';
    if(unclassified.length){
      h+='<div style="font-size:11.5px;color:var(--muted);padding:8px 2px;border-top:1px solid var(--line2);">';
      h+='<strong style="color:var(--ink2);">Not yet classified</strong> (fewer than '+PM_CFG.minGames+' games): ';
      h+=unclassified.map(r=>r.displayName+' ('+r.gamesPlayed+'g)').join(', ')+'.';
      h+='</div>';
    }
    h+='<div style="font-size:11px;color:var(--muted);margin-top:10px;padding-top:8px;border-top:1px solid var(--line2);">One verdict per player · 15% relative band · team-normalised floors · minutes gate: '+pmR1(PM_AVAIL_MIN*PM_CFG.gMinPct)+'min avg · impact gate: '+pmR1(PM_CFG.gImpPct*100)+'% team share</div>';
    h+='</div>';
  }

  return h;
}"""


# ── PATCH FUNCTION ────────────────────────────────────────────────────────────
def patch_file(path, replacement, label):
    if not path.exists():
        print(f"  SKIP — file not found: {path}")
        return False

    src = path.read_text(encoding="utf-8")

    count = src.count(OLD_BLOCK)
    assert count == 1, (
        f"ANCHOR CHECK FAILED for {label}: expected 1 match, found {count}.\n"
        "Do NOT proceed — restore from backup and regenerate the patch."
    )

    bak = path.with_suffix(".html.bak")
    shutil.copy2(path, bak)

    patched = src.replace(OLD_BLOCK, replacement, 1)
    assert patched != src, f"Replace produced no change for {label}."

    path.write_text(patched, encoding="utf-8")
    print(f"  ✓ {label} — patched ({path.name}), backup → {bak.name}")
    return True


# ── RUN ───────────────────────────────────────────────────────────────────────
print("\nCourtTrack — Player Movement v2.0 patch\n" + "─"*44)

errors = []

# Live team files
for team in TEAMS:
    replacement = new_block(
        team["quarter_sec"],
        team["clock_mode"],
        team["quarters"],
        team["label"],
    )
    try:
        patch_file(team["file"], replacement, team["label"])
    except AssertionError as e:
        errors.append(str(e))
        print(f"  ✗ {team['label']} — {e}")

# Template
try:
    patch_file(TEMPLATE, template_block(), "TEMPLATE")
except AssertionError as e:
    errors.append(str(e))
    print(f"  ✗ TEMPLATE — {e}")

print("\n" + "─"*44)
if errors:
    print(f"COMPLETED WITH {len(errors)} ERROR(S) — check above.")
    sys.exit(1)
else:
    print("All files patched successfully.\n")
    print("Next steps:")
    print("  1. Open each team's coach dashboard locally (file://) and check")
    print("     Progression → Player Movement shows four columns")
    print("  2. Confirm Eltham 12.1 (already patched) still looks correct")
    print("  3. git pull  →  git status  →  git add .  →  git commit -m 'feat: player movement v2.0 four-bucket model — all 4 teams + template'  →  git push")
    print("  4. Verify on live URLs in incognito after push")
