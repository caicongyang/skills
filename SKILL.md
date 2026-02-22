---
name: ssh-remote-exec
description: Execute commands on remote Linux servers via SSH without login跳转. Use when user wants to run commands on remote servers and get results directly. Ideal for checking status, managing services, viewing logs, or performing admin tasks.
---

# SSH Remote Execution

Execute commands on remote Linux servers via SSH and get results directly.

## Usage

Use the `exec` tool to run SSH commands:

```bash
ssh user@host "your command"
```

### Examples

**Check server status:**
```bash
ssh root@192.168.1.100 "systemctl status nginx"
```

**View disk usage:**
```bash
ssh user@192.168.1.100 "df -h"
```

**Check memory:**
```bash
ssh user@192.168.1.100 "free -h"
```

**View logs:**
```bash
ssh user@192.168.1.100 "tail -f /var/log/syslog"
```

**Execute multiple commands:**
```bash
ssh user@192.168.1.100 "cd /data && ls -la && pwd"
```

**Check running processes:**
```bash
ssh user@192.168.1.100 "ps aux | grep python"
```

## SSH Connection Options

**Specify port (default 22):**
```bash
ssh -p 2222 user@host "command"
```

**Use identity file:**
```bash
ssh -i /path/to/private_key user@host "command"
```

## Prerequisites

**Configure SSH key authentication:**
```bash
# Generate SSH key (if not exists)
ssh-keygen -t ed25519 -C "your@email.com"

# Copy public key to server
ssh-copy-id user@remote_host

# Or manually add to ~/.ssh/authorized_keys
```

**Test connection first:**
```bash
ssh user@host "echo 'SSH connection successful'"
```

## Best Practices

1. **Use key-based auth** - More secure than passwords
2. **Specify full commands** - Avoid interactive prompts
3. **Quote commands properly** - Especially with special characters
4. **Use absolute paths** - For files in specific locations
5. **Check exit codes** - Some commands return non-zero on expected conditions

## Common Tasks

| Task | Command |
|------|---------|
| Check OS version | `ssh host "cat /etc/os-release"` |
| Check uptime | `ssh host "uptime"` |
| Check CPU load | `ssh host "top -bn1 | head -5"` |
| List installed packages | `ssh host "dpkg -l | head -20"` |
| Check network connections | `ssh host "ss -tunap"` |
| View last 20 system logs | `ssh host "journalctl -n 20"` |
| Restart service | `ssh host "sudo systemctl restart nginx"` |
| Check firewall status | `ssh host "ufw status"` |

## Docker Management

### Container Operations

**List containers:**
```bash
# All containers (running + stopped)
ssh host "docker ps -a"

# Running containers only
ssh host "docker ps"

# Format output
ssh host "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
```

**Container status:**
```bash
# Inspect container
ssh host "docker inspect container_name"

# View container logs
ssh host "docker logs container_name"
ssh host "docker logs -f container_name"  # Follow logs
ssh host "docker logs --tail 100 container_name"  # Last 100 lines

# Container resource usage
ssh host "docker stats --no-stream"
ssh host "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'"
```

**Start/Stop/Restart containers:**
```bash
# Start container
ssh host "docker start container_name"

# Stop container
ssh host "docker stop container_name"

# Restart container
ssh host "docker restart container_name"

# Kill container
ssh host "docker kill container_name"

# Remove container
ssh host "docker rm container_name"
ssh host "docker rm -f container_name"  # Force remove

# Restart all stopped containers
ssh host "docker start $(docker ps -aq)"
```

**Execute command in container:**
```bash
# Execute single command
ssh host "docker exec container_name ls -la /app"

# Interactive shell
ssh host "docker exec -it container_name /bin/bash"
```

### Image Operations

**List images:**
```bash
ssh host "docker images"
ssh host "docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}'"
```

**Pull/Push images:**
```bash
ssh host "docker pull image_name:tag"
ssh host "docker push image_name:tag"
```

**Remove images:**
```bash
ssh host "docker rmi image_name:tag"
ssh host "docker rmi $(docker images -q)"  # Remove unused images
ssh host "docker image prune -a"  # Remove all unused images
```

### Docker Compose Operations

**Compose status:**
```bash
# List containers managed by compose
ssh host "docker compose ps"

# Status in project directory
ssh host "cd /path/to/project && docker compose ps"

# Detailed status
ssh host "docker compose ps --services --status"
```

