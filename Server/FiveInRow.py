#Server constants go here
url = 'localhost'
port = 9001
try:
	from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
	import json
	from random import randrange
	import traceback
except ImportError:
	print("Simple Web Socket can not be imported")
	print("Run 'python -m pip install -r requirements.txt' from inside the Server folder")
	exit()

def AIPlay(board):
	highest = 0;
	locX = -1;
	locY = -1;
	potentials = [None] * 15
	for i in range(15):
		potentials[i] = [None] * 15

	#Make the list of locations to check
	for x in range(15):
		for y in range(15):
			#if there is already a token then its not a valid choice
			if board[x][y] is not None:
				continue
			#Chekc if there is a token placed close, then its worth investigating more
			if x > 0:
				if board[x-1][y] is not None:
					potentials[x][y] = True
					continue
				if y > 0:
					if board[x][y-1] is not None:
						potentials[x][y] = True
						continue
					if board[x-1][y-1] is not None:
						potentials[x][y] = True;
						continue
				if y < 14:
					if board[x][y+1] is not None:
						potentials[x][y] = True
						continue
					if board[x-1][y+1] is not None:
						potentials[x][y] = True
						continue
			if x < 14:
				if board[x+1][y] is not None:
					potentials[x][y] = True
					continue
				if y > 0:
					if board[x][y-1] is not None:
						potentials[x][y] = True
						continue
					if board[x+1][y-1] is not None:
						potentials[x][y] = True;
						continue
				if y < 14:
					if board[x][y+1] is not None:
						potentials[x][y] = True
						continue
					if board[x+1][y+1] is not None:
						potentials[x][y] = True
						continue

	#Now calculate the score for each potential location
	for x in range(15):
		for y in range(15):
			if potentials[x][y] is not None:
				#Check right
				score = 0
				count = 0
				for i in range(1,min(5, 14-x)):
					if board[x + i][y] == 0:
						count+=1
					else:
						break
				#We know how long the chain we would adding be. Give a score of count*count for that
				score += count*count
				count = 0
				for i in range(1,min(5, 14-x)):
					if board[x + i][y] == 1:
						count+=1
					else:
						break
				#We are now aware of long the chain of the block will be. So let's give a score of count*count for that as well
				score += count*count
				#Now do the same thing for each of the remaining seven  directions

				#Left
				count = 0
				for i in range(1,min(5, x)):
					if board[x - i][y] == 0:
						count+=1
					else:
						break
				score += count*count

				count = 0
				for i in range(1,min(5, x)):
					if board[x - i][y] == 1:
						count+=1
					else:
						break
				score += count*count

				#Down
				count = 0
				for i in range(1,min(5, 14-y)):
					if board[x][y + i] == 0:
						count+=1
					else:
						break
				score += count*count

				count = 0
				for i in range(1,min(5, 14-y)):
					if board[x][y + i] == 1:
						count+=1
					else:
						break
				score += count*count

				#Up
				count = 0
				for i in range(1,min(5, y)):
					if board[x][y - i] == 0:
						count+=1
					else:
						break
				score += count*count

				count = 0
				for i in range(1,min(5, y)):
					if board[x][y - i] == 1:
						count+=1
					else:
						break
				score += count*count

				#down right
				count = 0
				for i in range(1,min(5, min(14-x, 14-y))):
					if board[x + i][y + i] == 0:
						count+=1
					else:
						break
				score += count*count

				count = 0
				for i in range(1,min(5, min(14-x, 14-y))):
					if board[x + i][y + i] == 1:
						count+=1
					else:
						break
				score += count*count

				#down left
				count = 0
				for i in range(1,min(5, min(x, 14-y))):
					if board[x - i][y + i] == 0:
						count+=1
					else:
						break
				score += count*count

				count = 0
				for i in range(1,min(5, min(x, 14-y))):
					if board[x - i][y + i] == 1:
						count+=1
					else:
						break
				score += count*count

				#up right
				count = 0
				for i in range(1,min(5, min(14-x, y))):
					if board[x + i][y - i] == 0:
						count+=1
					else:
						break
				score += count*count

				count = 0
				for i in range(1,min(5, min(14-x, y))):
					if board[x + i][y - i] == 1:
						count+=1
					else:
						break
				score += count*count

				#up left
				count = 0
				for i in range(1,min(5, min(x, y))):
					if board[x - i][y - i] == 0:
						count+=1
					else:
						break
				score += count*count

				count = 0
				for i in range(1,min(5, min(x, y))):
					if board[x - i][y - i] == 1:
						count+=1
					else:
						break
				score += count*count

				#Now that we have the score for that potential location, check if its better than the current highest, if so rememebr this new one instead
				if score > highest:
					highest = score
					locX = x
					locY = y

	#after the potentials have been checked return the best location
	return [locX, locY]

