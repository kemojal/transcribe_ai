#!/bin/bash

# Set environment variables
PGHOST=db
PGPORT=5432
PGUSER=postgres
PGPASSWORD=12345
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Perform backup
echo "Starting backup at $(date)" >> /var/log/backup.log
pg_dump -h $PGHOST -p $PGPORT -U $PGUSER -F c -b -v -f $BACKUP_DIR/backup_$DATE.dump postgres

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully at $(date)" >> /var/log/backup.log
else
    echo "Backup failed at $(date)" >> /var/log/backup.log
    exit 1
fi

# Remove backups older than 7 days
find $BACKUP_DIR -type f -name "backup_*.dump" -mtime +7 -delete 