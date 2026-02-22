document.addEventListener('DOMContentLoaded', () => {
  // dummy statistics
  const stats = {
    total: 1234,
    high: 321,
    medium: 654,
    low: 259,
    trends: [12, 19, 3, 5, 2, 3, 7],
    trendLabels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
    threats: [
      {id: 'T-1001', title: 'Suspicious IP activity', severity: 'High', type: 'IP', date: '2026-02-20'},
      {id: 'T-1002', title: 'Malicious domain detected', severity: 'Medium', type: 'Domain', date: '2026-02-21'},
      {id: 'T-1003', title: 'Rare file hash seen', severity: 'Low', type: 'Hash', date: '2026-02-19'},
      {id: 'T-1004', title: 'Phishing URL reported', severity: 'High', type: 'URL', date: '2026-02-22'},
      {id: 'T-1005', title: 'C2 server beaconing', severity: 'Medium', type: 'IP', date: '2026-02-18'}
    ]
  };

  // populate cards
  document.getElementById('totalThreats').textContent = stats.total;
  document.getElementById('highSeverity').textContent = stats.high;
  document.getElementById('mediumSeverity').textContent = stats.medium;
  document.getElementById('lowSeverity').textContent = stats.low;

  // render trend chart
  const ctx = document.getElementById('threatChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: stats.trendLabels,
      datasets: [{
        label: 'Threats',
        data: stats.trends,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59,130,246,0.2)',
        tension: 0.3
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });

  // fill table
  const tbody = document.querySelector('#threatTable tbody');
  stats.threats.forEach(th => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${th.id}</td>
      <td>${th.title}</td>
      <td><span class="severity-badge severity-${th.severity.toLowerCase()}">${th.severity}</span></td>
      <td>${th.type}</td>
      <td>${th.date}</td>
    `;
    tbody.appendChild(tr);
  });
});
