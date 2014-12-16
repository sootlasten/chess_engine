# C H E S S   E N G I N E .

from constants import *
import time

class Board(object):
    
    def __init__(self):
        """ Creates a new board with all the pieces at their original positions.
            Also initializes a variable that holds an en_passant square.
        """
        self.board = []
        for square in range(128):
            self.board.append(EMPTY)

        # Put all the black pieces in place. 
        self.board[0], self.board[7] = black_rook1, black_rook2
        self.board[1], self.board[6] = black_knight1, black_knight2
        self.board[2], self.board[5] = black_bishop1, black_bishop2
        self.board[3] = black_queen
        self.board[4] = black_king
        
        self.board[16] = black_pawn1
        self.board[17] = black_pawn2
        self.board[18] = black_pawn3
        self.board[19] = black_pawn4
        self.board[20] = black_pawn5
        self.board[21] = black_pawn6
        self.board[22] = black_pawn7
        self.board[23] = black_pawn8
            
        # Put all the white pieces in place.
        self.board[112], self.board[119] = white_rook1, white_rook2
        self.board[113], self.board[118] = white_knight1, white_knight2
        self.board[114], self.board[117] = white_bishop1, white_bishop2
        self.board[115] = white_queen
        self.board[116] = white_king
                                    
        self.board[96] = white_pawn1
        self.board[97] = white_pawn2
        self.board[98] = white_pawn3
        self.board[99] = white_pawn4
        self.board[100] = white_pawn5
        self.board[101] = white_pawn6
        self.board[102] = white_pawn7
        self.board[103] = white_pawn8

        self.passant_square = None
        self.move_count = 0

    def getOtherPlayer(self, player):
        """ Returns the other Player object. """
        if player == white_player:
            return black_player
        else:
            return white_player

    def getState(self):
        """ Returns the current state of the board data structure. """
        return self.board

    def getPiece(self, square):
        """ Returns a piece that is on a given square. """
        return self.board[square]

    def setPiece(self, square, piece):
        """ Put a piece on the square or makes a square empty. """
        self.board[square] = piece

    def getMoveCount(self):
        return self.move_count

    def isSquareUnderAttack(self, rules, square, player):
        """ Returns True if the square is under attack by a given player's piece. """
        players_color = player.getColor()
        other_players_color = self.getOtherPlayer(player).getColor()
        
        # Knight attacks.
        for knight_move in (14, 18, -14, -18, 31, 33, -31, -33):
            attack_square = square + knight_move
            if not attack_square & 0x88:
                piece = self.getPiece(attack_square)
                if piece and piece.getType() == KNIGHT and piece.getColor() == players_color:
                    return True

        # Check for every other piece attacks.
        for other_move in (-17, -16, -15, 1, 17, 16, 15, -1):
            attack_square = square + other_move
            if not attack_square & 0x88:
                piece = self.getPiece(attack_square)
                
                if not piece or (piece and piece.getColor() != other_players_color):
                    # King attacks.
                    if piece and piece.getType() == KING and piece.getColor() == players_color:
                        return True

                    # Pawn attacks.
                    elif piece and piece.getType() == PAWN:
                        if players_color == WHITE and other_move in (17, 15):
                            return True
                        elif players_color == BLACK and other_move in (-17, -15):
                            return True

                    while True:
                        if piece:
                            # Queen attacks.
                            if piece.getType() == QUEEN and piece.getColor() == players_color:
                                return True

                            # Bishop attacks.
                            elif piece.getType() == BISHOP and other_move in (-17, -15, 17, 15):
                                return True

                            # Rook attacks.
                            elif piece.getType() == ROOK and other_move in (-1, -16, 1, 16):
                                return True

                            else:
                                break

                        attack_square += other_move
                        if not attack_square & 0x88:
                            piece = self.getPiece(attack_square)
                            if piece and piece.getColor() == other_players_color:
                                break
                        else:
                            break

        return False 

    def getPassantSquare(self):
        return self.passant_square

    def generatePieceMoves(self, rules, piece, player):
        """ Returns a list of Move objects representing legal moves the piece can make. """
        valid_moves = []
        piece_pos = piece.getPosition()
        piece_type = piece.getType()
        piece_delta = piece.getDelta()
        
        for move_in_delta in piece_delta:
            target_square = piece_pos + move_in_delta
            move = self.createMoveObject(piece_pos, target_square, player)

            if piece_type & 4:
                while not target_square & 0x88 and not self.getPiece(target_square):
                    if rules.isPseudoLegal(move, self, player):
                        if rules.isLegal(move, self, player):
                            valid_moves.append(move)
                    target_square += move_in_delta
                    move = self.createMoveObject(piece_pos, target_square, player)

            if rules.isPseudoLegal(move, self, player):
                if rules.isLegal(move, self, player):
                    valid_moves.append(move)

        if piece_type == KING:
            if player.getShortCastle():
                move = self.createMoveObject(piece_pos, piece_pos + 2, player)
                if rules.isPseudoLegal(move, self, player):
                    if rules.isLegal(move, self, player):
                        valid_moves.append(move)

            if player.getLongCastle():
                move = self.createMoveObject(piece_pos, piece_pos - 2, player)
                if rules.isPseudoLegal(move, self, player):
                    if rules.isLegal(move, self, player):
                        valid_moves.append(move)

        return valid_moves

    def generateCaptures(self, rules, player):
        """ Returns a list of Move objects that are pseudo-legal captrues. """
        captures = []
        piece_dict = player.getPieceDict()

        for piece_type in piece_dict:
            for piece in piece_dict[piece_type]:
                piece_pos = piece.getPosition()
                for move_in_delta in piece.getDelta():
                    target_square = piece_pos + move_in_delta

                    if piece_type & 4:  # Sliding piece.
                        while not target_square & 0x88 and not self.getPiece(target_square):
                            target_square += move_in_delta

                    move = self.createMoveObject(piece_pos, target_square, player)
                    if rules.isPseudoLegal(move, self, player) and self.getPiece(target_square):
                        move = self.createMoveObject(piece_pos, target_square, player)
                        captures.append(move)

        return captures

    def generateNonCaptures(self, rules, player):
        """ Returns a list of Move objects that are pseudo-legal non-captures. """
        non_captures = []
        piece_dict = player.getPieceDict()

        for piece_type in piece_dict:
            for piece in piece_dict[piece_type]:
                piece_pos = piece.getPosition()
                for move_in_delta in piece.getDelta():
                    target_square = piece_pos + move_in_delta
                    move = self.createMoveObject(piece_pos, target_square, player)

                    if piece_type & 4:  # Sliding piece.
                        while not target_square & 0x88 and not self.getPiece(target_square):
                            if rules.isPseudoLegal(move, self, player):
                                non_captures.append(move)
                            target_square += move_in_delta
                            move = self.createMoveObject(piece_pos, target_square, player)

                    if rules.isPseudoLegal(move, self, player) and not self.getPiece(target_square):
                        non_captures.append(move)

        if player.getShortCastle():
            kings_pos = player.getPieceDict()[KING][0].getPosition()
            move = self.createMoveObject(kings_pos, kings_pos + 2, player)
            if rules.isPseudoLegal(move, self, player):
                non_captures.append(move)

        if player.getLongCastle():
            kings_pos = player.getPieceDict()[KING][0].getPosition()
            move = self.createMoveObject(kings_pos, kings_pos - 2, player)
            if rules.isPseudoLegal(move, self, player):
                non_captures.append(move)

        return non_captures
                    
    def makeMove(self, move, player):
        """ Makes a move on the board and changes Piece object. Returns None. """
        moved_piece = move.getPiece()
        captured_piece = move.getCapturedPiece()
        special_move = move.getSpecialMove()
        self.passant_square = None

        self.move_count += 1

        # CASTLING.
        if moved_piece.getType() == KING:
            # King's move sets both castling flags False.
            player.changeShortCastle(False)
            player.changeLongCastle(False)

            if special_move == SHORT_CASTLE:
                # Move rook when short castling.
                castling_rook = self.getPiece(move.getTargetSquare() + 1)
                rook_target = move.getTargetSquare() - 1
                
                self.setPiece(rook_target, castling_rook)
                self.setPiece(castling_rook.getPosition(), EMPTY)

                castling_rook.changePosition(rook_target)  # Change's Piece object's position (rook). 

            elif special_move == LONG_CASTLE:
                 # Move rook when long castling.
                castling_rook = self.getPiece(move.getTargetSquare() - 2)
                rook_target = move.getTargetSquare() + 1
                
                self.setPiece(rook_target, castling_rook)
                self.setPiece(castling_rook.getPosition(), EMPTY)
                
                castling_rook.changePosition(rook_target)  # Change's Piece object's position (rook).

        elif moved_piece.getType() == ROOK:
            # Rook move set's castling flag False on that side.
            if player.getColor() == WHITE:
                # White player.
                if moved_piece.getPosition() == 119:
                    player.changeShortCastle(False)
                elif moved_piece.getPosition() == 112:
                    player.changeLongCastle(False)

            else:
                # Black player.
                if moved_piece.getPosition() == 7:
                    player.changeShortCastle(False)
                elif moved_piece.getPosition() == 0:
                    player.changeLongCastle(False)

        # EN PASSANT.
        if special_move == EN_PASSANT:
            if player.getColor() == WHITE:
                self.setPiece(move.getTargetSquare() + 16, EMPTY)
            else:
                self.setPiece(move.getTargetSquare() - 16, EMPTY)

        # Get en passant square if pawn moved 2 squares at the beginning.
        if moved_piece.getType() == PAWN:
            self.move_count = 0
            if player.getColor() == WHITE and moved_piece.getPosition() / 16 == 6 and \
               move.getOriginSquare() - move.getTargetSquare() == 32:
                self.passant_square = move.getTargetSquare() + 16
            elif player.getColor() == BLACK and moved_piece.getPosition() / 16 == 1 and \
                 move.getTargetSquare() - move.getOriginSquare() == 32:
                self.passant_square = move.getTargetSquare() - 16
                
                          
        # PROMOTION.
        if special_move == PROMOTION:
            # Get a new piece object.
            if player.getColor() == WHITE:
                new_piece = Piece(QUEEN, WHITE, move.getTargetSquare(), QUEEN_VALUE, WHITE_QUEEN_TABLE, 'graphics/white_queen.png')
            else:
                new_piece = Piece(QUEEN, BLACK, move.getTargetSquare(), QUEEN_VALUE, BLACK_QUEEN_TABLE, 'graphics/black_queen.png')
            self.setPiece(new_piece.getPosition(), new_piece)
            self.setPiece(moved_piece.getPosition(), EMPTY)
            player.addPiece(new_piece)
            player.removePiece(moved_piece)
            
        else:
            self.setPiece(move.getTargetSquare(), moved_piece)  # Set moved piece on target square.
            self.setPiece(moved_piece.getPosition(), EMPTY)  # Make the origin square empty.
            moved_piece.changePosition(move.getTargetSquare())  # Change piece object's position.

        if captured_piece:  # Remove captured piece from other player's piece dict.
            self.getOtherPlayer(player).removePiece(captured_piece)
            self.move_count = 0

    def unmakeMove(self, move, player):
        """ Unmakes a move on the board. Returns None. """
        moved_piece = move.getPiece()
        captured_piece = move.getCapturedPiece()
        special_move = move.getSpecialMove()

        # Set move count, castling and en passant count back.
        prev_pos = move.getPreviousPosition()
        self.passant_square = prev_pos[0]
        player.changeShortCastle(prev_pos[1])
        player.changeLongCastle(prev_pos[2])
        self.move_count = prev_pos[3]
        
        if special_move == PROMOTION:
            new_piece = self.getPiece(move.getTargetSquare())
            player.removePiece(new_piece)  # Remove the new piece from the player's piece dictionary.
            player.addPiece(moved_piece)  # Put promoted piece back to player's piece dict.

        elif special_move == EN_PASSANT:
            self.setPiece(captured_piece.getPosition(), captured_piece)
            self.setPiece(move.getTargetSquare(), EMPTY) 

        elif special_move == SHORT_CASTLE:
            # Move rook back when short castling.
            castling_rook = self.getPiece(move.getTargetSquare() - 1)
            rook_target = move.getTargetSquare() + 1
            
            self.setPiece(rook_target, castling_rook)
            self.setPiece(castling_rook.getPosition(), EMPTY)

            castling_rook.changePosition(rook_target)  # Change's Piece object's position (rook). 
            
        elif special_move == LONG_CASTLE:
            # Move rook back when long castling.
            castling_rook = self.getPiece(move.getTargetSquare() + 1)
            rook_target = move.getTargetSquare() - 2

            self.setPiece(rook_target, castling_rook)
            self.setPiece(castling_rook.getPosition(), EMPTY)

            castling_rook.changePosition(rook_target)  # Change's Piece object's position (rook). 
            
        if special_move != EN_PASSANT:
            self.setPiece(move.getTargetSquare(), captured_piece)  # Put captured piece (or empty square) back to it's position.
        self.setPiece(move.getOriginSquare(), moved_piece)  # Put moved piece back to it's original position.
        moved_piece.changePosition(move.getOriginSquare())  # Change piece object's position.

        if captured_piece:  # Add captured piece to other player's piece dict.
            self.getOtherPlayer(player).addPiece(captured_piece)

    def createMoveObject(self, origin_square, target_square, player):
        """ Create a move object. """
        moved_piece = self.getPiece(origin_square)
        try:
            captured_piece = self.getPiece(target_square)  # or empty square.
        except:
            captured_piece = None
        special = None
        prev_pos = [self.passant_square, player.getShortCastle(), player.getLongCastle(), self.move_count]
        
        # If origin square is empty, return EMPTY. 
        if moved_piece == EMPTY:
            return EMPTY

        elif moved_piece.getType() == PAWN:
            # Pawn promotion.
            if (moved_piece.getColor() == WHITE and target_square / 16 == 0 and origin_square / 16 == 1) or \
               (moved_piece.getColor() == BLACK and target_square / 16 == 7) and origin_square / 16 == 6:
                    special = PROMOTION

            # En passant.
            if (abs(target_square - origin_square) == 15 or abs(target_square - origin_square) == 17) \
               and not captured_piece:
                if moved_piece.getColor() == WHITE:
                    if target_square / 16 == 2:
                        special = EN_PASSANT
                        captured_piece = self.getPiece(target_square + 16)
                else:
                    if target_square / 16 == 5:
                        special = EN_PASSANT
                        captured_piece = self.getPiece(target_square - 16)
            
        elif moved_piece.getType() == KING:
            # Castling.
            diff = target_square - origin_square
            if abs(diff) == 2:
                if diff > 0:
                    special = SHORT_CASTLE
                else:
                    special = LONG_CASTLE

        return Move(moved_piece, origin_square, target_square, captured_piece, special, prev_pos)


