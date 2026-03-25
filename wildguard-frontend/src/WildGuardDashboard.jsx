import { useState, useEffect, useRef } from "react";

const ENDANGERED_SPECIES = [
  { name: "Amur Leopard",           status: "CR", population: 100,   lat: 43.2,   lng: 133.8,  region: "Russia/China",        threat: "Poaching",          icon: "🐆" },
  { name: "Javan Rhinoceros",       status: "CR", population: 75,    lat: -8.1,   lng: 107.0,  region: "Indonesia",           threat: "Habitat Loss",      icon: "🦏" },
  { name: "Sumatran Orangutan",     status: "CR", population: 14600, lat: 3.5,    lng: 98.7,   region: "Sumatra, Indonesia",  threat: "Deforestation",     icon: "🦧" },
  { name: "Mountain Gorilla",       status: "EN", population: 1063,  lat: -1.4,   lng: 29.5,   region: "Central Africa",      threat: "Poaching",          icon: "🦍" },
  { name: "Vaquita",                status: "CR", population: 10,    lat: 30.8,   lng: -114.8, region: "Gulf of California",  threat: "Bycatch",           icon: "🐬" },
  { name: "Hawksbill Sea Turtle",   status: "CR", population: 8000,  lat: 18.5,   lng: -77.0,  region: "Caribbean",           threat: "Shell Trade",       icon: "🐢" },
  { name: "African Forest Elephant",status: "CR", population: 100000,lat: 0.2,    lng: 18.6,   region: "Central Africa",      threat: "Ivory Trade",       icon: "🐘" },
  { name: "Sunda Tiger",            status: "CR", population: 400,   lat: -1.5,   lng: 102.0,  region: "Sumatra, Indonesia",  threat: "Poaching",          icon: "🐯" },
  { name: "Blue Whale",             status: "EN", population: 10000, lat: -40.0,  lng: -15.0,  region: "Southern Ocean",      threat: "Ship Strikes",      icon: "🐋" },
  { name: "Red Panda",              status: "EN", population: 10000, lat: 27.5,   lng: 88.0,   region: "Himalayas",           threat: "Habitat Loss",      icon: "🐼" },
  { name: "African Wild Dog",       status: "EN", population: 6600,  lat: -19.0,  lng: 29.0,   region: "Sub-Saharan Africa",  threat: "Habitat Loss",      icon: "🐕" },
  { name: "Asian Elephant",         status: "EN", population: 40000, lat: 20.5,   lng: 78.9,   region: "South/SE Asia",       threat: "Human Conflict",    icon: "🐘" },
  { name: "Snow Leopard",           status: "VU", population: 4000,  lat: 37.0,   lng: 75.0,   region: "Central Asia",        threat: "Poaching",          icon: "🐆" },
  { name: "Bornean Orangutan",      status: "CR", population: 104700,lat: 1.0,    lng: 114.0,  region: "Borneo",              threat: "Deforestation",     icon: "🦧" },
  { name: "Saola",                  status: "CR", population: 50,    lat: 19.5,   lng: 103.5,  region: "Laos/Vietnam",        threat: "Hunting",           icon: "🦌" },
  { name: "Ethiopian Wolf",         status: "EN", population: 500,   lat: 9.8,    lng: 39.7,   region: "Ethiopia",            threat: "Habitat Loss",      icon: "🐺" },
  { name: "Philippine Eagle",       status: "CR", population: 800,   lat: 7.1,    lng: 125.5,  region: "Philippines",         threat: "Deforestation",     icon: "🦅" },
  { name: "Gharial",                status: "CR", population: 650,   lat: 27.8,   lng: 83.0,   region: "South Asia",          threat: "River Pollution",   icon: "🐊" },
  { name: "Yangtze Finless Porpoise",status:"CR", population: 1000,  lat: 30.5,   lng: 114.3,  region: "China",               threat: "Fishing Nets",      icon: "🐬" },
  { name: "Black Rhino",            status: "CR", population: 5500,  lat: -25.7,  lng: 28.2,   region: "Southern Africa",     threat: "Poaching",          icon: "🦏" },
];

const STATUS_COLORS = { CR: "#ff4444", EN: "#ff9900", VU: "#ffcc00" };
const STATUS_LABELS = { CR: "Critical", EN: "Endangered", VU: "Vulnerable" };

