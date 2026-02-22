document.addEventListener("DOMContentLoaded", function () {

  const severityCtx = document.getElementById("severityChart");
  const distributionCtx = document.getElementById("distributionChart");

  new Chart(severityCtx, {
    type: "bar",
    data: {
      labels: ["High", "Medium", "Low"],
      datasets: [{
        label: "Threat Severity",
        data: [40, 50, 35]
      }]
    }
  });

  new Chart(distributionCtx, {
    type: "pie",
    data: {
      labels: ["High", "Medium", "Low"],
      datasets: [{
        data: [40, 50, 35]
      }]
    }
  });

});
const filter = document.getElementById("severityFilter");

filter.addEventListener("change", function () {
  const selected = this.value;
  const rows = document.querySelectorAll("#threatTable tr");

  rows.forEach(row => {
    if (selected === "All" || row.dataset.severity === selected) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
});
function fetchThreatData() {
  console.log("Fetching data from backend API...");
  // Placeholder for future API call
}

fetchThreatData();