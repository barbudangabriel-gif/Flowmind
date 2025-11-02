# Server Troubleshooting Session - November 1, 2025

**Server IP:** 91.107.206.64  
**Domain:** flowmindanalytics.ai  
**Status:** Site DOWN - Connection Refused

---

## Problem Summary

- Site https://flowmindanalytics.ai NOT responding
- Port 80 and 443: Connection refused
- Port 22 (SSH): Closed/blocked
- Currently in Hetzner Rescue Mode

---

## Screenshots & Debug Info

### 1. lsblk output (disk structure)

**Paste screenshot or output here:**

```
[Paste aici output-ul de la lsblk]
```

---

### 2. Next Steps

Once disk structure is identified, will:
1. Mount main disk partition
2. Check/fix firewall rules (UFW)
3. Check Docker containers status
4. Check Caddy configuration
5. Restart services

---

## Commands to Run

```bash
# 1. Check disk structure
lsblk

# 2. Mount main partition (will update based on lsblk output)
# mount /dev/XXX /mnt

# 3. Check what's on the disk
# ls -la /mnt/opt/flowmind
```

---

## Notes

- Server was working previously (deployment completed Nov 1)
- SSH key changed (server may have been reset/reinstalled)
- Need to verify if previous installation still exists