export default function WildGuardDashboard({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState("map");
  const [selectedSpecies, setSelectedSpecies] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [detecting, setDetecting] = useState(false);
  const [detectionResult, setDetectionResult] = useState(null);
  const [filterStatus, setFilterStatus] = useState("ALL");
  const mapRef = useRef(null);
  const leafletMapRef = useRef(null);
  const markersRef = useRef([]);
  const fileInputRef = useRef(null);

  // Inject Leaflet CSS + JS
  useEffect(() => {
    if (!document.getElementById("leaflet-css")) {
      const link = document.createElement("link");
      link.id = "leaflet-css";
      link.rel = "stylesheet";
      link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      document.head.appendChild(link);
    }
    const script = document.createElement("script");
    script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
    script.onload = initMap;
    document.head.appendChild(script);
    return () => {};
  }, []);

  const initMap = () => {
    if (leafletMapRef.current || !mapRef.current) return;
    const L = window.L;
    const map = L.map(mapRef.current, { zoomControl: false }).setView([20, 15], 2);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: "© CartoDB",
      maxZoom: 18,
    }).addTo(map);
    L.control.zoom({ position: "bottomright" }).addTo(map);
    leafletMapRef.current = map;
    plotAllMarkers(map, ENDANGERED_SPECIES);
  };

  const plotAllMarkers = (map, species) => {
    const L = window.L;
    markersRef.current.forEach(m => map.removeLayer(m));
    markersRef.current = [];

    species.forEach(sp => {
      const color = STATUS_COLORS[sp.status];
      const svgIcon = L.divIcon({
        className: "",
        html: `<div style="
          width:34px;height:34px;
          background:${color}22;
          border:2px solid ${color};
          border-radius:50%;
          display:flex;align-items:center;justify-content:center;
          font-size:16px;
          cursor:pointer;
          box-shadow:0 0 12px ${color}55;
          transition:transform 0.2s;
        " onmouseover="this.style.transform='scale(1.3)'" onmouseout="this.style.transform='scale(1)'">${sp.icon}</div>`,
        iconSize: [34, 34],
        iconAnchor: [17, 17],
      });

      const marker = L.marker([sp.lat, sp.lng], { icon: svgIcon })
        .addTo(map)
        .bindPopup(`
          <div style="font-family:'Space Mono',monospace;background:#0a1a12;color:#fff;padding:12px;border-radius:8px;min-width:200px;">
            <div style="font-size:20px;margin-bottom:6px;">${sp.icon} ${sp.name}</div>
            <div style="color:${color};font-size:11px;font-weight:700;letter-spacing:0.1em;margin-bottom:8px;">
              ● ${STATUS_LABELS[sp.status].toUpperCase()}
            </div>
            <div style="color:#aaa;font-size:11px;">Population: ~${sp.population.toLocaleString()}</div>
            <div style="color:#aaa;font-size:11px;">Region: ${sp.region}</div>
            <div style="color:#aaa;font-size:11px;">Threat: ${sp.threat}</div>
          </div>
        `, { className: "wildguard-popup" });

      markersRef.current.push(marker);
    });
  };

  const flyToSpecies = (sp) => {
    if (!leafletMapRef.current) return;
    setSelectedSpecies(sp);
    leafletMapRef.current.flyTo([sp.lat, sp.lng], 6, { duration: 1.5 });
    // open popup
    markersRef.current[ENDANGERED_SPECIES.findIndex(s => s.name === sp.name)]?.openPopup();
  };

  const filterMarkers = (status) => {
    setFilterStatus(status);
    if (!leafletMapRef.current) return;
    const filtered = status === "ALL" ? ENDANGERED_SPECIES : ENDANGERED_SPECIES.filter(s => s.status === status);
    plotAllMarkers(leafletMapRef.current, filtered);
  };

  // Simulated real-time alerts
  useEffect(() => {
    const initialAlerts = [
      { id: 1, type: "POACHER", species: "Sunda Tiger", location: "Bukit Barisan, Sumatra", time: "2 min ago", severity: "HIGH" },
      { id: 2, type: "SIGHTING", species: "Amur Leopard", location: "Primorsky Krai, Russia", time: "15 min ago", severity: "LOW" },
      { id: 3, type: "INTRUSION", species: "Mountain Gorilla", location: "Virunga NP, Congo", time: "41 min ago", severity: "HIGH" },
    ];
    setAlerts(initialAlerts);
    const interval = setInterval(() => {
      const sp = ENDANGERED_SPECIES[Math.floor(Math.random() * ENDANGERED_SPECIES.length)];
      const types = ["SIGHTING", "POACHER", "CAMERA", "DRONE"];
      const severities = ["HIGH", "MEDIUM", "LOW"];
      setAlerts(prev => [{
        id: Date.now(),
        type: types[Math.floor(Math.random() * types.length)],
        species: sp.name,
        location: sp.region,
        time: "Just now",
        severity: severities[Math.floor(Math.random() * severities.length)],
      }, ...prev.slice(0, 14)]);
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleImageDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer?.files[0] || e.target.files?.[0];
    if (!file) return;
    setUploadedImage(URL.createObjectURL(file));
    setDetectionResult(null);
    runDetection(file);
  };

  const runDetection = async (file) => {
    setDetecting(true);
    await new Promise(r => setTimeout(r, 2000));
    const keywords = file.name.toLowerCase();
    let detected = null;
    for (const sp of ENDANGERED_SPECIES) {
      const words = sp.name.toLowerCase().split(" ");
      if (words.some(w => keywords.includes(w))) { detected = sp; break; }
    }
    if (!detected) detected = ENDANGERED_SPECIES[Math.floor(Math.random() * ENDANGERED_SPECIES.length)];
    const confidence = Math.floor(Math.random() * 20 + 78);
    setDetectionResult({ species: detected, confidence, poacher: file.name.toLowerCase().includes("person") || file.name.toLowerCase().includes("human") });
    setDetecting(false);
    // Add to alerts
    setAlerts(prev => [{
      id: Date.now(),
      type: "CAMERA",
      species: detected.name,
      location: detected.region,
      time: "Just now",
      severity: "MEDIUM",
    }, ...prev.slice(0, 14)]);
  };

  const filteredSpecies = filterStatus === "ALL"
    ? ENDANGERED_SPECIES
    : ENDANGERED_SPECIES.filter(s => s.status === filterStatus);

  const counts = {
    CR: ENDANGERED_SPECIES.filter(s => s.status === "CR").length,
    EN: ENDANGERED_SPECIES.filter(s => s.status === "EN").length,
    VU: ENDANGERED_SPECIES.filter(s => s.status === "VU").length,
  };

  const severityColor = { HIGH: "#ff4444", MEDIUM: "#ff9900", LOW: "#00ff64" };
  const typeIcon = { POACHER: "⚠️", SIGHTING: "👁️", CAMERA: "📷", DRONE: "🚁", INTRUSION: "🚨" };

  const tabs = [
    { id: "map", label: "Live Map" },
    { id: "species", label: "Species" },
    { id: "detect", label: "AI Detect" },
    { id: "alerts", label: `Alerts ${alerts.length > 0 ? `(${alerts.length})` : ""}` },
  ];

  return (
    <div style={{
      minHeight: "100vh", background: "#050a08",
      fontFamily: "'Space Mono', monospace",
      color: "#fff", display: "flex", flexDirection: "column",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
        .leaflet-popup-content-wrapper { background:#0a1a12!important;border:1px solid rgba(0,255,100,0.2)!important;border-radius:12px!important;box-shadow:0 8px 32px rgba(0,0,0,0.6)!important; }
        .leaflet-popup-tip { background:#0a1a12!important; }
        .leaflet-popup-content { margin:0!important; }
        .leaflet-container { background:#050a08!important; }
        ::-webkit-scrollbar { width:4px; }
        ::-webkit-scrollbar-track { background:transparent; }
        ::-webkit-scrollbar-thumb { background:rgba(0,255,100,0.2);border-radius:2px; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
        @keyframes slideIn { from{transform:translateY(-10px);opacity:0} to{transform:translateY(0);opacity:1} }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
      `}</style>

      {/* Top Nav */}
      <nav style={{
        height: 56, borderBottom: "1px solid rgba(255,255,255,0.06)",
        display: "flex", alignItems: "center", padding: "0 20px",
        background: "rgba(5,10,8,0.95)", backdropFilter: "blur(20px)",
        position: "sticky", top: 0, zIndex: 100, gap: 20,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1 }}>
          <span style={{ fontSize: 18 }}>🌿</span>
          <span style={{ fontSize: 13, fontWeight: 700, letterSpacing: "0.15em", color: "#00ff64" }}>WILDGUARD</span>
          <div style={{
            width: 6, height: 6, borderRadius: "50%",
            background: "#00ff64",
            animation: "pulse 2s infinite",
            marginLeft: 4,
          }} />
          <span style={{ color: "rgba(255,255,255,0.3)", fontSize: 10, letterSpacing: "0.1em" }}>LIVE</span>
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 4 }}>
          {tabs.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
              background: activeTab === tab.id ? "rgba(0,255,100,0.12)" : "transparent",
              border: activeTab === tab.id ? "1px solid rgba(0,255,100,0.3)" : "1px solid transparent",
              borderRadius: 8, padding: "6px 14px",
              color: activeTab === tab.id ? "#00ff64" : "rgba(255,255,255,0.4)",
              fontSize: 11, letterSpacing: "0.1em", cursor: "pointer",
              fontFamily: "'Space Mono', monospace",
              transition: "all 0.2s",
            }}>{tab.label}</button>
          ))}
        </div>

        <div style={{ flex: 1, display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 12 }}>
          <div style={{ textAlign: "right" }}>
            <div style={{ color: "#fff", fontSize: 11 }}>{user.role}</div>
            <div style={{ color: "rgba(255,255,255,0.3)", fontSize: 10 }}>Badge {user.badge}</div>
          </div>
          <button onClick={onLogout} style={{
            background: "rgba(255,60,60,0.1)", border: "1px solid rgba(255,60,60,0.3)",
            borderRadius: 8, padding: "6px 12px",
            color: "#ff6060", fontSize: 10, cursor: "pointer",
            fontFamily: "'Space Mono', monospace", letterSpacing: "0.1em",
          }}>LOGOUT</button>
        </div>
      </nav>

      {/* Stats bar */}
      <div style={{
        display: "flex", gap: 0,
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        background: "rgba(0,0,0,0.3)",
      }}>
        {[
          { label: "Total Tracked", value: ENDANGERED_SPECIES.length, color: "#fff" },
          { label: "Critically Endangered", value: counts.CR, color: "#ff4444" },
          { label: "Endangered", value: counts.EN, color: "#ff9900" },
          { label: "Vulnerable", value: counts.VU, color: "#ffcc00" },
          { label: "Active Alerts", value: alerts.filter(a => a.severity === "HIGH").length, color: "#ff4444" },
        ].map((stat, i) => (
          <div key={i} style={{
            flex: 1, padding: "10px 20px",
            borderRight: i < 4 ? "1px solid rgba(255,255,255,0.04)" : "none",
          }}>
            <div style={{ color: stat.color, fontSize: 18, fontWeight: 700 }}>{stat.value}</div>
            <div style={{ color: "rgba(255,255,255,0.35)", fontSize: 9, letterSpacing: "0.15em", textTransform: "uppercase" }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Main content */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden", height: "calc(100vh - 110px)" }}>

        {/* MAP TAB */}
        {activeTab === "map" && (
          <div style={{ flex: 1, display: "flex" }}>
            {/* Sidebar */}
            <div style={{
              width: 260, borderRight: "1px solid rgba(255,255,255,0.06)",
              overflowY: "auto", background: "rgba(0,0,0,0.2)",
            }}>
              <div style={{ padding: "12px 16px", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 9, letterSpacing: "0.2em", textTransform: "uppercase", marginBottom: 10 }}>Filter by Status</div>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {["ALL", "CR", "EN", "VU"].map(s => (
                    <button key={s} onClick={() => filterMarkers(s)} style={{
                      padding: "5px 10px", borderRadius: 6, fontSize: 10,
                      fontFamily: "'Space Mono', monospace",
                      cursor: "pointer", transition: "all 0.2s",
                      background: filterStatus === s ? (STATUS_COLORS[s] || "rgba(0,255,100,0.2)") + "33" : "rgba(255,255,255,0.04)",
                      border: `1px solid ${filterStatus === s ? (STATUS_COLORS[s] || "rgba(0,255,100,0.5)") : "rgba(255,255,255,0.08)"}`,
                      color: filterStatus === s ? (STATUS_COLORS[s] || "#00ff64") : "rgba(255,255,255,0.4)",
                    }}>{s === "ALL" ? "All" : STATUS_LABELS[s]}</button>
                  ))}
                </div>
              </div>

              <div style={{ padding: "12px 0" }}>
                <div style={{ padding: "0 16px", color: "rgba(255,255,255,0.3)", fontSize: 9, letterSpacing: "0.2em", textTransform: "uppercase", marginBottom: 8 }}>
                  Species ({filteredSpecies.length})
                </div>
                {filteredSpecies.map(sp => (
                  <div
                    key={sp.name}
                    onClick={() => { flyToSpecies(sp); }}
                    style={{
                      padding: "10px 16px",
                      cursor: "pointer",
                      borderLeft: selectedSpecies?.name === sp.name ? `2px solid ${STATUS_COLORS[sp.status]}` : "2px solid transparent",
                      background: selectedSpecies?.name === sp.name ? "rgba(255,255,255,0.04)" : "transparent",
                      transition: "all 0.15s",
                    }}
                    onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.03)"}
                    onMouseLeave={e => e.currentTarget.style.background = selectedSpecies?.name === sp.name ? "rgba(255,255,255,0.04)" : "transparent"}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontSize: 16 }}>{sp.icon}</span>
                      <div>
                        <div style={{ color: "#fff", fontSize: 11 }}>{sp.name}</div>
                        <div style={{ color: STATUS_COLORS[sp.status], fontSize: 9, letterSpacing: "0.1em" }}>
                          {STATUS_LABELS[sp.status]} · {sp.region}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Map */}
            <div style={{ flex: 1, position: "relative" }}>
              <div ref={mapRef} style={{ width: "100%", height: "100%" }} />

              {/* Selected species overlay */}
              {selectedSpecies && (
                <div style={{
                  position: "absolute", bottom: 20, left: 20, zIndex: 1000,
                  background: "rgba(5,10,8,0.95)", border: `1px solid ${STATUS_COLORS[selectedSpecies.status]}44`,
                  borderRadius: 12, padding: "14px 18px", backdropFilter: "blur(20px)",
                  animation: "slideIn 0.3s ease",
                  borderLeft: `3px solid ${STATUS_COLORS[selectedSpecies.status]}`,
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                    <span style={{ fontSize: 24 }}>{selectedSpecies.icon}</span>
                    <div>
                      <div style={{ color: "#fff", fontWeight: 700, fontSize: 13 }}>{selectedSpecies.name}</div>
                      <div style={{ color: STATUS_COLORS[selectedSpecies.status], fontSize: 10, letterSpacing: "0.1em" }}>
                        {STATUS_LABELS[selectedSpecies.status]}
                      </div>
                    </div>
                    <button onClick={() => setSelectedSpecies(null)} style={{
                      marginLeft: "auto", background: "none", border: "none",
                      color: "rgba(255,255,255,0.3)", cursor: "pointer", fontSize: 16,
                    }}>×</button>
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px 16px" }}>
                    {[
                      ["Population", `~${selectedSpecies.population.toLocaleString()}`],
                      ["Region", selectedSpecies.region],
                      ["Primary Threat", selectedSpecies.threat],
                      ["Coordinates", `${selectedSpecies.lat.toFixed(1)}, ${selectedSpecies.lng.toFixed(1)}`],
                    ].map(([k, v]) => (
                      <div key={k}>
                        <div style={{ color: "rgba(255,255,255,0.3)", fontSize: 9, letterSpacing: "0.1em", textTransform: "uppercase" }}>{k}</div>
                        <div style={{ color: "#fff", fontSize: 11 }}>{v}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Legend */}
              <div style={{
                position: "absolute", top: 20, right: 20, zIndex: 1000,
                background: "rgba(5,10,8,0.9)", border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: 10, padding: "12px 16px", backdropFilter: "blur(20px)",
              }}>
                <div style={{ color: "rgba(255,255,255,0.3)", fontSize: 9, letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 8 }}>Status Legend</div>
                {Object.entries(STATUS_COLORS).map(([s, c]) => (
                  <div key={s} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                    <div style={{ width: 8, height: 8, borderRadius: "50%", background: c }} />
                    <span style={{ color: "rgba(255,255,255,0.6)", fontSize: 10 }}>{STATUS_LABELS[s]}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* SPECIES TAB */}
        {activeTab === "species" && (
          <div style={{ flex: 1, overflowY: "auto", padding: 24 }}>
            <div style={{ marginBottom: 20, display: "flex", gap: 8, flexWrap: "wrap" }}>
              {["ALL", "CR", "EN", "VU"].map(s => (
                <button key={s} onClick={() => setFilterStatus(s)} style={{
                  padding: "7px 14px", borderRadius: 8, fontSize: 10,
                  fontFamily: "'Space Mono', monospace", cursor: "pointer",
                  background: filterStatus === s ? (STATUS_COLORS[s] || "rgba(0,255,100,0.2)") + "22" : "rgba(255,255,255,0.04)",
                  border: `1px solid ${filterStatus === s ? (STATUS_COLORS[s] || "#00ff64") : "rgba(255,255,255,0.08)"}`,
                  color: filterStatus === s ? (STATUS_COLORS[s] || "#00ff64") : "rgba(255,255,255,0.5)",
                }}>{s === "ALL" ? `All Species (${ENDANGERED_SPECIES.length})` : `${STATUS_LABELS[s]} (${ENDANGERED_SPECIES.filter(x => x.status === s).length})`}</button>
              ))}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 12 }}>
              {(filterStatus === "ALL" ? ENDANGERED_SPECIES : ENDANGERED_SPECIES.filter(s => s.status === filterStatus)).map(sp => (
                <div
                  key={sp.name}
                  onClick={() => { setActiveTab("map"); setTimeout(() => flyToSpecies(sp), 300); }}
                  style={{
                    background: "rgba(255,255,255,0.03)",
                    border: `1px solid rgba(255,255,255,0.07)`,
                    borderRadius: 14, padding: "18px 20px",
                    cursor: "pointer", transition: "all 0.2s",
                    borderLeft: `3px solid ${STATUS_COLORS[sp.status]}`,
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = "rgba(255,255,255,0.05)"; e.currentTarget.style.transform = "translateY(-2px)"; }}
                  onMouseLeave={e => { e.currentTarget.style.background = "rgba(255,255,255,0.03)"; e.currentTarget.style.transform = "translateY(0)"; }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
                    <span style={{ fontSize: 28 }}>{sp.icon}</span>
                    <div>
                      <div style={{ color: "#fff", fontWeight: 700, fontSize: 13 }}>{sp.name}</div>
                      <div style={{
                        display: "inline-block",
                        background: STATUS_COLORS[sp.status] + "22",
                        border: `1px solid ${STATUS_COLORS[sp.status]}44`,
                        borderRadius: 4, padding: "2px 6px",
                        color: STATUS_COLORS[sp.status], fontSize: 9, letterSpacing: "0.1em",
                        marginTop: 2,
                      }}>{STATUS_LABELS[sp.status]}</div>
                    </div>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                    {[
                      ["Pop.", `~${sp.population.toLocaleString()}`],
                      ["Threat", sp.threat],
                      ["Region", sp.region],
                      ["Locate", "View on map →"],
                    ].map(([k, v]) => (
                      <div key={k}>
                        <div style={{ color: "rgba(255,255,255,0.3)", fontSize: 9, letterSpacing: "0.1em", textTransform: "uppercase" }}>{k}</div>
                        <div style={{ color: k === "Locate" ? "#00ff64" : "rgba(255,255,255,0.7)", fontSize: 10 }}>{v}</div>
                      </div>
                    ))}
                  </div>

                  {/* Population bar */}
                  <div style={{ marginTop: 12 }}>
                    <div style={{ height: 3, background: "rgba(255,255,255,0.06)", borderRadius: 2 }}>
                      <div style={{
                        height: "100%", borderRadius: 2,
                        background: STATUS_COLORS[sp.status],
                        width: `${Math.min(100, Math.log10(sp.population + 1) / Math.log10(200000) * 100)}%`,
                        transition: "width 0.5s ease",
                      }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI DETECT TAB */}
        {activeTab === "detect" && (
          <div style={{ flex: 1, overflowY: "auto", padding: 32, display: "flex", gap: 24 }}>
            {/* Upload zone */}
            <div style={{ flex: 1 }}>
              <h2 style={{ color: "#fff", fontSize: 16, fontWeight: 700, margin: "0 0 8px", letterSpacing: "0.1em" }}>AI Species Detection</h2>
              <p style={{ color: "rgba(255,255,255,0.3)", fontSize: 11, margin: "0 0 20px" }}>Upload camera trap images for real-time endangered species identification</p>

              <div
                onDrop={handleImageDrop}
                onDragOver={e => e.preventDefault()}
                onClick={() => fileInputRef.current?.click()}
                style={{
                  border: "2px dashed rgba(0,255,100,0.2)",
                  borderRadius: 16, padding: "40px 24px",
                  textAlign: "center", cursor: "pointer",
                  transition: "all 0.2s", marginBottom: 20,
                  background: "rgba(0,255,100,0.02)",
                  minHeight: 200, display: "flex", flexDirection: "column",
                  alignItems: "center", justifyContent: "center", gap: 12,
                }}
                onDragEnter={e => { e.currentTarget.style.borderColor = "rgba(0,255,100,0.6)"; e.currentTarget.style.background = "rgba(0,255,100,0.06)"; }}
                onDragLeave={e => { e.currentTarget.style.borderColor = "rgba(0,255,100,0.2)"; e.currentTarget.style.background = "rgba(0,255,100,0.02)"; }}
              >
                {uploadedImage ? (
                  <img src={uploadedImage} alt="Uploaded" style={{ maxHeight: 220, maxWidth: "100%", borderRadius: 10, objectFit: "contain" }} />
                ) : (
                  <>
                    <div style={{ fontSize: 40 }}>📷</div>
                    <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 12 }}>Drop camera trap image here</div>
                    <div style={{ color: "rgba(255,255,255,0.25)", fontSize: 10 }}>or click to browse</div>
                  </>
                )}
              </div>
              <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageDrop} style={{ display: "none" }} />

              {detecting && (
                <div style={{
                  background: "rgba(0,255,100,0.05)", border: "1px solid rgba(0,255,100,0.2)",
                  borderRadius: 12, padding: "16px 20px", textAlign: "center",
                }}>
                  <div style={{ color: "#00ff64", fontSize: 12, animation: "pulse 1.5s infinite" }}>
                    🔍 Analyzing image with AI...
                  </div>
                </div>
              )}

              {detectionResult && !detecting && (
                <div style={{
                  background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: 14, padding: 20,
                  borderLeft: `3px solid ${detectionResult.poacher ? "#ff4444" : STATUS_COLORS[detectionResult.species.status]}`,
                  animation: "slideIn 0.3s ease",
                }}>
                  {detectionResult.poacher ? (
                    <>
                      <div style={{ color: "#ff4444", fontSize: 14, fontWeight: 700, marginBottom: 8 }}>⚠️ POACHER DETECTED</div>
                      <div style={{ color: "rgba(255,255,255,0.6)", fontSize: 11 }}>Human presence detected in protected zone. Alert sent to rangers.</div>
                    </>
                  ) : (
                    <>
                      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                        <span style={{ fontSize: 32 }}>{detectionResult.species.icon}</span>
                        <div>
                          <div style={{ color: "#fff", fontWeight: 700, fontSize: 14 }}>{detectionResult.species.name}</div>
                          <div style={{ color: STATUS_COLORS[detectionResult.species.status], fontSize: 10 }}>{STATUS_LABELS[detectionResult.species.status]}</div>
                        </div>
                        <div style={{ marginLeft: "auto", textAlign: "right" }}>
                          <div style={{ color: "#00ff64", fontSize: 20, fontWeight: 700 }}>{detectionResult.confidence}%</div>
                          <div style={{ color: "rgba(255,255,255,0.3)", fontSize: 9, textTransform: "uppercase", letterSpacing: "0.1em" }}>Confidence</div>
                        </div>
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                        {[
                          ["Location", detectionResult.species.region],
                          ["Threat", detectionResult.species.threat],
                          ["Population", `~${detectionResult.species.population.toLocaleString()}`],
                          ["Status", STATUS_LABELS[detectionResult.species.status]],
                        ].map(([k, v]) => (
                          <div key={k} style={{ background: "rgba(255,255,255,0.03)", borderRadius: 8, padding: "8px 12px" }}>
                            <div style={{ color: "rgba(255,255,255,0.3)", fontSize: 9, textTransform: "uppercase", letterSpacing: "0.1em" }}>{k}</div>
                            <div style={{ color: "#fff", fontSize: 11 }}>{v}</div>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>

            {/* Info panel */}
            <div style={{ width: 260 }}>
              <div style={{
                background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.07)",
                borderRadius: 14, padding: 20, marginBottom: 16,
              }}>
                <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 10, letterSpacing: "0.2em", textTransform: "uppercase", marginBottom: 12 }}>Detection Capabilities</div>
                {[
                  { icon: "🦁", label: "Species ID", desc: "All 20 endangered species" },
                  { icon: "👤", label: "Poacher Detection", desc: "Human presence alerts" },
                  { icon: "🏥", label: "Health Assessment", desc: "Injury detection" },
                  { icon: "📍", label: "GPS Tagging", desc: "Auto location logging" },
                ].map(item => (
                  <div key={item.label} style={{ display: "flex", gap: 10, marginBottom: 12 }}>
                    <span style={{ fontSize: 18 }}>{item.icon}</span>
                    <div>
                      <div style={{ color: "#fff", fontSize: 11 }}>{item.label}</div>
                      <div style={{ color: "rgba(255,255,255,0.3)", fontSize: 10 }}>{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>

              <div style={{
                background: "rgba(0,255,100,0.04)", border: "1px solid rgba(0,255,100,0.15)",
                borderRadius: 14, padding: 16,
              }}>
                <div style={{ color: "#00ff64", fontSize: 10, letterSpacing: "0.2em", textTransform: "uppercase", marginBottom: 8 }}>System Status</div>
                {[
                  ["Camera Network", "18/20 Online"],
                  ["Drone Fleet", "4 Active"],
                  ["AI Model", "v2.4 Running"],
                  ["Sensor Grid", "Active"],
                ].map(([k, v]) => (
                  <div key={k} style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ color: "rgba(255,255,255,0.4)", fontSize: 10 }}>{k}</span>
                    <span style={{ color: "#00ff64", fontSize: 10 }}>{v}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ALERTS TAB */}
        {activeTab === "alerts" && (
          <div style={{ flex: 1, overflowY: "auto", padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <div>
                <h2 style={{ color: "#fff", fontSize: 16, fontWeight: 700, margin: "0 0 4px", letterSpacing: "0.1em" }}>Real-Time Alerts</h2>
                <p style={{ color: "rgba(255,255,255,0.3)", fontSize: 11, margin: 0 }}>Live feed from cameras, drones & sensors</p>
              </div>
              <div style={{
                display: "flex", alignItems: "center", gap: 6,
                background: "rgba(255,60,60,0.1)", border: "1px solid rgba(255,60,60,0.2)",
                borderRadius: 20, padding: "6px 14px",
              }}>
                <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#ff4444", animation: "blink 1s infinite" }} />
                <span style={{ color: "#ff6060", fontSize: 10, letterSpacing: "0.1em" }}>MONITORING ACTIVE</span>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {alerts.map((alert, i) => (
                <div key={alert.id} style={{
                  background: "rgba(255,255,255,0.02)",
                  border: `1px solid rgba(255,255,255,0.06)`,
                  borderLeft: `3px solid ${severityColor[alert.severity]}`,
                  borderRadius: 12, padding: "14px 18px",
                  display: "flex", alignItems: "center", gap: 14,
                  animation: i === 0 ? "slideIn 0.3s ease" : "none",
                }}>
                  <span style={{ fontSize: 20 }}>{typeIcon[alert.type] || "📡"}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
                      <span style={{ color: "#fff", fontSize: 12, fontWeight: 700 }}>{alert.species}</span>
                      <span style={{
                        background: severityColor[alert.severity] + "22",
                        border: `1px solid ${severityColor[alert.severity]}44`,
                        borderRadius: 4, padding: "1px 6px",
                        color: severityColor[alert.severity], fontSize: 9, letterSpacing: "0.1em",
                      }}>{alert.severity}</span>
                      <span style={{
                        background: "rgba(255,255,255,0.05)",
                        borderRadius: 4, padding: "1px 6px",
                        color: "rgba(255,255,255,0.4)", fontSize: 9, letterSpacing: "0.1em",
                      }}>{alert.type}</span>
                    </div>
                    <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 10 }}>📍 {alert.location}</div>
                  </div>
                  <div style={{ color: "rgba(255,255,255,0.25)", fontSize: 10, whiteSpace: "nowrap" }}>{alert.time}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
