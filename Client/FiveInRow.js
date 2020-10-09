var canvas = document.getElementById("FiveInRow");
var context = canvas.getContext("2d");
var indicator = document.getElementById("TurnIdicator");

var board = new Array(15);
for(var i = 0; i < board.length; i++){
	//Make the board array 15*15
	board[i] = new Array(15);
}
for(var x = 0; x < 15; x++){
	for(var y = 0; y < 15; y++){
		//Draw the boxes for the board
		context.beginPath();
		context.strokeStyle = "black"
		context.rect(canvas.width/15 * x, canvas.width/15 * y, canvas.width/15, canvas.width/15);
		context.stroke();
	}
}
//Save the box drawings, so it can be reapplied in one step
var boardBackground = context.getImageData(0, 0, canvas.width, canvas.height);
var PlayerColors = ["#000000", "#ffffff"]

function drawBoard(){
	context.putImageData(boardBackground, 0, 0);
	for(var x = 0; x < 15; x++){
		for(var y = 0; y < 15; y++){
			if(board[x][y] != undefined){
				context.beginPath();
				context.arc(canvas.width/15*x + canvas.width/30, canvas.width/15*y + canvas.width/30, canvas.width/38 - 2, 0, 2 * Math.PI);
				context.fillStyle = PlayerColors[board[x][y]];
				context.stroke();
				context.fill();
			}
		}
	}
}

function DeclareWinner(ID){
	var div = document.createElement("div");
	document.body.appendChild(div);
	div.outerHTML = '<div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 80%; height: 80%; background: white; border: 1px solid black; display: flex; justify-content: center; align-items: center; font-size: 2rem"><div style="position: absolute; top: 100%; left: 50%; transform: translate(-50%, -50%); background: white; border: 1px solid black; padding: 0.5rem 2rem; border-radius: 999999px; cursor: pointer" onclick="(function(event){document.body.removeChild(event.target.parentElement)})(event);">Close</div>Player '+ID+' won the game!\r\nPlease reload to play again</div>';
}

function StartOnlinePlay(){
	var socket = new WebSocket("ws://localhost:9001/");

	var myID = -1; // Make the ID obvious when its not set
	var currentPlayer = -1; //Keep track of who's turn it is

	//What to do when the server sends us a message
	socket.onmessage = function(event){
		//When receiving a message, parse the JSON to get the data
		var incoming = JSON.parse(event.data);
		switch(incoming.STATUS){
			case "ERROR":
				//If its an error, show it to the user
				var div = document.createElement("div");
				document.body.appendChild(div)
				div.outerHTML = '<div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 80%; height: 80%; background: white; border: 1px solid black; display: flex; justify-content: center; align-items: center; font-size: 2rem"><div style="position: absolute; top: 100%; left: 50%; transform: translate(-50%, -50%); background: white; border: 1px solid black; padding: 0.5rem 2rem; border-radius: 999999px; cursor: pointer" onclick="(function(event){document.body.removeChild(event.target.parentElement)})(event);">Close</div>'+incoming.ERROR+'</div>';
				break;
			case "JOIN":
				//If it's a join action, then remember the ID the server gave you
				myID = incoming.ID;
				if(myID == 0){
					indicator.innerHTML = "Waiting for players. Click here to play against AI"
					indicator.onclick = function(event){
						console.log("SOLOPLAY");
						socket.send('{"STATUS": "SOLOPLAY"}')
						indicator.onclick = undefined;
					}
				}
				break;
			case "TURN":
				//If it's a turn action, then remember and tell the user who's turn it is now
				currentPlayer = incoming.PLAYER
				if(incoming.PLAYER == myID){
					indicator.innerHTML = "It is your turn"
				} else {
					indicator.innerHTML = 'It is player '+incoming.PLAYER+'\'s turn'
				}
				break;
			case "PLACE":
				//If it's a place action then add it to the board and refresh the canvas to show the new piece
				board[incoming.X][incoming.Y] = incoming.ID;
				drawBoard();
				break;
			case "WINNER":
				//If it's a winner action then a winner has been decided so show the user
				DeclareWinner(incoming.ID)
				break;
		}
	}

	canvas.addEventListener("click", function(event){
		//When there is a click on the canvas get the actual screen size of the canvas
		var boundingRect = canvas.getBoundingClientRect();
		//and work out in what tile the click happened
		var clickX = Math.floor((event.clientX - boundingRect.left) / boundingRect.width * 15);
		var clickY = Math.floor((event.clientY - boundingRect.top) / boundingRect.height * 15);
		console.log(event, boundingRect, clickX, clickY);

		if(socket.readyState == 1 && currentPlayer == myID)
			//if the socket is still active and it is the user's turn then inform the server where the click happened to place a new piece there
			console.log('{"STATUS": "PLACE", "X": "'+clickX+'", "Y": "'+clickY+'", "ID": "'+myID+'"}');
			socket.send('{"STATUS": "PLACE", "X": "'+clickX+'", "Y": "'+clickY+'", "ID": "'+myID+'"}');
	})
}