class Piece(object):

    def __init__(self, piece_type, color, position, value, piece_table, graphics):
        """ Set up piece information variables. """
        self.type = piece_type
        self.color = color
        self.position = position
        self.value = value
        self.piece_table = piece_table
        self.graphics = graphics 

    def getType(self):
        """ Returns the type of the piece. """
        return self.type

    def getColor(self):
        """ Returns the color of the piece. """
        return self.color

    def getPosition(self):
        """ Returns the position of the piece. """
        return self.position

    def getValue(self):
        """ Returns the piece's value. """
        return self.value

    def changePosition(self, new_position):
        """ Changes the position of the piece. """
        self.position = new_position

    def insertNewPieceTable(self, new_table):
        """ Replaces the piece's old piece-square table with a new one. """
        self.piece_table = new_table 

    def getPieceTableValue(self):
        """ Returns the piece's square table value based on the position of the piece. """
        return self.piece_table[self.position] 

    def loadImage(self, image):
        self.image = image

    def getImage(self):
        """ Returns the graphics of the piece. """
        return self.image
    
    def getDelta(self):
        """ Returns a tuple of the piece's deltas. """
        if self.type == PAWN:  # Pawn.
            if self.color == WHITE:
                delta = (-16, -32, -15, -17)
            elif self.color == BLACK:
                delta = (16, 32, 15, 17)
        elif self.type == KNIGHT:  # Knight. 
            delta = (-33, -31, -14, 18, 33, 31, 14, -18)
        elif self.type == BISHOP:  # Bishop. 
            delta = (-17, -15, 17, 15)
        elif self.type == ROOK:  # Rook. 
            delta = (-1, -16, 1, 16)
        else:  # Queen or King. 
            delta = (-17, -16, -15, 1, 17, 16, 15, -1)
        return delta
            