**Start/Stop/Restart compose:**
```bash
# Start services
ssh host "cd /path/to/project && docker compose up -d"

# Stop services
ssh host "cd /path/to/project && docker compose down"

# Restart services
ssh host "cd /path/to/project && docker compose restart"
ssh host "cd /path/to/project && docker compose restart service_name"

# Pull latest images and restart
ssh host "cd /path/to/project && docker compose pull && docker compose up -d"
```

**View logs:**
```bash
# All services logs
ssh host "cd /path/to/project && docker compose logs"

# Follow logs
ssh host "cd /path/to/project && docker compose logs -f"

# Last N lines
ssh host "cd /path/to/project && docker compose logs --tail 50"

# Specific service logs
ssh host "cd /path/to/project && docker compose logs -f service_name"
```

**Service operations:**
```bash
# Scale services
ssh host "cd /path/to/project && docker compose up -d --scale service_name=3"

# Rebuild and restart
ssh host "cd /path/to/project && docker compose up -d --build"

# Check config (dry-run)
ssh host "cd /path/to/project && docker compose config"
```

### Docker System Management

**System-wide commands:**
```bash
# Disk usage by Docker
ssh host "docker system df"
ssh host "docker system df -v"  # Detailed

# Remove unused data
ssh host "docker system prune"  # All unused containers, networks, images
ssh host "docker system prune -a"  # Including all unused images

# Remove specific items
ssh host "docker container prune"  # Stopped containers
ssh host "docker network prune"  # Unused networks
ssh host "docker image prune"  # Dangling images

# Docker events (real-time)
ssh host "docker events --filter 'container=container_name'"
```

## Shell Script Execution

### Execute Remote Scripts

**Run existing script:**
```bash
# Execute script (must have execute permission)
ssh host "/path/to/script.sh"

# Run with arguments
ssh host "/path/to/script.sh arg1 arg2"

# Run as specific user
ssh host "sudo -u username /path/to/script.sh"
```

**Download and execute script:**
```bash
# Download via curl and execute
ssh host "curl -sL https://example.com/script.sh | bash"

# Download via wget and execute
ssh host "wget -qO- https://example.com/script.sh | bash"
```

**Execute from remote URL:**
```bash
ssh host "bash -c '\$(curl -sL https://example.com/install.sh)'"
```

### Script Management

**Check script content first:**
```bash
# View script without executing
ssh host "cat /path/to/script.sh"

# Check permissions
ssh host "ls -la /path/to/script.sh"

# Make executable
ssh host "chmod +x /path/to/script.sh"

# Create script on remote server
ssh host "cat > /path/to/script.sh << 'EOF'
#!/bin/bash
echo 'Hello World'
# Your commands here
EOF
chmod +x /path/to/script.sh"
```

### Common Script Examples

**Deployment script:**
```bash
ssh host "/opt/scripts/deploy.sh"
```

**Backup script:**
```bash
ssh host "/opt/scripts/backup.sh"
```

**Update script:**
```bash
ssh host "/opt/scripts/update.sh"
```

## Git Operations

### Repository Operations

**Clone repository:**
```bash
ssh host "git clone https://github.com/user/repo.git"
ssh host "git clone https://github.com/user/repo.git /path/to/destination"
```

**Clone private repo:**
```bash
# With personal access token
ssh host "git clone https://username:token@github.com/user/repo.git"
```

### Status & Information

**Check repository status:**
```bash
# Working tree status
ssh host "cd /path/to/repo && git status"

# Check current branch
ssh host "cd /path/to/repo && git branch"

# View recent commits
ssh host "cd /path/to/repo && git log --oneline -10"

# Check remote branches
ssh host "cd /path/to/repo && git branch -r"

# View remote URLs
ssh host "cd /path/to/repo && git remote -v"

# Check differences
ssh host "cd /path/to/repo && git diff"
ssh host "cd /path/to/repo && git diff --stat"
```

**Check for updates:**
```bash
# Fetch remote changes
ssh host "cd /path/to/repo && git fetch"

# Check current branch status vs remote
ssh host "cd /path/to/repo && git status"

# View unpulled commits
ssh host "cd /path/to/repo && git log HEAD..origin/branch --oneline"
```

### Branch Operations

**Switch branch:**
```bash
ssh host "cd /path/to/repo && git checkout branch_name"
ssh host "cd /path/to/repo && git checkout -b new_branch"  # Create and switch
```

**Create and push branch:**
```bash
ssh host "cd /path/to/repo && git checkout -b feature/new-feature"
ssh host "cd /path/to/repo && git push -u origin feature/new-feature"
```

