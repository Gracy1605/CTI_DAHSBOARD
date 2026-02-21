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