async function runBuilder() {
  const output = document.getElementById("output");
  const runBtn = document.getElementById("runBtn");
  output.textContent = "Running workflow...";
  runBtn.disabled = true;

  const payload = {
    user_id: Number(document.getElementById("userId").value || 1),
    request_text: document.getElementById("requestText").value,
    input: {
      prompt: document.getElementById("prompt").value,
      style_hint: document.getElementById("styleHint").value,
      target_framework: document.getElementById("targetFramework").value,
      target_style_system: "tailwind",
      reference_urls: [],
      reference_images: [],
      figma_url: null,
    },
  };

  try {
    const res = await fetch("/api/v1/web-builder/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await res.json();
    output.textContent = JSON.stringify(json, null, 2);
  } catch (err) {
    output.textContent = `Failed: ${String(err)}`;
  } finally {
    runBtn.disabled = false;
  }
}
