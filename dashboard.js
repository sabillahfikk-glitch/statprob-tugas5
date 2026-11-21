(function () {
  "use strict";

  const RAW = window.SLEEP_DATA || [];
  const charts = {};
  const WARNA = {
    biru: "#2e5c8a",
    biruMuda: "#5b9bd5",
    hijau: "#82c99a",
    oranye: "#e8a87c",
    abu: "#5b6b7b"
  };

  function el(id) {
    return document.getElementById(id);
  }

  function setIsi(id, nilai) {
    const node = el(id);
    if (node) node.textContent = nilai;
  }

  function nilaiUnik(kunci) {
    return Array.from(new Set(RAW.map(function (r) { return r[kunci]; }))).sort();
  }

  function isiSelect(id, kunci) {
    const select = el(id);
    if (!select) return;
    nilaiUnik(kunci).forEach(function (nilai) {
      const opsi = document.createElement("option");
      opsi.value = nilai;
      opsi.textContent = nilai;
      select.appendChild(opsi);
    });
  }

  function filtered() {
    const f = el("filter-fakultas");
    const g = el("filter-gender");
    const k = el("filter-kafein");
    const nf = f ? f.value : "";
    const ng = g ? g.value : "";
    const nk = k ? k.value : "";
    return RAW.filter(function (r) {
      return (!nf || r.Fakultas === nf) &&
             (!ng || r.Jenis_Kelamin === ng) &&
             (!nk || r.Konsumsi_Kafein === nk);
    });
  }

  function ratarata(rows, kunci) {
    if (!rows.length) return null;
    let total = 0;
    rows.forEach(function (r) { total += Number(r[kunci]); });
    return total / rows.length;
  }

  function dikelompokkan(rows, kunci) {
    const peta = new Map();
    rows.forEach(function (r) {
      const kunciGrup = r[kunci];
      if (!peta.has(kunciGrup)) peta.set(kunciGrup, []);
      peta.get(kunciGrup).push(r);
    });
    return peta;
  }

  function renderKPI(rows) {
    setIsi("kpi-n", String(rows.length));
    const tidur = ratarata(rows, "Durasi_Tidur_Jam");
    const stres = ratarata(rows, "Skor_Stres");
    const ipk = ratarata(rows, "IPK");
    setIsi("kpi-tidur", tidur === null ? "—" : tidur.toFixed(2));
    setIsi("kpi-stres", stres === null ? "—" : stres.toFixed(1));
    setIsi("kpi-ipk", ipk === null ? "—" : ipk.toFixed(2));
  }

  function hapusChart() {
    Object.keys(charts).forEach(function (id) {
      if (charts[id] && typeof charts[id].destroy === "function") charts[id].destroy();
      delete charts[id];
    });
  }

  function renderCharts(rows) {
    if (typeof Chart === "undefined") return;
    hapusChart();
    Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif";
    Chart.defaults.color = WARNA.abu;

    const groups = dikelompokkan(rows, "Fakultas");
    const fakultas = Array.from(groups.keys()).sort();
    const opsi = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } };

    if (el("chart-fakultas")) {
      charts.fakultas = new Chart(el("chart-fakultas"), {
        type: "bar",
        data: {
          labels: fakultas,
          datasets: [{
            label: "Jumlah responden",
            data: fakultas.map(function (f) { return groups.get(f).length; }),
            backgroundColor: WARNA.biruMuda,
            borderRadius: 6
          }]
        },
        options: opsi
      });
    }

    const kafein = dikelompokkan(rows, "Konsumsi_Kafein");
    if (el("chart-kafein")) {
      charts.kafein = new Chart(el("chart-kafein"), {
        type: "doughnut",
        data: {
          labels: Array.from(kafein.keys()),
          datasets: [{
            data: Array.from(kafein.keys()).map(function (k) { return kafein.get(k).length; }),
            backgroundColor: [WARNA.biruMuda, WARNA.oranye, WARNA.hijau]
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });
    }

    if (el("chart-tidur-stres")) {
      charts.scat = new Chart(el("chart-tidur-stres"), {
        type: "scatter",
        data: {
          datasets: [{
            label: "Responden",
            data: rows.map(function (r) {
              return { x: Number(r.Durasi_Tidur_Jam), y: Number(r.Skor_Stres) };
            }),
            backgroundColor: WARNA.biruMuda,
            pointRadius: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { title: { display: true, text: "Durasi tidur (jam)" } },
            y: { title: { display: true, text: "Skor stres" } }
          }
        }
      });
    }

    if (el("chart-ipk-fakultas")) {
      charts.ipk = new Chart(el("chart-ipk-fakultas"), {
        type: "bar",
        data: {
          labels: fakultas,
          datasets: [
            {
              label: "Rata-rata IPK",
              data: fakultas.map(function (f) { return ratarata(groups.get(f), "IPK") || 0; }),
              backgroundColor: WARNA.biruMuda,
              yAxisID: "y"
            },
            {
              label: "Rata-rata stres / 10",
              data: fakultas.map(function (f) { return (ratarata(groups.get(f), "Skor_Stres") || 0) / 10; }),
              backgroundColor: WARNA.hijau,
              yAxisID: "y1"
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { type: "linear", position: "left", title: { display: true, text: "IPK" } },
            y1: {
              type: "linear", position: "right", grid: { drawOnChartArea: false },
              title: { display: true, text: "Skor stres / 10" }
            }
          }
        }
      });
    }
  }

  function renderTable(rows) {
    const badan = el("ringkasan-body");
    if (!badan) return;
    badan.innerHTML = "";
    const groups = dikelompokkan(rows, "Fakultas");
    Array.from(groups.keys()).sort().forEach(function (fakultas) {
      const grup = groups.get(fakultas);
      const tr = document.createElement("tr");
      const nilai = [
        fakultas,
        String(grup.length),
        (ratarata(grup, "Durasi_Tidur_Jam") || 0).toFixed(2),
        (ratarata(grup, "Skor_Stres") || 0).toFixed(1),
        (ratarata(grup, "IPK") || 0).toFixed(2)
      ];
      nilai.forEach(function (teks) {
        const td = document.createElement("td");
        td.textContent = teks;
        tr.appendChild(td);
      });
      badan.appendChild(tr);
    });
  }

  function render() {
    const rows = filtered();
    renderKPI(rows);
    renderCharts(rows);
    renderTable(rows);
  }

  function init() {
    isiSelect("filter-fakultas", "Fakultas");
    isiSelect("filter-gender", "Jenis_Kelamin");
    isiSelect("filter-kafein", "Konsumsi_Kafein");

    ["filter-fakultas", "filter-gender", "filter-kafein"].forEach(function (id) {
      const node = el(id);
      if (node) node.addEventListener("change", render);
    });

    const reset = el("filter-reset");
    if (reset) {
      reset.addEventListener("click", function () {
        ["filter-fakultas", "filter-gender", "filter-kafein"].forEach(function (id) {
          const node = el(id);
          if (node) node.value = "";
        });
        render();
      });
    }

    render();
  }

  window.__dashboard = { filtered: filtered };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
