"""
Ntfy monitoring script generator for Docker stack monitoring
"""


def generate_ntfy_monitor_script(
    ntfy_server: str, ntfy_topic: str, stack_name: str = "iiot-stack"
) -> str:
    """
    Generate a bash script that monitors Docker stack and sends updates via ntfy

    Features:
    - Sends status updates every 10-15 seconds
    - Listens for commands: Stop, Status, Log
    - Provides container health status
    """

    script = f"""#!/bin/bash
# Ntfy Stack Monitoring Script
# Monitors Docker Compose stack and sends notifications via ntfy

NTFY_SERVER="{ntfy_server}"
NTFY_TOPIC="{ntfy_topic}"
STACK_NAME="{stack_name}"
UPDATE_INTERVAL=12  # seconds between updates
MONITORING_ACTIVE=true

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo "🔔 Starting Ntfy Stack Monitor"
echo "Server: $NTFY_SERVER"
echo "Topic: $NTFY_TOPIC"
echo "================================"

# Function to send ntfy notification
send_notification() {{
    local title="$1"
    local message="$2"
    local priority="${{3:-default}}"
    local tags="${{4:-}}"

    curl -s -X POST "$NTFY_SERVER/$NTFY_TOPIC" \\
        -H "Title: $title" \\
        -H "Priority: $priority" \\
        -H "Tags: $tags" \\
        -d "$message" > /dev/null
}}

# Function to get stack status
get_stack_status() {{
    local status_msg=""
    local container_count=$(docker compose ps -q 2>/dev/null | wc -l)
    local running_count=$(docker compose ps -q 2>/dev/null | xargs docker inspect -f '{{{{.State.Running}}}}' 2>/dev/null | grep -c true || echo 0)
    local healthy_count=$(docker compose ps -q 2>/dev/null | xargs docker inspect -f '{{{{.State.Health.Status}}}}' 2>/dev/null | grep -c healthy || echo 0)

    # Get container details
    local container_details=""
    while IFS= read -r container; do
        if [ -n "$container" ]; then
            local name=$(docker inspect -f '{{{{.Name}}}}' "$container" 2>/dev/null | sed 's/^\\///')
            local state=$(docker inspect -f '{{{{.State.Status}}}}' "$container" 2>/dev/null)
            local health=$(docker inspect -f '{{{{.State.Health.Status}}}}' "$container" 2>/dev/null || echo "N/A")

            if [ "$state" = "running" ]; then
                if [ "$health" = "healthy" ] || [ "$health" = "N/A" ]; then
                    container_details+="✅ $name: $state\\n"
                else
                    container_details+="⚠️  $name: $state ($health)\\n"
                fi
            else
                container_details+="❌ $name: $state\\n"
            fi
        fi
    done < <(docker compose ps -q 2>/dev/null)

    # Build status message
    status_msg="Stack: $STACK_NAME\\n"
    status_msg+="Total: $container_count | Running: $running_count"
    if [ $healthy_count -gt 0 ]; then
        status_msg+=" | Healthy: $healthy_count"
    fi
    status_msg+="\\n\\n$container_details"

    echo -e "$status_msg"
}}

# Function to get detailed status
get_detailed_status() {{
    local details=""
    details+="📊 Stack: $STACK_NAME\\n"
    details+="Time: $(date '+%Y-%m-%d %H:%M:%S')\\n\\n"

    # Container status
    details+="CONTAINERS:\\n"
    while IFS= read -r container; do
        if [ -n "$container" ]; then
            local name=$(docker inspect -f '{{{{.Name}}}}' "$container" 2>/dev/null | sed 's/^\\///')
            local state=$(docker inspect -f '{{{{.State.Status}}}}' "$container" 2>/dev/null)
            local uptime=$(docker inspect -f '{{{{.State.StartedAt}}}}' "$container" 2>/dev/null)
            local cpu=$(docker stats --no-stream --format "{{{{.CPUPerc}}}}" "$container" 2>/dev/null)
            local mem=$(docker stats --no-stream --format "{{{{.MemUsage}}}}" "$container" 2>/dev/null)

            details+="  $name\\n"
            details+="    Status: $state\\n"
            details+="    CPU: $cpu | Mem: $mem\\n"
        fi
    done < <(docker compose ps -q 2>/dev/null)

    echo -e "$details"
}}

# Function to check for commands
check_commands() {{
    # Listen for the last message on the topic
    local last_msg=$(curl -s "$NTFY_SERVER/$NTFY_TOPIC/json?poll=1" | tail -1 | jq -r '.message' 2>/dev/null)

    if [ -n "$last_msg" ]; then
        case "$last_msg" in
            "Stop"|"stop"|"STOP")
                echo "${{YELLOW}}📡 Received Stop command${{NC}}"
                MONITORING_ACTIVE=false
                send_notification "Monitor Stopped" "Stack monitoring paused. Send 'Log' to resume." "default" "pause"
                ;;
            "Status"|"status"|"STATUS")
                echo "${{GREEN}}📡 Received Status command${{NC}}"
                local status=$(get_detailed_status)
                send_notification "Stack Status" "$status" "high" "bar_chart"
                ;;
            "Log"|"log"|"LOG")
                echo "${{GREEN}}📡 Received Log command${{NC}}"
                MONITORING_ACTIVE=true
                send_notification "Monitor Resumed" "Stack monitoring resumed" "default" "play"
                ;;
        esac
    fi
}}

# Send initial notification
send_notification "Monitor Started" "Stack monitoring is now active\\nSend 'Stop', 'Status', or 'Log' commands" "default" "rocket"

# Main monitoring loop
while true; do
    # Check for commands
    check_commands

    # Send periodic updates if monitoring is active
    if [ "$MONITORING_ACTIVE" = true ]; then
        status=$(get_stack_status)

        # Check if all containers are running
        container_count=$(docker compose ps -q 2>/dev/null | wc -l)
        running_count=$(docker compose ps -q 2>/dev/null | xargs docker inspect -f '{{{{.State.Running}}}}' 2>/dev/null | grep -c true || echo 0)

        if [ $container_count -eq $running_count ] && [ $container_count -gt 0 ]; then
            # All running - send normal update
            send_notification "Stack OK" "$status" "low" "white_check_mark"
        elif [ $running_count -eq 0 ]; then
            # All stopped - send warning
            send_notification "Stack Down" "$status" "urgent" "warning"
        else
            # Some issues - send medium priority
            send_notification "Stack Issues" "$status" "high" "warning"
        fi

        echo "${{GREEN}}[$(date '+%H:%M:%S')] Sent update to ntfy${{NC}}"
    fi

    sleep $UPDATE_INTERVAL
done
"""

    return script


