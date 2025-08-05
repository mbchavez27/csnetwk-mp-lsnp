import random
import time
from network.sender import unicast_message
from tokens.generator import generate_token
import uuid
active_games = {}
WIN_LINES = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]
    ]

def handleInvite(msg, sender_ip, peer_table, logger):  
    game_id = msg.get("GAMEID")
    symbol = msg.get("SYMBOL")
    sender = msg.get("FROM")
    inviter_name = peer_table.get_name(sender)
    display_name = inviter_name.split("@")[0]
    invitee_symbol = "O" if symbol == "X" else "X"

    invitee_user_id = None
    for uid, data in peer_table.peers.items():
        if data["ip"] == sender_ip:
            continue
        invitee_user_id = uid
        break
    if not invitee_user_id:
        to_field = msg.get("TO", "unknown@127.0.0.1")
        invitee_user_id = to_field

    active_games[game_id] ={
        "board": [" "] * 9,
        "players": {symbol: sender, invitee_symbol: invitee_user_id},
        "turn": symbol
    }
    
    if logger and logger.verbose:
        print(f"[GAME] {inviter_name} invited you to play Tic-Tac-Toe (game {game_id}) as {invitee_symbol}.")
    
    
    print(f"{display_name} is inviting you to play Tic-Tac-Toe.")

def formatMessage(msg: dict) -> str:
    return "\n".join(f"{key}: {value}" for key, value in msg.items())

def printBoard(board):
    for i in range(0, 9, 3):
        print(f"{board[i]} | {board[i+1]} | {board[i+2]} ")
        if i < 6:
            print("-----------")

def checkWinner(board):
   
    for line in WIN_LINES:
        a, b, c = line
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a], line
    
    if " " not in board:
        return "DRAW", None
    return None, None

def findIP(game, sender):
    if "@" in sender:
        sender_ip = sender.split("@")[1]
    else:
        sender_ip = sender
    for symbol, user_id in game["players"].items():
        user_ip = user_id.split("@")[1]
        if user_ip != sender_ip:
            return user_ip
    return None

def handleMove(msg, sender, user_profile, peer_table, logger):
    game_id = msg.get("GAMEID")
    position = int(msg.get("POSITION", -1))
    symbol = msg.get("SYMBOL")

    game = active_games.get(game_id)
    if not game:
        if logger and logger.verbose:
            print(f"[GAME] Received a move for an unknown game {game_id}")
        return
    
    if position < 0 or position > 8 or game["board"][position] != " ":
        if logger and logger.verbose:
            print(f"[GAME] Invalid move received for game {game_id}")
        return
    
    game["board"][position] = symbol
    printBoard(game["board"])
    winner, winning_line = checkWinner(game["board"])
    
    if winner:
        opponent_ip = findIP(game, sender)
        sendResults(game_id, winner, winning_line, user_profile, peer_table)

        active_games.pop(game_id, None)
    else:
        game["turn"] = "O" if symbol == "X" else "X"

    
    

def handleResult(msg, sender, peer_table, logger):
    game_id = msg.get("GAMEID")
    result = msg.get("RESULT")
    symbol = msg.get("SYMBOL")
    winning_line = msg.get("WINNING_LINE")

    if logger:
        print(f"[GAME] Game {game_id} ended: {symbol} {result} (winning line: {winning_line})")
    
    if game_id in active_games:
        active_games.pop(game_id, None)

def sendInvite(game_id, symbol_choice, opponent_ip, user_profile, peer_table):
    opponent_user_id = next(
        (uid for uid, data in peer_table.peers.items() if data["ip"] == opponent_ip),
        None
    )
    
    msg = {
        "TYPE": "TICTACTOE_INVITE",
        "FROM": user_profile["user_id"],
        "TO": opponent_user_id,
        "GAMEID": game_id,
        "MESSAGE_ID": uuid.uuid4().hex[:8],
        "SYMBOL": symbol_choice,
        "TIMESTAMP": int(time.time()),
        "TOKEN": generate_token(user_profile["user_id"], 3600, "game")
    }
    active_games[game_id] = {
            "board": [" "] * 9,
            "players": {symbol_choice: user_profile["user_id"], "O" if symbol_choice == "X" else "X": opponent_user_id},
            "turn": symbol_choice
        }
    unicast_message(formatMessage(msg), opponent_ip)

def sendMove(game_id, position, symbol, opponent_ip, user_profile, peer_table):
    opponent_user_id = next(
        (uid for uid, data in peer_table.peers.items() if data["ip"] == opponent_ip),
        f"unknown@{opponent_ip}"
    )
    msg = {
        "TYPE": "TICTACTOE_MOVE",
        "FROM": user_profile["user_id"],
        "TO": opponent_user_id,
        "GAMEID": game_id,
        "POSITION": str(position),
        "MESSAGE_ID": uuid.uuid4().hex[:8],
        "SYMBOL": symbol,
        "TIMESTAMP": int(time.time()),
        "TOKEN": generate_token(user_profile["user_id"], 3600, "game")
    }
    unicast_message(formatMessage(msg), opponent_ip)

def sendResults(game_id, winner, winning_line, user_profile, peer_table):
    game = active_games.get(game_id)
    
    sender_id = user_profile["user_id"]
    opponent_ip = None
    opponent_user_id = None
    for symbol, uid in game["players"].items():
        if uid != sender_id:
            opponent_user_id = uid
            opponent_ip = uid.split("@")[1]
            break

    msg = {
        "TYPE": "TICTACTOE_RESULT",
        "FROM": user_profile["user_id"],
        "TO": opponent_user_id,
        "GAMEID": game_id,
        "MESSAGE_ID": uuid.uuid4().hex[:8],
        "RESULT": "WIN" if winner in ["X", "O"] else "",
        "SYMBOL": winner if winner in ["X", "O"] else "DRAW",
        "WINNING_LINE": ",".join(str(x) for x in winning_line) if winning_line else "",
        "TIMESTAMP": int(time.time())
    }
    unicast_message(formatMessage(msg), opponent_ip)
    unicast_message(formatMessage(msg), user_profile["ip"])