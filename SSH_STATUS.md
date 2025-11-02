# SSH Setup pentru Hetzner - România

## Status: Server în boot

Server-ul a fost restartat cu Power Cycle. Ar trebui să se pornească în Rescue Mode în următoarele 60-90 de secunde.

## Next Steps:

### 1. Test SSH Connection (când server e gata)
```bash
ssh -i ~/.ssh/flowmind_ed25519 root@91.107.206.64 'echo SSH Merge!'
```

### 2. Dacă SSH Merge:
```bash
# Verific că Docker containers sunt running
ssh -i ~/.ssh/flowmind_ed25519 root@91.107.206.64 'docker ps'

# Verific logs din Caddy
ssh -i ~/.ssh/flowmind_ed25519 root@91.107.206.64 'systemctl status caddy'

# Verific backend container
ssh -i ~/.ssh/flowmind_ed25519 root@91.107.206.64 'docker logs flowmind-backend-1 | tail -20'
```

### 3. Dacă trebuie să reboot normal:
```bash
ssh -i ~/.ssh/flowmind_ed25519 root@91.107.206.64 'reboot'
```

## Rescue Mode vs Normal Mode

**Rescue Mode (ACUM):**
- Linux minimal system
- Ca să editez /etc/authorized_keys și să reboot

**Normal Mode (DUPĂ reboot):**
- Production container environment
- Docker, Caddy, Backend running
- Website pe https://flowmindanalytics.ai

## Urmărim Progress

După ce server se pornește, testez conexiunea și raportez status.

Aștept confirmarea că e ready...
