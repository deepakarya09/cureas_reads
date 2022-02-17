DB Auto Backup  

gunzip -c cr.sql.gz | psql test        restore command
# ./pg_backup.sh                       run script manually (command)

note 
  1) creat cron job
  2) update export variable 
			PGPASSWORD="password"
			export PGPASSWORD="password"