class Move(object):
    
    def __init__(self, piece, origin_square, target_square, capture, special, prev_pos):
        """ Set up move infromation variables. """
        self.piece = piece
        self.origin_square = origin_square
        self.target_square = target_square
        self.captured_piece = capture
        self.special = special
        self.prev_pos = prev_pos
                    
    def getPiece(self):
        """ Returns the piece object that is moved. """
        return self.piece

    def getOriginSquare(self):
        """ Returns the square the moved piece is taken from. """
        return self.origin_square

    def getTargetSquare(self):
        """ Returns the square the moved piece is put. """
        return self.target_square

    def getCapturedPiece(self):
        """ Returns the captured piece. """
        return self.captured_piece

    def getSpecialMove(self):
        """ If a move is 'special', returns the distinctive value. Otherwise None. """
        return self.special

    def getPreviousPosition(self):
        """ Returns a list about the previous position's information. """
        return self.prev_pos

    def __eq__(self, other):
        """ Overrides the normal __eg__ method. """
        return (self.origin_square == other.origin_square) and \
               (self.target_square == other.target_square)
    

class Player(object):

    def __init__(self, name, color, player_type):
        """ Initializes some variables and sets up the piece dictionary which contains all the player's piece objects
            still on the board.
        """
        self.name = name
        self.color = color
        self.type = player_type
        self.long_castle = True
        self.short_castle = True

        # Set up the piece dictionary.
        if self.color == WHITE:
            self.piece_dict = {PAWN: [white_pawn1, white_pawn2, white_pawn3, white_pawn4,
                                      white_pawn5, white_pawn6, white_pawn7, white_pawn8],
                               KNIGHT: [white_knight1, white_knight2],
                               BISHOP: [white_bishop1, white_bishop2],
                               ROOK: [white_rook1, white_rook2],
                               QUEEN: [white_queen],
                               KING: [white_king]}

        else:
            self.piece_dict = {PAWN: [black_pawn1, black_pawn2, black_pawn3, black_pawn4,
                                      black_pawn5, black_pawn6, black_pawn7, black_pawn8],
                               KNIGHT: [black_knight1, black_knight2],
                               BISHOP: [black_bishop1, black_bishop2],
                               ROOK: [black_rook1, black_rook2],
                               QUEEN: [black_queen],
                               KING: [black_king]}

    def getName(self):
        """ Returns player's name. """
        return self.name

    def getColor(self):
        """ Returns player's color. """
        return self.color

    def getType(self):
        """ Returns player's type (computer or human). """
        return self.type

    def getShortCastle(self):
        """ Returns True if short castling is allowed. """
        return self.short_castle

    def getLongCastle(self):
        """ Returns True if long castling is allowed. """
        return self.long_castle

    def changeShortCastle(self, boolean):
        """ Changes short castling rights. """
        self.short_castle = boolean

    def changeLongCastle(self, boolean):
        """ Changes long castling rights. """
        self.long_castle = boolean

    def getPieceDict(self):
        """ Return the the piece dictionary containing all player's pieces. """
        return self.piece_dict

    def removePiece(self, piece):
        """ Removes a piece from the piece dictionary. """
        piece_type = piece.getType()
        for i in range(len(self.piece_dict[piece_type])):
            if self.piece_dict[piece_type][i]  == piece:
                del self.piece_dict[piece_type][i]
                break

    def addPiece(self, piece):
        """ Adds a piece to the piece dictionary. """
        self.piece_dict[piece.getType()].append(piece)

   
