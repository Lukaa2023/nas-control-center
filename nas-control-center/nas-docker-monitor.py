
#!/usr/bin/env python3

import json
import subprocess
import datetime
import os

OUTPUT = "/srv/nas/websites/vukyweb/nas/data/docker.json"

def collect():
    result = subprocess.run(
        ["/usr/bin/docker", "ps", "-a", "--format", "{{json .}}"],
        capture_output=True,
        text=True,
        check=True,
        timeout=15
    )

    containers = []

    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        item = json.loads(line)

        containers.append({
            "name": item["Names"],
            "image": item["Image"],
            "state": item["State"],
            "status": item["Status"],
            "ports": item["Ports"],
            "health": item["HealthStatus"],
            "id": item["ID"]
        })

    running = sum(
        1 for container in containers
        if container["state"] == "running"
    )

    return {
        "updated_at": datetime.datetime.now().astimezone().isoformat(),
        "total": len(containers),
        "running": running,
        "stopped": len(containers) - running,
        "containers": containers
    }

data = collect()
temporary = OUTPUT + ".tmp"

with open(temporary, "w") as f:
    json.dump(data, f, indent=2)

os.replace(temporary, OUTPUT)
os.chmod(OUTPUT, 0o644)
