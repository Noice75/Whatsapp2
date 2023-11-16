# import chess
# import threading
# import time
# import whatsapp
# from whatsapp import commands

# # Define custom symbols
# custom_symbols = {
#     chess.Piece(chess.PAWN, chess.WHITE): '♙',
#     chess.Piece(chess.KNIGHT, chess.WHITE): '♘',
#     chess.Piece(chess.BISHOP, chess.WHITE): '♗',
#     chess.Piece(chess.ROOK, chess.WHITE): '♖',
#     chess.Piece(chess.QUEEN, chess.WHITE): '♕',
#     chess.Piece(chess.KING, chess.WHITE): '♔',
#     chess.Piece(chess.PAWN, chess.BLACK): '♟',
#     chess.Piece(chess.KNIGHT, chess.BLACK): '♞',
#     chess.Piece(chess.BISHOP, chess.BLACK): '♝',
#     chess.Piece(chess.ROOK, chess.BLACK): '♜',
#     chess.Piece(chess.QUEEN, chess.BLACK): '♛',
#     chess.Piece(chess.KING, chess.BLACK): '♚',
# }

# whiteTime = 0
# blackTime = 0
# whiteID = None
# blackID = None
# no_limit = True
# resign = False
# def countdown(board):
#     global whiteTime
#     global blackTime
#     while whiteTime > 0 and blackTime > 0:
#         if(resign):
#             break
#         if(board.turn):
#             time.sleep(1)
#             whiteTime -= 1
#         elif(board.turn == False):
#             time.sleep(1)
#             blackTime -= 1
#     if(whiteTime <= 0):
#         whatsapp.send("Black Wins By Timeout!")
#     elif(blackTime <= 0):
#         whatsapp.send("White Wins By Timeout!")


# def display_board(board):
#     custom_board = board.__str__()
#     for piece, symbol in custom_symbols.items():
#         custom_board = custom_board.replace(piece.symbol(), symbol).replace('.'," * ")

#     turn_indicator = "White's turn" if board.turn else "Black's turn"
#     if(not board.turn):
#         rows = custom_board.split('\n')
#         reversed_board = '\n'.join(reversed(rows))
#         reversed_board += f"\n{turn_indicator}"
#         whatsapp.send(reversed_board)
#     else:
#         custom_board += f"\n{turn_indicator}"
#         whatsapp.send(custom_board)

# def get_move(board):
#     while True:
#         try:
#             if(board):
#                 move = whatsapp.wait_for_id(whiteID).body
#             else:
#                 move = whatsapp.wait_for_id(blackID).body
#             if move.lower() in ['resign', 'quit']:
#                 return 'resign'
#             return chess.Move.from_uci(move)
#         except ValueError:
#             whatsapp.send("Invalid move. Try again.")

# def main():
#     global resign
#     resign = False
#     board = chess.Board()
#     if(not no_limit):
#         win_checkThread = threading.Thread(target=countdown, args=(board,))
#         win_checkThread.start()
#     while not board.is_game_over():
#         display_board(board)
#         move = get_move(board=board.turn)

#         if move == 'resign':
#             resign = True
#             if(not no_limit):
#                 win_checkThread.join()
#             whatsapp.send(f"{'White' if board.turn else 'Black'} has resigned. {'Black' if board.turn else 'White'} wins!")
#             return

#         if move in board.legal_moves:
#             board.push(move)
#         else:
#             whatsapp.send("Invalid move. Try again.")

#     display_board(board)
#     whatsapp.send(f"Game Over. {'Black' if board.turn else 'White'} wins!")

# @commands.command(aliases=["Chess"])
# def chess(ctx):
#     global no_limit, whiteTime, blackTime, whiteID, blackID
#     whatsapp.send("Set Time, `Time constraint [0 <= Time <= 15]`")
#     ctxx = whatsapp.wait_for_id(ctx.id[-17:])
#     if(ctxx.body == "0"):
#         no_limit = True
#     else:
#         no_limit = False
#         try:
#             if(int(ctxx.body) > 15 or int(ctxx.body) < 0):
#                 whatsapp.send("Valid Time constraint [0 <= Time <= 15]")
#                 return
#         except:
#             whatsapp.send(f"Invalid time limit '{ctxx.body}'")
#             return
        
#         whiteTime = int(ctxx.body)
#         whiteID = ctx.id[-17:]
#         blackID = ctx.mention[-1]
#         blackTime = int(ctxx.body)
#         main()
# if __name__ == "__main__":
#     main()
import whatsapp
print(whatsapp._on_message_thread_)