class Rules(object):

    def isPathClear(self, origin_square, target_square, step, board):
        """ Returns True if the horizontal, vertical or diagonal path between two squares is empty. """
        # The base case, where origin square and target square are only one square apart.
        if target_square - origin_square == step:
            return True

        # Change the origin square one square closer to target square.
        origin_square += step
        
        if board.getPiece(origin_square):
            return False

        return self.isPathClear(origin_square, target_square, step, board)

    def isPseudoLegal(self, move, board, player):
        """ Returns True if a given move is pseudo legal. """

        # Check if trying to move an empty square.
        if not move:
            return False

        origin_square = move.getOriginSquare()
        target_square = move.getTargetSquare()

        # Check if target square is inside the board.
        if target_square & 0x88:
            return False
        
        origin_piece = move.getPiece()
        captured_piece = move.getCapturedPiece()

        # Check if trying to move to the same square.
        if origin_square == target_square:
            return False

        # Check if target square is occupied by a piece with the same color.
        if captured_piece and player.getColor() == captured_piece.getColor():
            return False

        # Check if trying to move enemy's piece.
        if origin_piece.getColor() != player.getColor():
            return False 

        diff = target_square - origin_square

        # Pawn.
        if origin_piece.getType() == PAWN:
            # Move not in pawn's move delta.
            if diff not in origin_piece.getDelta():
                return False

            # Can't move directly ahead if pieces are blocking.
            elif diff in origin_piece.getDelta()[:2] and captured_piece:
                return False

            # Can't move 2 squares if not at the starting position.
            elif diff == origin_piece.getDelta()[1] and (origin_square / 16 != 1 and origin_square / 16 != 6):
                return False
 
            # Can't move 2 squares ahead if piece is blocking.
            elif diff == origin_piece.getDelta()[1] and board.getPiece(origin_square + origin_piece.getDelta()[0]):
                return False

            # En passant.
            elif move.getSpecialMove() == EN_PASSANT and target_square != board.getPassantSquare():
                return False 

            # Can't move diagonally if there are no enemy pieces.
            elif diff in origin_piece.getDelta()[2:] and not captured_piece:
                return False

        # Knight.
        elif origin_piece.getType() == KNIGHT:
            if diff not in origin_piece.getDelta():
                return False

        # Bishop.
        elif origin_piece.getType() == BISHOP:
            if diff % 17 and diff % 15:
                return False

        # Rook.
        elif origin_piece.getType() == ROOK:
            if diff % 16 and abs(diff) > 8:
                return False

        # Queen.
        elif origin_piece.getType() == QUEEN:
            if (diff % 17 and diff % 15) and (diff % 16 and abs(diff) > 8):
                return False

        # King.
        elif origin_piece.getType() == KING:
            # Short castling. 
            if move.getSpecialMove() == SHORT_CASTLE:
                if player.getShortCastle() and \
                not board.getPiece(origin_square + 1) and \
                not board.getPiece(origin_square + 2):
                    return True

            # Long castling.
            elif move.getSpecialMove() == LONG_CASTLE:
                if player.getLongCastle() and \
                not board.getPiece(origin_square - 1) and \
                not board.getPiece(origin_square - 2) and \
                not board.getPiece(origin_square - 3):
                    return True

            if diff not in origin_piece.getDelta():
                return False
            
        # See if a path between origin and target square is clear for sliding pieces. 
        if origin_piece.getType() & 4:
            if diff % 17 == 0:
                step = 17
            elif diff % 16 == 0:
                step = 16
            elif diff % 15 == 0:
                step = 15
            else:
                step = 1

            if diff < 0:
                step *= -1

            if not self.isPathClear(origin_square, target_square, step, board):
                return False

        return True  # If all the other tests were false.
    
    def isLegal(self, move, board, player):
        """ Returns True if the player's move is legal. """
        if move.getSpecialMove() == SHORT_CASTLE:
            square = move.getOriginSquare()
            while square < (move.getTargetSquare() + 1):
                if board.isSquareUnderAttack(self, square, board.getOtherPlayer(player)):
                    return False
                square += 1

        elif move.getSpecialMove() == LONG_CASTLE:
            square = move.getOriginSquare()
            while square > (move.getTargetSquare() - 2):
                if board.isSquareUnderAttack(self, square, board.getOtherPlayer(player)):
                    return False
                square -= 1
                    
        board.makeMove(move, player)
        
        if not self.isInCheck(board, player):
            board.unmakeMove(move, player)
            return True
        
        board.unmakeMove(move, player)
            
        return False
        
    def isInCheck(self, board, player):
        """ Returns True if player's king is in check. """
        # get opponent's Player object.
        opponent = board.getOtherPlayer(player)

        player.getPieceDict()[KING]
        king_position = player.getPieceDict()[KING][0].getPosition()
        if board.isSquareUnderAttack(self, king_position, opponent):
            return True

        return False

    def isCheckMate(self, board, player):
        """ Returns True if player is in checkmate. """
        if not self.isInCheck(board, player):
            return False

        king_pos = player.getPieceDict()[KING][0].getPosition()
        king_delta = player.getPieceDict()[KING][0].getDelta()
        
        for move_in_delta in king_delta:
            move = board.createMoveObject(king_pos, king_pos + move_in_delta, player)
            if self.isPseudoLegal(move, board, player):
                if self.isLegal(move, board, player):
                    return False

        piece_dict = player.getPieceDict()
        for piece_type in piece_dict:
            if piece_type == KING:
                continue
            for piece in piece_dict[piece_type]:
                piece_moves = board.generatePieceMoves(self, piece, player)
                if piece_moves:
                    return False
                
        return True

    def isStaleMate(self, board, player):
        """ Returns True if a player has reached a stalemate. """
        if self.isInCheck(board, player):
            return False

        piece_dict = player.getPieceDict()

        for piece_type in piece_dict:
            for piece in piece_dict[piece_type]:
                piece_pos = piece.getPosition()
                piece_delta = piece.getDelta()
                for move_in_delta in piece_delta:
                    target_square = piece_pos + move_in_delta
                    move = board.createMoveObject(piece_pos, target_square, player)

                    if self.isPseudoLegal(move, board, player):
                        if self.isLegal(move, board, player):
                            return False

                    if piece_type & 4:
                        while not target_square & 0x88 and not board.getPiece(target_square):
                            target_square += move_in_delta
                            move_object = board.createMoveObject(piece_pos, target_square, player)
                            if self.isPseudoLegal(move, board, player):
                                if self.isLegal(move, board, player):
                                    return False

        return True

    def isMaterialDraw(self):
        """ Returns True if game is a draw due to lack of material. """
        # Boolenas for draw by material detection. 
        white_has_bishop = False
        white_has_knight = False
        black_has_bishop = False
        black_has_knight = False 
        
        for piece_type in white_player.getPieceDict():
            for piece in white_player.getPieceDict()[piece_type]:
                # Check pieces for draw by material detections.  
                if piece_type == PAWN or piece_type == QUEEN or piece_type == ROOK:
                    return False 
                elif (piece_type == BISHOP or piece_type == KNIGHT) and (white_has_knight or white_has_bishop):
                    return False 
                elif piece_type == BISHOP:
                    white_has_bishop = True
                elif piece_type == KNIGHT:
                    white_has_knight = True

        for piece_type in black_player.getPieceDict():
            for piece in black_player.getPieceDict()[piece_type]:
                # Check pieces for draw by material detection.
                if piece_type == PAWN or piece_type == QUEEN or piece_type == ROOK:
                    return False 
                elif (piece_type == BISHOP or piece_type == KNIGHT) and (black_has_bishop or black_has_knight):
                    return False 
                elif piece_type == BISHOP:
                    black_has_bishop = True
                elif piece_type == KNIGHT:
                    black_has_knight = True

        return True


