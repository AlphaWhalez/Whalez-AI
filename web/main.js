async function fetchHealth() {
  const output = document.getElementById('health-output');
  output.textContent = 'Fetching...';
  try {
    const response = await fetch('/health');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    output.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    output.textContent = `Failed to load health: ${error}`;
  }
}

document.getElementById('refresh').addEventListener('click', fetchHealth);
fetchHealth();

async function submitAffirmation() {
  const message = document.getElementById('affirm-message').value.trim();
  const output = document.getElementById('affirm-output');
  if (!message) {
    output.textContent = 'Please enter a message';
    return;
  }
  try {
    const response = await fetch('/api/affirm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Unknown error');
    }
    const data = await response.json();
    output.textContent = JSON.stringify(data, null, 2);
    document.getElementById('affirm-message').value = '';
  } catch (error) {
    output.textContent = `Failed to submit: ${error}`;
  }
}

document.getElementById('affirm-submit').addEventListener('click', submitAffirmation);