function StartLocalPlay(){
	var currentPlayer = 1;

	board[7][7] = 0;
	drawBoard();

	indicator.innerHTML = 'It is player '+currentPlayer+'\'s turn'

	canvas.addEventListener("click", function(event){
		//When there is a click on the canvas get the actual screen size of the canvas
		var boundingRect = canvas.getBoundingClientRect();
		//and work out in what tile the click happened
		var clickX = Math.floor((event.clientX - boundingRect.left) / boundingRect.width * 15);
		var clickY = Math.floor((event.clientY - boundingRect.top) / boundingRect.height * 15);

		if(board[clickX][clickY] == undefined){
			board[clickX][clickY] = currentPlayer;
			drawBoard();

			//check for winner
			//Horizontal
			var score = 1; //We know the newly added tile counts in the score, so no need to check for it
			for(var i = 1; i < 5; i++){
				if(clickX + i > 14 || board[clickX + i][clickY] != currentPlayer)
					break;
				else
					score++;
			}
			for(var i = -1; i > -5; i--){
				if(clickX + i < 0 || board[clickX + i][clickY] != currentPlayer)
					break;
				else {
					score++;
				}
			}
			if(score >= 5)//we have a winner!
				DeclareWinner(currentPlayer);

			//Vertical
			score = 1; //We know the newly added tile counts in the score, so no need to check for it
			for(var i = 1; i < 5; i++){
				if(clickY + i > 14 || board[clickX][clickY + i] != currentPlayer)
					break;
				else
					score++;
			}
			for(var i = -1; i > -5; i--){
				if(clickY + i < 0 || board[clickX][clickY + i] != currentPlayer)
					break;
				else {
					score++;
				}
			}
			if(score >= 5)//we have a winner!
				DeclareWinner(currentPlayer);

			// bottom right diagonal
			score = 1; //We know the newly added tile counts in the score, so no need to check for it
			for(var i = 1; i < 5; i++){
				if(clickX + i > 14 || clickY + i > 14 || board[clickX + i][clickY + i] != currentPlayer)
					break;
				else
					score++;
			}
			for(var i = -1; i > -5; i--){
				if(clickX + i < 0 || clickY + i < 0 || board[clickX + i][clickY + i] != currentPlayer)
					break;
				else {
					score++;
				}
			}
			if(score >= 5)//we have a winner!
				DeclareWinner(currentPlayer);

			//top right diagonal
			score = 1; //We know the newly added tile counts in the score, so no need to check for it
			for(var i = 1; i < 5; i++){
				if(clickX + i > 14 || clickY - i < 0 || board[clickX + i][clickY - i] != currentPlayer)
					break;
				else
					score++;
			}
			for(var i = -1; i > -5; i--){
				if(clickX + i < 0 || clickY - i > 14 || board[clickX + i][clickY - i] != currentPlayer)
					break;
				else {
					score++;
				}
			}
			if(score >= 5)//we have a winner!
				DeclareWinner(currentPlayer);


			currentPlayer = (currentPlayer + 1) % 2; //Go to next player turn and roll back around to the first player when applicable
			indicator.innerHTML = 'It is player '+currentPlayer+'\'s turn'
		}
	})
}

//Ask the player what type of game they want to play
var div = document.createElement("div");
document.body.appendChild(div)
div.outerHTML = '<div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 80%; height: 80%; background: white; border: 1px solid black; display: flex; justify-content: center; align-items: center; font-size: 2rem"><div style="position: absolute; top: 100%; transform: translateY(-50%); display: flex;"><div style="background: white; border: 1px solid black; padding: 0.5rem 2rem; margin: 1rem; border-radius: 999999px; cursor: pointer" onclick="(function(event){document.body.removeChild(event.target.parentElement.parentElement); StartOnlinePlay();})(event);">Online</div><div style="background: white; border: 1px solid black; padding: 0.5rem 2rem; margin: 1rem;  border-radius: 999999px; cursor: pointer" onclick="(function(event){document.body.removeChild(event.target.parentElement.parentElement); StartLocalPlay();})(event);">Local</div></div>Would you like to play online or locally?</div>';