class Engine(object):              
                                   
    def mateCheck(self, rules, board, player, ply):
        """ Checks for checkmate and stalemate. """
        # Check for checkmate.
        if rules.isCheckMate(board, player):
            return -(MATE_VALUE + ply)

        # Check for stalemate.
        else:
            return DRAW_VALUE

    def positionEvaluation(self, board, rules, player):
        """ Evaluates the current position on board. """
        if rules.isCheckMate(board, player):  # Check for checkmate. 
            return -MATE_VALUE

        elif rules.isStaleMate(board, player):  # Check for stalemate.
            return DRAW_VALUE

        value = 0

        # Booleans for draw by material detection. 
        draw_by_material = True
        white_has_bishop = False
        white_has_knight = False
        black_has_bishop = False
        black_has_knight = False

        # Booleans for material on board detection.
        white_end_game = False
        white_end_game = False
        white_pieces = 0
        black_pieces = 0
        
        for piece_type in white_player.getPieceDict():
            for piece in white_player.getPieceDict()[piece_type]:
                piece_value = piece.getValue()
                value += piece_value
                white_pieces += piece_value
                value += piece.getPieceTableValue()
                # Check pieces for draw by material detections.  
                if piece_type == PAWN or piece_type == QUEEN or piece_type == ROOK:
                    draw_by_material = False
                elif (piece_type == BISHOP or piece_type == KNIGHT) and (white_has_knight or white_has_bishop):
                    draw_by_material = False
                elif piece_type == BISHOP:
                    white_has_bishop = True
                elif piece_type == KNIGHT:
                    white_has_knight = True

        for piece_type in black_player.getPieceDict():
            for piece in black_player.getPieceDict()[piece_type]:
                piece_value = piece.getValue()
                value -= piece_value
                black_pieces += piece_value
                value -= piece.getPieceTableValue()
                # Check pieces for draw by material detection.
                if piece_type == PAWN or piece_type == QUEEN or piece_type == ROOK:
                    draw_by_material = False
                elif (piece_type == BISHOP or piece_type == KNIGHT) and (black_has_bishop or black_has_knight):
                    draw_by_material = False
                elif piece_type == BISHOP:
                    black_has_bishop = True
                elif piece_type == KNIGHT:
                    black_has_knight = True
                    
        if draw_by_material or board.getMoveCount() >= 50:
            return DRAW_VALUE

        if white_pieces <= 21300 and black_pieces <= 21300:
            white_player.getPieceDict()[KING][0].insertNewPieceTable(WHITE_KING_END_TABLE)
            black_player.getPieceDict()[KING][0].insertNewPieceTable(BLACK_KING_END_TABLE)

        else:
            white_player.getPieceDict()[KING][0].insertNewPieceTable(WHITE_KING_MIDDLE_TABLE)
            black_player.getPieceDict()[KING][0].insertNewPieceTable(BLACK_KING_MIDDLE_TABLE)

        return value * player.getColor()

    def iterativeDeepening(self, board, rules, player):
        """ Iterative deepening framework. Returns the optimal move sequenece for player. """
        self.pv = []
        self.prev_pv = []
        self.use_pv = False
        self.current_depth = 1
        alpha = -150000
        beta = 150000
        
        while self.current_depth < 5:
            self.use_null_move = False
            ply = self.current_depth
            
            current_eval = self.alphaBeta(board, rules, alpha, beta, ply, player, self.pv)
            
            self.use_pv = True            
            self.prev_pv = self.pv
            self.pv = []

            self.current_depth += 1

            if abs(current_eval) >= MATE_VALUE:
                break
            
        return self.prev_pv
            
    def moveOrdering(self, captures, non_captures, ply):
        """ Orders the moves in the following order: pv, captures, non-captures. """
        moves = self.captureOrdering(captures)
        moves.extend(non_captures)
        ordered_moves = []

        # Use the previous iteration's best move.
        if self.use_pv and ply > 1:
            pv_move = self.prev_pv[self.current_depth - ply]
            ordered_moves.append(pv_move)
            moves.remove(pv_move)

        ordered_moves.extend(moves)

        return ordered_moves

    def captureOrdering(self, captures):
        """ Orders captures by the MVV / LVA scheme. """
        ordered_moves = []
        
        PxQ = []
        NxQ = []
        BxQ = []
        RxQ = []
        QxQ = []
        KxQ = []

        PxR = []
        NxR = []
        BxR = []
        RxR = []
        QxR = []
        KxR = []

        PxB = []
        NxB = []
        BxB = []
        RxB = []
        QxB = []
        KxB = []

        PxN = []
        NxN = []
        BxN = []
        RxN = []
        QxN = []
        KxN = []

        PxP = []
        NxP = []
        BxP = []
        RxP = []
        QxP = []
        KxP = []

        for move in captures:
            attacker = move.getPiece().getType()
            victim = move.getCapturedPiece().getType()

            if victim == QUEEN:
                if attacker == PAWN:
                    PxQ.append(move)
                elif attacker == KNIGHT:
                    NxQ.append(move)
                elif attacker == BISHOP:
                    BxQ.append(move)
                elif attacker == ROOK:
                    RxQ.append(move)
                elif attacker == QUEEN:
                    QxQ.append(move)
                else:
                    KxQ.append(move)

            elif victim == ROOK:
                if attacker == PAWN:
                    PxR.append(move)
                elif attacker == KNIGHT:
                    NxR.append(move)
                elif attacker == BISHOP:
                    BxR.append(move)
                elif attacker == ROOK:
                    RxR.append(move)
                elif attacker == QUEEN:
                    QxR.append(move)
                else:
                    KxR.append(move)

            elif victim == BISHOP:
                if attacker == PAWN:
                    PxB.append(move)
                elif attacker == KNIGHT:
                    NxB.append(move)
                elif attacker == BISHOP:
                    BxB.append(move)
                elif attacker == ROOK:
                    RxB.append(move)
                elif attacker == QUEEN:
                    QxB.append(move)
                else:
                    KxB.append(move)

            elif victim == KNIGHT:
                if attacker == PAWN:
                    PxN.append(move)
                elif attacker == KNIGHT:
                    NxN.append(move)
                elif attacker == BISHOP:
                    BxN.append(move)
                elif attacker == ROOK:
                    RxN.append(move)
                elif attacker == QUEEN:
                    QxN.append(move)
                else:
                    KxN.append(move)

            elif victim == PAWN:
                if attacker == PAWN:
                    PxP.append(move)
                elif attacker == KNIGHT:
                    NxP.append(move)
                elif attacker == BISHOP:
                    BxP.append(move)
                elif attacker == ROOK:
                    RxP.append(move)
                elif attacker == QUEEN:
                    QxP.append(move)
                else:
                    KxP.append(move)

        ordered_moves.extend(PxQ)
        ordered_moves.extend(NxQ)
        ordered_moves.extend(BxQ)
        ordered_moves.extend(RxQ)
        ordered_moves.extend(QxQ)
        ordered_moves.extend(KxQ)

        ordered_moves.extend(PxR)
        ordered_moves.extend(NxR)
        ordered_moves.extend(BxR)
        ordered_moves.extend(RxR)
        ordered_moves.extend(QxR)
        ordered_moves.extend(KxR)

        ordered_moves.extend(PxB)
        ordered_moves.extend(NxB)
        ordered_moves.extend(BxB)
        ordered_moves.extend(RxB)
        ordered_moves.extend(QxB)
        ordered_moves.extend(KxB)

        ordered_moves.extend(PxN)
        ordered_moves.extend(NxN)
        ordered_moves.extend(BxN)
        ordered_moves.extend(RxN)
        ordered_moves.extend(QxN)
        ordered_moves.extend(KxN)

        ordered_moves.extend(PxP)
        ordered_moves.extend(NxP)
        ordered_moves.extend(BxP)
        ordered_moves.extend(RxP)
        ordered_moves.extend(QxP)
        ordered_moves.extend(KxP)

        return ordered_moves

    def alphaBeta(self, board, rules, alpha, beta, ply, player, pv):
        """ Implements a minimax algorithm with alpha-beta pruning. """
        if ply <= 0:
            return self.quiescenceSearch(board, rules, alpha, beta, player)

        captures = board.generateCaptures(rules, player)
        non_captures = board.generateNonCaptures(rules, player)

        if not len(captures) and not len(non_captures):
            return self.mateCheck(rules, board, player, ply)

        localpv = []

        # Null move reduction.
        if self.use_null_move and not self.use_pv:
            if not rules.isInCheck(board, player):
                R = 2
                self.use_null_move = False
                current_eval = -self.alphaBeta(board, rules, -beta, 1 - beta, ply - (R + 1), board.getOtherPlayer(player), localpv)

                if current_eval >= beta:
                    return current_eval

        move_list = self.moveOrdering(captures, non_captures, ply)

        for move in move_list:
            if rules.isLegal(move, board, player):
                board.makeMove(move, player)
                self.use_null_move = True
                current_eval = -self.alphaBeta(board, rules, -beta, -alpha, ply - 1, board.getOtherPlayer(player), localpv)
                board.unmakeMove(move, player)

                if current_eval >= beta:
                    return beta

                elif current_eval > alpha:
                    self.use_pv = False
                    
                    # Extract the principal variation.
                    if not pv:
                        pv.append(move)
                    else:
                        pv[0] = move

                    # Append local pv to global pv.
                    for i in range(len(localpv)):
                        if len(pv) - 2 < i:
                            pv.insert(i+1, localpv[i])
                        else:
                            pv[i+1] = localpv[i]
                        
                    alpha = current_eval
            
        return alpha

    def quiescenceSearch(self, board, rules, alpha, beta, player):
        stand_pat = self.positionEvaluation(board, rules, player)
        if stand_pat >= beta:
            return beta

        elif stand_pat > alpha:
            alpha = stand_pat
            
        captures = self.captureOrdering(board.generateCaptures(rules, player))
        for move in captures:
            if rules.isLegal(move, board, player):
                board.makeMove(move, player)
                current_eval = -self.quiescenceSearch(board, rules, -beta, -alpha, board.getOtherPlayer(player))
                board.unmakeMove(move, player)

                if current_eval >= beta:
                    return beta

                elif current_eval > alpha:
                    alpha = current_eval

        return alpha 
    

