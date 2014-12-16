# C H E S S  E N G I N E.

import pygame, sys
from pygame.locals import *
from engine import *

class Game(object):

    def __init__(self):
        self.board = Board()
        self.engine = Engine()
        self.rules = Rules()

    def screenToBoard(self, coordinates):
        """ Returns the board data structure squre given the screen coordinates. """
        x = int(coordinates[0] / 60)
        y = int(coordinates[1] / 60)
        return y * 16 + x

    def boardToScreen(self, square, square_size):
        """ Given a square on the board, returns the corresponding screen coordinates (tuple). """
        x = (square - (int((square / 16)) * 16)) * square_size
        y = int((square / 16)) * square_size
        return x, y

    def boardToChess(self, square):
        """ Given a square on the boarwd, returns the corresponding chess notation. """
        chess_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        x = chess_letters[square % 16]
        y = int((square / 16)) + 1
        return '%s%d' % (x, y)

    def checkPromotionPic(self, move, player):
        """ If move is promotion, loads the new piece's picture. """
        if move.getSpecialMove() == PROMOTION:
            new_piece = self.board.getPiece(move.getTargetSquare())
            if player.getColor() == WHITE:
                new_piece.loadImage(pygame.image.load('graphics/white_queen.png'))
            else:
                new_piece.loadImage(pygame.image.load('graphics/black_queen.png'))

    def gameLoop(self):
        """ Runs the game. """
        pygame.init()
        
        square_size = 60
        window_size = 480
        chosen_piece = None
        mouse_clicked = False
        game_over = False
        turn = white_player

        screen = pygame.display.set_mode((window_size, window_size), 0, 32)
        pygame.display.set_caption('Sten\'s chess engine')
        font = pygame.font.SysFont('comicsansms', 70)
        
        # Load white pieces. 
        white_pawn1.loadImage(pygame.image.load('graphics/white_pawn.png'))
        white_pawn2.loadImage(pygame.image.load('graphics/white_pawn.png'))
        white_pawn3.loadImage(pygame.image.load('graphics/white_pawn.png'))
        white_pawn4.loadImage(pygame.image.load('graphics/white_pawn.png'))
        white_pawn5.loadImage(pygame.image.load('graphics/white_pawn.png'))
        white_pawn6.loadImage(pygame.image.load('graphics/white_pawn.png'))
        white_pawn7.loadImage(pygame.image.load('graphics/white_pawn.png'))
        white_pawn8.loadImage(pygame.image.load('graphics/white_pawn.png'))
        white_knight1.loadImage(pygame.image.load('graphics/white_knight.png'))
        white_knight2.loadImage(pygame.image.load('graphics/white_knight.png'))
        white_bishop1.loadImage(pygame.image.load('graphics/white_bishop.png'))
        white_bishop2.loadImage(pygame.image.load('graphics/white_bishop.png'))
        white_rook1.loadImage(pygame.image.load('graphics/white_rook.png'))
        white_rook2.loadImage(pygame.image.load('graphics/white_rook.png'))
        white_queen.loadImage(pygame.image.load('graphics/white_queen.png'))
        white_king.loadImage(pygame.image.load('graphics/white_king.png'))
        
        # Load black pieces.
        black_pawn1.loadImage(pygame.image.load('graphics/black_pawn.png'))
        black_pawn2.loadImage(pygame.image.load('graphics/black_pawn.png'))
        black_pawn3.loadImage(pygame.image.load('graphics/black_pawn.png'))
        black_pawn4.loadImage(pygame.image.load('graphics/black_pawn.png'))
        black_pawn5.loadImage(pygame.image.load('graphics/black_pawn.png'))
        black_pawn6.loadImage(pygame.image.load('graphics/black_pawn.png'))
        black_pawn7.loadImage(pygame.image.load('graphics/black_pawn.png'))
        black_pawn8.loadImage(pygame.image.load('graphics/black_pawn.png'))
        black_knight1.loadImage(pygame.image.load('graphics/black_knight.png'))
        black_knight2.loadImage(pygame.image.load('graphics/black_knight.png'))
        black_bishop1.loadImage(pygame.image.load('graphics/black_bishop.png'))
        black_bishop2.loadImage(pygame.image.load('graphics/black_bishop.png'))
        black_rook1.loadImage(pygame.image.load('graphics/black_rook.png'))
        black_rook2.loadImage(pygame.image.load('graphics/black_rook.png'))
        black_queen.loadImage(pygame.image.load('graphics/black_queen.png'))
        black_king.loadImage(pygame.image.load('graphics/black_king.png'))

        # Load empty squares.
        blank_squares = pygame.image.load('graphics/white.png'), pygame.image.load('graphics/black.png')

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == MOUSEBUTTONDOWN:
                    pos = self.screenToBoard(event.pos)
                    mouse_clicked = True

            
            if turn.getType() == HUMAN and mouse_clicked and not game_over:
                if self.board.getPiece(pos) and self.board.getPiece(pos).getColor() == turn.getColor():
                    chosen_piece = self.board.getPiece(pos)

                elif chosen_piece:
                    origin_square = chosen_piece.getPosition()
                    target_square = pos
                    move = self.board.createMoveObject(origin_square, target_square, turn)
                    if self.rules.isPseudoLegal(move, self.board, turn):
                        if self.rules.isLegal(move, self.board, turn):
                            if move.getSpecialMove() == SHORT_CASTLE:
                                print('white: 0-0')
                            elif move.getSpecialMove() == LONG_CASTLE:
                                print('white: 0-0-0')
                            elif move.getSpecialMove() == PROMOTION:
                                print('white: ' + self.boardToChess(move.getOriginSquare()) + '-' + self.boardToChess(move.getTargetSquare()) + '(Q)')
                            else:
                                print('white: ' + self.boardToChess(move.getOriginSquare()) + '-' + self.boardToChess(move.getTargetSquare()))
                            self.board.makeMove(move, turn)
                            self.checkPromotionPic(move, turn)  # Load a new picture if a piece was promoted.                           
                            turn = self.board.getOtherPlayer(turn)
                    chosen_piece = None

                mouse_clicked = False 

            elif turn.getType() == COMPUTER and not game_over:
                move = self.engine.iterativeDeepening(self.board, self.rules, turn)[0]
                if move.getSpecialMove() == SHORT_CASTLE:
                    print('black: 0-0')
                elif move.getSpecialMove() == LONG_CASTLE:
                    print('black: 0-0-0')
                elif move.getSpecialMove() == PROMOTION:
                    print('black: ' + self.boardToChess(move.getOriginSquare()) + '-' + self.boardToChess(move.getTargetSquare()) + '(Q)')
                else:
                    print('black: ' + self.boardToChess(move.getOriginSquare()) + '-' + self.boardToChess(move.getTargetSquare()))
                self.board.makeMove(move, turn)
                self.checkPromotionPic(move, turn)  # Load a new picture if a piece was promoted.
                turn = self.board.getOtherPlayer(turn)

            # Set up the blank board.
            for column in range(8):
                square_color = column % 2
                for row in range(8):
                    position = square_size * row, square_size * column, 60, 60
                    screen.blit(blank_squares[square_color], position)
                    square_color = (square_color + 1) % 2

            # Put all the pieces on the board.
            for color in WHITE, BLACK:
                if color == WHITE:
                    player = white_player
                else:
                    player = black_player

                for piece_type in player.getPieceDict():
                    for piece in player.getPieceDict()[piece_type]:
                        pos = piece.getPosition()
                        x, y = self.boardToScreen(pos, square_size)
                        piece_rect = x, y, square_size, square_size
                        screen.blit(piece.getImage(), piece_rect)

            # Highlight all squares where the selected piece can move.
            if chosen_piece:
                valid_moves = self.board.generatePieceMoves(self.rules, chosen_piece, turn)
                x, y = self.boardToScreen(chosen_piece.getPosition(), square_size)
                origin_rect = x, y, square_size, square_size
                screen.lock()
                pygame.draw.rect(screen, (255, 255, 0), origin_rect, 2)
                screen.unlock()
                for move in valid_moves:
                    x, y = self.boardToScreen(move.getTargetSquare(), square_size)
                    target_rect = x, y, square_size, square_size
                    screen.lock()
                    pygame.draw.rect(screen, (255, 255, 0), target_rect, 2)
                    screen.unlock()

            if self.rules.isCheckMate(self.board, turn):
                # pygame.display.set_caption('Checkmate!')
                text = font.render('Checkmate!', True, (255, 215, 0))
                text_rect = text.get_rect()
                text_rect.centerx = screen.get_rect().centerx
                text_rect.centery = screen.get_rect().centery
                screen.blit(text, text_rect)
                game_over = True

            elif self.rules.isStaleMate(self.board, turn):
                # pygame.display.set_caption('Stalemate!')
                text = font.render('Stalemate!', True, (255, 215, 0))
                text_rect = text.get_rect()
                text_rect.centerx = screen.get_rect().centerx
                text_rect.centery = screen.get_rect().centery
                screen.blit(text, text_rect)
                game_over = True

            elif self.rules.isMaterialDraw():
                # pygame.display.set_caption('Draw!')
                text = font.render('Draw!', True, (255, 215, 0))
                text_rect = text.get_rect()
                text_rect.centerx = screen.get_rect().centerx
                text_rect.centery = screen.get_rect().centery
                screen.blit(text, text_rect)
                game_over = True

            elif self.board.getMoveCount() == 50:
                # pygame.display.set_caption('Draw!')
                text = font.render('Draw!', True, (255, 215, 0))
                text_rect = text.get_rect()
                text_rect.centerx = screen.get_rect().centerx
                text_rect.centery = screen.get_rect().centery
                screen.blit(text, text_rect)
                game_over = True
                            
            pygame.display.update()
            

# Run the game. 
if __name__ == '__main__':
    game = Game()
    game.gameLoop()