**Delete branch:**
```bash
# Delete local branch
ssh host "cd /path/to/repo && git branch -d branch_name"

# Delete remote branch
ssh host "cd /path/to/repo && git push origin --delete branch_name"
```

### Pull & Push

**Pull updates:**
```bash
# Pull current branch
ssh host "cd /path/to/repo && git pull"

# Pull specific branch
ssh host "cd /path/to/repo && git pull origin branch_name"

# Pull with rebase
ssh host "cd /path/to/repo && git pull --rebase"
```

**Push changes:**
```bash
# Push current branch
ssh host "cd /path/to/repo && git push"

# Push to specific branch
ssh host "cd /path/to/repo && git push origin branch_name"

# Force push (use with caution!)
ssh host "cd /path/to/repo && git push --force"
```

### Commit Operations

**Stage and commit:**
```bash
# Add all changes
ssh host "cd /path/to/repo && git add ."

# Add specific file
ssh host "cd /path/to/repo && git add filename"

# Commit with message
ssh host "cd /path/to/repo && git commit -m 'Your commit message'"

# Amend last commit
ssh host "cd /path/to/repo && git commit --amend -m 'New message'"
ssh host "cd /path/to/repo && git commit --amend --no-edit"  # Keep same message
```

**Undo operations:**
```bash
# Unstage files
ssh host "cd /path/to/repo && git reset HEAD filename"
ssh host "cd /path/to/repo && git reset HEAD ."  # Unstage all

# Discard local changes (WARNING: irreversible)
ssh host "cd /path/to/repo && git checkout -- filename"
ssh host "cd /path/to/repo && git checkout -- ."  # Discard all

# Reset to previous commit (WARNING: removes changes)
ssh host "cd /path/to/repo && git reset --hard commit_hash"
ssh host "cd /path/to/repo && git reset --hard origin/branch_name"
```

### Tag Operations

**List tags:**
```bash
ssh host "cd /path/to/repo && git tag"
```

**Create tag:**
```bash
# Lightweight tag
ssh host "cd /path/to/repo && git tag v1.0.0"

# Annotated tag
ssh host "cd /path/to/repo && git tag -a v1.0.0 -m 'Version 1.0.0'"
```

**Push tags:**
```bash
ssh host "cd /path/to/repo && git push origin v1.0.0"
ssh host "cd /path/to/repo && git push origin --tags"  # Push all tags
```

### Stash Operations

**Save changes:**
```bash
ssh host "cd /path/to/repo && git stash"
ssh host "cd /path/to/repo && git stash save 'message'"
```

**Apply stashed changes:**
```bash
ssh host "cd /path/to/repo && git stash pop"  # Apply and remove
ssh host "cd /path/to/repo && git stash apply"  # Apply but keep stash
```

**Manage stash:**
```bash
ssh host "cd /path/to/repo && git stash list"
ssh host "cd /path/to/repo && git stash drop"  # Remove most recent stash
ssh host "cd /path/to/repo && git stash clear"  # Remove all stashes
```

### Submodule Operations

**Update submodules:**
```bash
ssh host "cd /path/to/repo && git submodule update --init --recursive"
ssh host "cd /path/to/repo && git submodule update --remote"
```

### CI/CD Scripts

**Automated deployment:**
```bash
ssh host "cd /path/to/repo && git pull && npm install && npm run build"
```

**Pull and restart:**
```bash
ssh host "cd /path/to/repo && git pull && docker compose up -d --build"
```

### Useful Git One-Liners

```bash
# Quick status
ssh host "cd /path/to/repo && git status --short"

# Check remote vs local
ssh host "cd /path/to/repo && git rev-parse --abbrev-ref HEAD && git rev-parse @{u}"

# Count commits
ssh host "cd /path/to/repo && git rev-list --count HEAD"
ssh host "cd /path/to/repo && git rev-list --count --all"

# Find large files in history
ssh host "cd /path/to/repo && git verify-pack -v .git/objects/pack/*.idx | sort -k 3 -n | tail -10"

# Clean untracked files
ssh host "cd /path/to/repo && git clean -fd"  # Dry run: git clean -n
ssh host "cd /path/to/repo && git clean -fd -x"  # Including ignored files
```

## Notes

- All output is returned directly to the chat
- Interactive commands (like `vim`, `top`) won't work well
- Long-running commands will block until completion
- Use `&` for background execution if needed