# -------------------------------------------------------------------
# Create instances of all of the piece objects! 
# White piece objects. 
white_pawn1 = Piece(PAWN, WHITE, 96, PAWN_VALUE, WHITE_PAWN_TABLE, 'graphics/white_pawn.png')
white_pawn2 = Piece(PAWN, WHITE, 97, PAWN_VALUE, WHITE_PAWN_TABLE, 'graphics/white_pawn.png')
white_pawn3 = Piece(PAWN, WHITE, 98, PAWN_VALUE, WHITE_PAWN_TABLE, 'graphics/white_pawn.png')
white_pawn4 = Piece(PAWN, WHITE, 99, PAWN_VALUE, WHITE_PAWN_TABLE, 'graphics/white_pawn.png')
white_pawn5 = Piece(PAWN, WHITE, 100, PAWN_VALUE, WHITE_PAWN_TABLE, 'graphics/white_pawn.png')
white_pawn6 = Piece(PAWN, WHITE, 101, PAWN_VALUE, WHITE_PAWN_TABLE, 'graphics/white_pawn.png')
white_pawn7 = Piece(PAWN, WHITE, 102, PAWN_VALUE, WHITE_PAWN_TABLE, 'graphics/white_pawn.png')
white_pawn8 = Piece(PAWN, WHITE, 103, PAWN_VALUE, WHITE_PAWN_TABLE, 'graphics/white_pawn.png')
white_knight1 = Piece(KNIGHT, WHITE, 113, KNIGHT_VALUE, WHITE_KNIGHT_TABLE, 'graphics/white_knight.png')
white_knight2 = Piece(KNIGHT, WHITE, 118, KNIGHT_VALUE, WHITE_KNIGHT_TABLE, 'graphics/white_knight.png')
white_bishop1 = Piece(BISHOP, WHITE, 114, BISHOP_VALUE, WHITE_BISHOP_TABLE, 'graphics/white_bishop.png')
white_bishop2 = Piece(BISHOP, WHITE, 117, BISHOP_VALUE, WHITE_BISHOP_TABLE, 'graphics/white_bishop.png')
white_rook1  = Piece(ROOK, WHITE, 112, ROOK_VALUE, WHITE_ROOK_TABLE, 'graphics/white_rook.png')
white_rook2 = Piece(ROOK, WHITE, 119, ROOK_VALUE, WHITE_ROOK_TABLE, 'graphics/white_rook.png')
white_queen = Piece(QUEEN, WHITE, 115, QUEEN_VALUE, WHITE_QUEEN_TABLE, 'graphics/white_queen.png')
white_king = Piece(KING, WHITE, 116, KING_VALUE, WHITE_KING_MIDDLE_TABLE, 'graphics/white_king.png')

