# CSNETWK MP: LSNP
Repository for CSNETWK MP: Local Social Networking Protocol

## Setup
1. Clone the repository from main

```bash
git clone https://github.com/mbchavez27/csnetwk-mp-lsnp.git
cd csnetwk-mp-lsnp
```

2. Install dependencies
```bash
pip install zeroconf
```

## Testing in Multiple Terminals (Same Machine)
For easy testing, each peer simulates a separate terminal:
```bash
# Terminal 1 
python main.py --ip 127.0.0.1 --username Alice --verbose

# Terminal 2 
python main.py --ip 127.0.0.2 --username Bob --verbose

# Terminal 3
python main.py --ip 127.0.0.3 --username Carol

```
--verbose enables debug logging to view sent/received messages.

--status is optional. Default is "Exploring LSNP!"

## Available Commands
Change your username
```bash
/profile name="<new_name>"
```
Change your status
```bash
/status "<new_status>"
```
Enable verbose debug logging
```bash
/verbose on 
```
Disable verbose debug logging
```bash
/verbose off
```
Show your peer info, followed peers, and groups
```bash
/info
```
Follow a user to see their public posts
```bash
/follow "<user_id>"
```
Unfollow a user
```bash
/unfollow "<user_id>"
```
Broadcast a public POST to followers
```bash
/post "<message>"
```
Send a direct private message
```bash
/dm "<user_id>" "<message>"
```
Like a specific post / Remove your like from a post
```bash
/like "<user_id>" "<post_timestamp>"
```
Create a new group
```bash
/group_create "<group_name>" "<user_id>" "<user_id_>"...
```
Add or remove member from a group
```bash
/group_update "<group_name>" add/remove "<user_id>"
```
Send a message to all members of a group
```bash
/group_msg "<group_name>" "<message>"
```
Send a tictactoe game invite
```bash
/tictactoe @username
```
Make a move in the game
```bash
/move GAMEID POSITION
```
Show the list of available commands
```bash
/help
```
Exit the LSNP application
```bash
/exit
```
## Authors
Cayanan, Kristine Magdalene

Chavez, Max Benedict

Licup, Evan Gabriel

Rodriguez, Juan Titus

## AI Disclaimer
The LSNP protocol is primarily designed by the authors. AI tools, primarily ChatGPT, were used to assist in formulating message structures, suggesting improvements to the peer discovery process, including optional mDNS integration, UDP usage and refining formatting. All AI-assisted content was carefully reviewed, validated, and adapted to ensure alignment with the project’s functional and educational goals. All AI-generated content was thoroughly reviewed, validated, and adapted to meet the functional and educational goals of the project.