document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-copy]");
  if (!button) return;
  const value = button.getAttribute("data-copy");
  const original = button.textContent;
  try {
    await navigator.clipboard.writeText(value);
    button.textContent = "Copied!";
  } catch {
    const area = document.createElement("textarea");
    area.value = value;
    document.body.appendChild(area);
    area.select();
    try { document.execCommand("copy"); button.textContent = "Copied!"; }
    catch { button.textContent = "Select manually"; }
    area.remove();
  }
  setTimeout(() => { button.textContent = original; }, 1500);
});

// Live NAS monitoring
async function updateNASStats() {
  const updated = document.getElementById("last-updated");

  try {
    const response = await fetch("data/stats.json?t=" + Date.now(), {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error("HTTP " + response.status);
    }

    const data = await response.json();

    function setText(id, value) {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    }

    function setBar(id, percentage) {
      const element = document.getElementById(id);
      if (element) {
        const value = Math.max(0, Math.min(100, Number(percentage) || 0));
        element.style.width = value + "%";
      }
    }

    function formatBytes(bytes) {
      const gb = bytes / (1024 ** 3);
      return gb.toFixed(1) + " GB";
    }

    setText("cpu-value", data.cpu.usage_percent + "%");
    setBar("cpu-bar", data.cpu.usage_percent);

    setText(
      "cpu-load",
      "Load average: " +
      data.cpu.load_1m + " / " +
      data.cpu.load_5m + " / " +
      data.cpu.load_15m
    );

    setText("memory-value", data.memory.usage_percent + "%");
    setBar("memory-bar", data.memory.usage_percent);

    setText(
      "memory-detail",
      formatBytes(data.memory.used) + " / " +
      formatBytes(data.memory.total)
    );

    setText("disk-value", data.disk.usage_percent + "%");
    setBar("disk-bar", data.disk.usage_percent);

    setText(
      "disk-detail",
      formatBytes(data.disk.used) + " / " +
      formatBytes(data.disk.total)
    );

    setText("uptime-value", data.uptime_human);
    setText("hostname-value", "Host: " + data.hostname);

    if (updated) {
      const time = new Date(data.updated_at);
      setText("last-updated", "Updated " + time.toLocaleTimeString());
    }

  } catch (error) {
    console.error("NAS monitoring error:", error);
    setText("last-updated", "Unable to load statistics");
  }
}

updateNASStats();
setInterval(updateNASStats, 10000);


// Docker container monitoring

async function updateDockerStats() {
  const list = document.getElementById("docker-container-list");
  if (!list) return;

  try {
    const response = await fetch("data/docker.json?t=" + Date.now(), {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error("HTTP " + response.status);
    }

    const data = await response.json();

    document.getElementById("docker-summary").textContent =
      `${data.running} running / ${data.stopped} stopped / ${data.total} total`;

    document.getElementById("docker-updated").textContent =
      "Updated " + new Date(data.updated_at).toLocaleTimeString();

    list.replaceChildren();

    data.containers.forEach(container => {
      const card = document.createElement("article");
      card.className = "docker-container";

      const header = document.createElement("div");
      header.className = "docker-container-header";

      const name = document.createElement("h4");
      name.textContent = container.name;

      const state = document.createElement("span");
      state.className = "docker-state " +
        (container.state === "running" ? "running" : "stopped");
      state.textContent = container.state.toUpperCase();

      const image = document.createElement("p");
      image.textContent = "Image: " + container.image;

      const status = document.createElement("p");
      status.textContent = container.status;

      const ports = document.createElement("p");
      ports.textContent = "Ports: " + (container.ports || "None");

      const health = document.createElement("p");
      health.textContent = "Health check: " +
        (container.health === "none" ? "Not configured" : container.health);

      header.append(name, state);
      card.append(header, image, status, ports, health);
      list.appendChild(card);
    });

  } catch (error) {
    console.error("Docker monitoring error:", error);
    document.getElementById("docker-updated").textContent =
      "Unable to load Docker data";
  }
}

updateDockerStats();
setInterval(updateDockerStats, 15000);
