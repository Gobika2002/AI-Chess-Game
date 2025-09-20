# Chess AI - Enhanced Version
import cv2
import os
import numpy as np
import chess 
import chess.engine

# 🎨 Constants
SQUARE_SIZE = 80 # Size of each square on the chessboard
BOARD_SIZE = SQUARE_SIZE * 8 # Total size of the chessboard
WINDOW_WIDTH = BOARD_SIZE + 200 # Extra space for notation
WINDOW_HEIGHT = BOARD_SIZE + 100 # Extra space for status bar
LIGHT = (240, 240, 240) # Light square color
DARK = (100, 100, 160) # Dark square color
HIGHLIGHT = (0, 255, 0) # Highlight color

# ✅ Load Piece Images
def load_piece_images(path='assets'): # Load chess piece images
    pieces = {} # Dictionary to hold piece images
    for filename in os.listdir(path): # Iterate through files in the assets directory
        if filename.endswith('.png'): # Check for PNG files
            key = filename.split('.')[0]  # Get the piece key (e.g., "wP" for white pawn)
            img = cv2.imread(os.path.join(path, filename), cv2.IMREAD_UNCHANGED) # Read image with alpha channel
            if img is not None: # Check if image was loaded successfully
                pieces[key] = cv2.resize(img, (SQUARE_SIZE, SQUARE_SIZE)) # Resize to square size
    print(f"✅ Loaded {len(pieces)} piece images: {list(pieces.keys())}") # Log loaded piece images
    return pieces

# 🧩 Overlay PNG with Transparency
def overlay_piece(board_img, piece_img, x, y): # Overlay a piece image on the board
    if piece_img.shape[2] == 4: # Check for alpha channel
        alpha_s = piece_img[:, :, 3] / 255.0 # Get source alpha
        alpha_l = 1.0 - alpha_s # Get inverse alpha
        for c in range(3): # Iterate over color channels
            board_img[y:y+SQUARE_SIZE, x:x+SQUARE_SIZE, c] = ( 
                alpha_s * piece_img[:, :, c] +
                alpha_l * board_img[y:y+SQUARE_SIZE, x:x+SQUARE_SIZE, c] # Get background color
            )
    else:
        board_img[y:y+SQUARE_SIZE, x:x+SQUARE_SIZE] = piece_img # Overlay without transparency

# 🎯 Draw Notation
def draw_notation(canvas, x_offset, y_offset): # Draw algebraic notation
    font = cv2.FONT_HERSHEY_SIMPLEX # Font for text
    for col in range(8): # Draw column labels
        text = chr(ord('a') + col) # Column label (a-h)
        x = x_offset + col * SQUARE_SIZE + 25 # X position
        y = y_offset + BOARD_SIZE + 20 # Y position
        cv2.putText(canvas, text, (x, y), font, 0.5, (0, 0, 0), 1) # Draw column label
    for row in range(8): # Draw row labels
        text = str(8 - row) # Row label (1-8)
        x = x_offset - 20  # X position
        y = y_offset + row * SQUARE_SIZE + 45 # Y position
        cv2.putText(canvas, text, (x, y), font, 0.5, (0, 0, 0), 1) # Draw row label

# 🧠 Draw Board
def draw_board(board, piece_images, selected_square=None):
    img = np.zeros((BOARD_SIZE, BOARD_SIZE, 3), dtype=np.uint8)
    for row in range(8):
        for col in range(8):
            color = LIGHT if (row + col) % 2 == 0 else DARK
            cv2.rectangle(img, (col*SQUARE_SIZE, row*SQUARE_SIZE),
                          ((col+1)*SQUARE_SIZE, (row+1)*SQUARE_SIZE), color, -1)
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)
            if piece:
                key = ('w' if piece.color == chess.WHITE else 'b') + piece.symbol().upper()
                piece_img = piece_images.get(key)
                if piece_img is not None:
                    y, x = row*SQUARE_SIZE, col*SQUARE_SIZE
                    overlay_piece(img, piece_img, x, y)
            if selected_square == square:
                cv2.rectangle(img, (col*SQUARE_SIZE, row*SQUARE_SIZE),
                              ((col+1)*SQUARE_SIZE, row*SQUARE_SIZE + SQUARE_SIZE), HIGHLIGHT, 2)
    return img

