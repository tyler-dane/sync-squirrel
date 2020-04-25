# sync-squirrel
Syncs contacts between Less-Annoying CRM, ConvertKit, Acuity

## Build Notes
`./build.sh` # <-- make sure `virtualenv` active

## Install Notes
Copy binary and config in `dist/` to desired directory
Copy `run.sh` to desired directory and update with desired bath
Copy `config.dev.yaml` to desired dir

#### Install chromedriver:
- Works in Chrome and Chromium
- TBD

#### Cronjob:
`crontab -e`:

Runs every 10 minutes
```bash
*/10 * * * * /Users/ty/test/sync_1.0.0/run.sh
```

## Other notes
Install Chromedriver on Linux:
```bash
sudo apt-get install chromium-chromedriver
```

See where binary installed
```bash
dpkg -L chromium-chromedriver
```

