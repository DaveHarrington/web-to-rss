# Scraper
sudo -u www-data crontab -e

```
*/5 * * * * /home/dave/web-to-rss/run.sh 2>&1 | logger -t www-to-rss
```

# App
sudo -u www-data make