class FiveInRowServer:
	def __init__(self):
		self.players = []
		self.playerturn = -1
		#Make sure the playerturn is easily recognizable when not set correctly
		self.board = [None] * 15
		for i in range(15):
			#Create the board array 15*15
			self.board[i] = [None] * 15
		self.soloPlay = False;
	def addPlayer(self, player):
		if len(self.players) < 2:
			#Make sure to not go over the 2 player limit
			player.ID = len(self.players)
			self.players.append(player)
			#Tell the user that they have successfully joined the game
			player.sendMessage('{"STATUS": "JOIN", "ID": %s}' % (player.ID))
			if len(self.players) == 2:
				self.players[0].sendMessage('{"STATUS": "GAMESTART"}')
				self.playRound()
		else:
			#Tell the user why they cannot connect
			player.sendMessage('{"STATUS": "ERROR", "ERROR": "The game room has enough players already"}')
	def playRound(self):
		if self.playerturn == -1:
			#We know this is the first turn so do the initial board setup and skip first players turn since their tile is already placed
			self.placePiece(7, 7, 0)
			self.playerturn = 0
		self.playerturn = (self.playerturn + 1) % 2
		if self.soloPlay == False:
			#When the game is for two human players
			for player in self.players:
				#Inform every player whos turn it is now
				player.sendMessage('{"STATUS": "TURN", "PLAYER": "%s"}' % (self.playerturn))
		else:
			#When the user is playing against the AI
			if self.playerturn == 1:
				#AI will always be player 0, so the user can play the first turn
				AIPiece = AIPlay(self.board)
				self.placePiece(AIPiece[0], AIPiece[1], 1)
			else:
				#Tell the user its his turn
				self.players[0].sendMessage('{"STATUS": "TURN", "PLAYER": "%s"}' % (0))
	def placePiece(self, x, y, ID):
		#If it reaches this point, it should already be validated
		self.board[x][y] = ID
		#Tell the player where the piece was placed
		for player in self.players:
			player.sendMessage('{"STATUS": "PLACE", "X": "%s", "Y": "%s", "ID": "%s"}' % (x, y, ID))


		#Check if that move won the game
		if self.playerturn == -1:
			#but only if its not the first piece
			return
		highest = 1
		for i in range(1,min(5, 14-x)):
			#Check if there is a line to the right, up to the right of the board
			if self.board[x + i][y] == ID:
				highest+=1
		for i in range(1,min(5, x)):
			#Check if there is a line to the left, up to the left fo the board
			if self.board[x - i][y] == ID:
				highest+=1
		if highest >= 5:
			#the piece is part of a horizontal line long enough to win
			self.declareWinner(ID)
			return

		highest = 1
		for i in range(1,min(5, 14-y)):
			#Check if there is a line to the bottom, up to the bottom of the board
			if self.board[x][y + i] == ID:
				highest+=1
		for i in range(1,min(5, y)):
			#Check if there is a line to the top, up to the top fo the board
			if self.board[x][y - i] == ID:
				highest+=1
		if highest >= 5:
			#the piece is part of a vertical line long enough to win
			self.declareWinner(ID)
			return

		highest = 1
		for i in range(1,min(5, min(14-x, 14-y))):
			#Check if there is a line to the bottom right, up to the bottom and right of the board
			if self.board[x + i][y + i] == ID:
				highest+=1
		for i in range(1,min(5, min(x, y))):
			#Check if there is a line to the top left. up to the top and left of the board
			if self.board[x - i][y - i] == ID:
				highest+=1
		if highest >= 5:
			#the piece is part of a north west line long enough to win
			self.declareWinner(ID)
			return

		highest = 1
		for i in range(1,min(5, min(14-x, y))):
			#Check if there is a line to the top right of the board
			if self.board[x + i][y - i] == ID:
				highest+=1
		for i in range(1,min(5, min(x, 14-y))):
			#Check if there is a line to the bottom left of the board
			if self.board[x - i][y + i] == ID:
				highest+=1
		if highest >= 5:
			#the piece is part of a horizontal line long enough to win
			self.declareWinner(ID)
			return

		#no winner, so move on to the next turn
		GameServerInstance.playRound()

	def checkPiece(self, X, Y, ID, player):
		if GameServerInstance.players[ID] is player:
			#Now that we know it is actually the correct player
			if GameServerInstance.playerturn == ID:
				#we make sure that it is actually their turn and add the piece
				self.placePiece(X, Y, ID)


	def declareWinner(self, ID):
		for player in self.players:
			#Tell the players that there is a winner
			player.sendMessage('{"STATUS": "WINNER", "ID": "%s"}' % (ID))

		#Reset the game
		for player in self.players:
			player.close()
		self.players = []
		self.playerturn = -1
		self.board = [None] * 15
		for i in range(15):
			#Create the board array 15*15
			self.board[i] = [None] * 15

GameServerInstance = FiveInRowServer()

# Now that the server package is loaded we can use it
class PlayerHandler(WebSocket):
	def handleConnected(self):
		try:
			GameServerInstance.addPlayer(self)
		except Exception as e:
			print("Error: ")
			print(e)
	def handleMessage(self):
		try:
			incoming = json.loads(self.data)
			if incoming["STATUS"] == "PLACE":
				GameServerInstance.checkPiece(int(incoming["X"]), int(incoming["Y"]), int(incoming["ID"]), self)
			elif incoming["STATUS"] == "SOLOPLAY":
				GameServerInstance.soloPlay = True;
				GameServerInstance.playRound()
		except Exception as e:
			print(traceback.format_exc())

WebSocketServer = SimpleWebSocketServer(url, port, PlayerHandler)
print("Server is running at %s:%s" % (url, port))
WebSocketServer.serveforever()