def generate_ntfy_readme_section(ntfy_server: str, ntfy_topic: str) -> str:
    """Generate README section for ntfy monitoring"""

    return f"""
## 🔔 Ntfy Stack Monitoring

Your stack includes automatic monitoring via [ntfy]({ntfy_server}).

### Starting the Monitor

**Linux/Mac:**
```bash
chmod +x monitor.sh
./monitor.sh &
```

**Windows:**
Run in a separate terminal:
```cmd
bash monitor.sh
```

### Features

- **Automatic Updates**: Receive stack status every 10-15 seconds
- **Remote Commands**: Control monitoring from anywhere
- **Health Checks**: Monitor container health and resource usage

### Commands

Subscribe to your topic: **{ntfy_topic}**

Send commands by publishing messages to the same topic:

- **Stop** - Pause monitoring updates
- **Status** - Get detailed stack status immediately
- **Log** - Resume monitoring updates

### Subscribe to Notifications

**Web Browser:**
```
{ntfy_server}/{ntfy_topic}
```

**Mobile App:**
Download ntfy from App Store/Play Store and subscribe to: `{ntfy_topic}`

**Command Line:**
```bash
curl -s {ntfy_server}/{ntfy_topic}/json
```

### Example: Send a Command

```bash
curl -X POST {ntfy_server}/{ntfy_topic} -d "Status"
```
"""
