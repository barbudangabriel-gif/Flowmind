#!/bin/bash

# Automated backup script for FlowMind production
# Add to crontab: 0 2 * * * /opt/flowmind/deploy/backup.sh

set -e

BACKUP_DIR="/opt/flowmind/backups"
DATE=$(date +%Y%m%d-%H%M%S)
RETENTION_DAYS=7

echo "🗄️  FlowMind Backup - $DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup Redis data
echo "📦 Backing up Redis..."
docker exec flowmind-redis redis-cli SAVE
docker cp flowmind-redis:/data/dump.rdb $BACKUP_DIR/redis-$DATE.rdb

# Backup Mindfolios JSON files
echo "📦 Backing up Mindfolios..."
tar -czf $BACKUP_DIR/mindfolios-$DATE.tar.gz /opt/flowmind/data/mindfolios

# Backup environment config (without secrets)
echo "📦 Backing up config..."
cp /opt/flowmind/deploy/.env.production $BACKUP_DIR/env-$DATE.backup

# Remove old backups (older than RETENTION_DAYS)
echo "🧹 Cleaning old backups (older than $RETENTION_DAYS days)..."
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

# Calculate backup sizes
TOTAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)

echo "✅ Backup complete"
echo "📊 Total backup size: $TOTAL_SIZE"
echo "📁 Location: $BACKUP_DIR"

# List current backups
echo ""
echo "Current backups:"
ls -lh $BACKUP_DIR | tail -n +2
