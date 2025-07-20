# csnetwk-mp-lsnp
Repository for CSNETWK MP: Local Social Networking Protocol

# CSNETWK MP: LSNP - Lightweight Social Networking Protocol

## Setup
1. Clone the repository from main

```bash
git clone https://github.com/mbchavez27/csnetwk-mp-lsnp.git
cd csnetwk-mp-lsnp
```

2. Create and switch to your feature branch

```bash
git branch feature_name
git checkout branch_name
```

## Testing
Each peer simulates a separate terminal using a unique loopback IP:
```bash
# Terminal 1 in verbose mode
python main.py --ip 127.0.0.2 --username Bella --status Hello --verbose

# Terminal 2 
python main.py --ip 127.0.0.3 --username Edward --verbose

# Terminal 3 in non verbose mode
python main.py --ip 127.0.0.4 --username Jacob

```
--verbose enables debug logging to view sent/received messages.
--status is optional. Default is "Exploring LSNP!"

## Available Commands
Update your display name and status
```bash
/profile name="New Name" status="New Status"
```
Quickly update just your status
```bash
/status Exploring LSNP!
```
Enable verbose debug logging
```bash
/verbose on 
```
Disable verbose debug logging
```bash
/verbose off
```
Show the list of available commands
```bash
/help
```

## Checklist