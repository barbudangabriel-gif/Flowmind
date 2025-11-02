# Hetzner Rescue Mode - SSH Key Setup

## Step-by-Step Instructions

### Step 1: Activate Rescue Mode
1. In Hetzner console → Select server "flowmindanalytics"
2. Go to **Rescue** tab
3. Click **"Activate Rescue Mode"** (or similar button)
4. Select architecture: **Linux x64** (default is fine)
5. Click **"Reset and boot into rescue mode"**
6. Server will reboot (takes ~1 minute)

### Step 2: Boot from Rescue
1. After reboot, you'll see a new IP or prompt
2. The rescue system boots with YOUR SSH keys automatically
3. Look for message like: "Rescue system ready at IP: xxx.xxx.xxx.xxx"
4. OR just try: `ssh root@91.107.206.64` (might work now!)

### Step 3: Mount Original Filesystem
Once in rescue mode, run:
```bash
# Mount the original disk
mount /dev/sda1 /mnt

# Verify it mounted (should show files)
ls /mnt/

# If you see 'root', 'boot', 'home' etc - good!
# If not, try /dev/sda2 or check with: lsblk
```

### Step 4: Add SSH Key to authorized_keys
```bash
# Create .ssh directory if needed
mkdir -p /mnt/root/.ssh

# Add Codespaces public key
cat >> /mnt/root/.ssh/authorized_keys << 'EOF'
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBdxa4oZZVu14Dou+RtEP7hM0bZ2m6OBxHEwoKzIR9AV codespace@codespaces-989c74
EOF

# Fix permissions
chmod 600 /mnt/root/.ssh/authorized_keys
chmod 700 /mnt/root/.ssh

# Verify it was added
cat /mnt/root/.ssh/authorized_keys
```

### Step 5: Exit Rescue and Reboot
```bash
# Unmount
umount /mnt

# Reboot to normal mode
reboot
```

### Step 6: Test SSH
Back in Codespaces:
```bash
ssh -i ~/.ssh/flowmind_ed25519 root@91.107.206.64 'echo SSH Works!'
```

## If Something Goes Wrong

**Can't mount filesystem?**
```bash
# List disks
lsblk

# Try different partition (usually sda1 or sda2)
mount /dev/sda2 /mnt
```

**SSH still doesn't work after reboot?**
- Go back to Rescue Mode
- Verify file was added: `cat /mnt/root/.ssh/authorized_keys`
- Check permissions: `ls -la /mnt/root/.ssh/`

**Need to go back to Rescue?**
- Just click "Activate Rescue Mode" again in Hetzner console

## Once SSH Works

From Codespaces:
```bash
ssh -i ~/.ssh/flowmind_ed25519 root@91.107.206.64 'docker ps'
```

Then we can:
- Check container status
- View logs
- Restart services
- Deploy updates