# Black piece objects.
black_pawn1 = Piece(PAWN, BLACK, 16, PAWN_VALUE, BLACK_PAWN_TABLE, 'graphics/black_pawn.png')
black_pawn2 = Piece(PAWN, BLACK, 17, PAWN_VALUE, BLACK_PAWN_TABLE, 'graphics/black_pawn.png')
black_pawn3 = Piece(PAWN, BLACK, 18, PAWN_VALUE, BLACK_PAWN_TABLE, 'graphics/black_pawn.png')
black_pawn4 = Piece(PAWN, BLACK, 19, PAWN_VALUE, BLACK_PAWN_TABLE, 'graphics/black_pawn.png')
black_pawn5 = Piece(PAWN, BLACK, 20, PAWN_VALUE, BLACK_PAWN_TABLE, 'graphics/black_pawn.png')
black_pawn6 = Piece(PAWN, BLACK, 21, PAWN_VALUE, BLACK_PAWN_TABLE, 'graphics/black_pawn.png')
black_pawn7 = Piece(PAWN, BLACK, 22, PAWN_VALUE, BLACK_PAWN_TABLE, 'graphics/black_pawn.png')
black_pawn8 = Piece(PAWN, BLACK, 23, PAWN_VALUE, BLACK_PAWN_TABLE, 'graphics/black_pawn.png')
black_knight1 = Piece(KNIGHT, BLACK, 1, KNIGHT_VALUE, BLACK_KNIGHT_TABLE, 'graphics/black_knight.png')
black_knight2 = Piece(KNIGHT, BLACK, 6, KNIGHT_VALUE, BLACK_KNIGHT_TABLE, 'graphics/black_knight.png')
black_bishop1 = Piece(BISHOP, BLACK, 2, BISHOP_VALUE, BLACK_BISHOP_TABLE, 'graphics/black_bishop.png')
black_bishop2 = Piece(BISHOP, BLACK, 5, BISHOP_VALUE, BLACK_BISHOP_TABLE, 'graphics/black_bishop.png')
black_rook1  = Piece(ROOK, BLACK, 0, ROOK_VALUE, BLACK_ROOK_TABLE, 'graphics/black_rook.png')
black_rook2 = Piece(ROOK, BLACK, 7, ROOK_VALUE, BLACK_ROOK_TABLE, 'graphics/black_rook.png')
black_queen = Piece(QUEEN, BLACK, 3, QUEEN_VALUE, BLACK_QUEEN_TABLE, 'graphics/black_quuen.png')
black_king = Piece(KING, BLACK, 4, KING_VALUE, BLACK_KING_MIDDLE_TABLE, 'graphics/black_king.png')

# Create player object instances!
white_player = Player('sten', WHITE, HUMAN)
black_player = Player('maria', BLACK, COMPUTER)