# 🖱️ Mouse Interaction
selected_square = None
game_over = False
game_over_announced = False

def get_square_from_mouse(x, y, x_offset, y_offset):
    col = (x - x_offset) // SQUARE_SIZE
    row = (y - y_offset) // SQUARE_SIZE
    if 0 <= col < 8 and 0 <= row < 8:
        return chess.square(col, 7 - row)
    return None

# 🤖 AI Move Logic
engine_path = r"D:\OPEN CV\stockfish\stockfish-windows-x86-64-sse41-popcnt.exe" # Path to your Stockfish engine
engine = chess.engine.SimpleEngine.popen_uci(engine_path)

def ai_move(board, level=1):
    print("🤖 AI thinking...")
    time_limit = {1: 0.1, 2: 0.5, 3: 1.0}
    result = engine.play(board, chess.engine.Limit(time=time_limit.get(level, 0.1)))
    print(f"🤖 AI played: {result.move}")
    board.push(result.move)

# 🧵 Main Loop
board = chess.Board()
piece_images = load_piece_images()

def mouse_callback(event, x, y, flags, param):
    global selected_square, board, game_over, game_over_announced
    x_offset = (WINDOW_WIDTH - BOARD_SIZE) // 2
    y_offset = (WINDOW_HEIGHT - BOARD_SIZE) // 2

    if game_over:
        if not game_over_announced:
            print("🛑 Game is over. No moves allowed.")
            game_over_announced = True
        return

    if event == cv2.EVENT_LBUTTONDOWN:
        clicked = get_square_from_mouse(x, y, x_offset, y_offset)
        if clicked is None:
            return
        print(f"🖱️ Clicked: {chess.square_name(clicked)}")
        if selected_square:
            move = chess.Move(selected_square, clicked)
            print(f"🔁 Trying move: {move}")
            if move in board.legal_moves:
                board.push(move)
                print("✅ Move played")
                selected_square = None
                if board.is_game_over():
                    game_over = True
                    outcome = board.outcome()
                    print("🏁 Game Over!")
                    print("📜 Result:", outcome.result())
                    print("🧠 Reason:", outcome.termination.name)
                else:
                    ai_move(board)
                    if board.is_game_over():
                        game_over = True
                        outcome = board.outcome()
                        print("🏁 Game Over!")
                        print("📜 Result:", outcome.result())
                        print("🧠 Reason:", outcome.termination.name)
            else:
                print("❌ Illegal move")
                selected_square = None
        elif board.piece_at(clicked) and board.piece_at(clicked).color == chess.WHITE:
            selected_square = clicked
            print(f"🎯 Selected: {chess.square_name(selected_square)}")

cv2.namedWindow("Chess AI")
cv2.setMouseCallback("Chess AI", mouse_callback)

while True:
    canvas = np.ones((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8) * 255
    x_offset = (WINDOW_WIDTH - BOARD_SIZE) // 2
    y_offset = (WINDOW_HEIGHT - BOARD_SIZE) // 2
    board_img = draw_board(board, piece_images, selected_square)
    canvas[y_offset:y_offset+BOARD_SIZE, x_offset:x_offset+BOARD_SIZE] = board_img
    draw_notation(canvas, x_offset, y_offset)

    if game_over:
        outcome = board.outcome()
        result_text = f"Game Over: {outcome.result()} ({outcome.termination.name})"
        text_size = cv2.getTextSize(result_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        text_x = (WINDOW_WIDTH - text_size[0]) // 2
        cv2.putText(canvas, result_text, (text_x, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow("Chess AI", canvas)
    key = cv2.waitKey(20) & 0xFF
    if key == 27:  # ESC to quit
        break
    if key == ord('r'):
        board.reset()
        selected_square = None
        game_over = False
        game_over_announced = False
        print("🔄 Game restarted")

engine.quit()
cv2.destroyAllWindows()