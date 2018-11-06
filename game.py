import os

def loadNewGame():
    deck = []
    builds = []
    scores = []
    piles = []
    hands = []
    table = []
    file_name = str(input("Please select file you would like to load from: "))
    if os.path.exists(file_name):
        with open(file_name, mode = 'r') as fh:
            for line in fh:
                #get round number
                if(line.find("Round") != -1):
                    roundInfo = " ".join(line.split())
                    roundInfo = roundInfo.split()
                elif(line.find("Score:") != -1):
                    scoreInfo =" ".join(line.split())
                    scoreInfo = scoreInfo.split()
                    scores.append(scoreInfo)
                elif(line.find("Hand:") != -1):
                    handInfo =" ".join(line.split())    
                    handInfo = handInfo.split()
                    hands.append(handInfo)
                elif(line.find("Pile:") != -1):
                    pileInfo = " ".join(line.split())
                    pileInfo = pileInfo.split()
                    piles.append(pileInfo)
                elif(line.find("Table:") != -1):
                    tableInfo = " ".join(line.split())
                    tableInfo = tableInfo.split()
                    table.append(tableInfo)
                elif(line.find("Build Owner:") != -1):
                    buildInfo = " ".join(line.split())
                    buildInfo = buildInfo.split(":")
                    buildInfo = buildInfo[1].split()
                    builds.append(buildInfo)
                elif(line.find("Deck: ") != -1):
                    _deck = " ".join(line.split())
                    _deck = _deck.split()
                    deck.append(_deck)
                elif(line.find("Next Player: ") != -1):
                    nextPlayer = " ".join(line.split())
                    nextPlayer = nextPlayer.split()
    else:
        print("The file you are trying to load from does not exist! Game will now exit.")
        exit(0)

    #get round number
    loadedRound = roundInfo[1]
    #get respective scores
    computerScore = scores[0][1]
    humanScore = scores[1][1]

    #get computer and human hands 
    computerHand = [x for x in hands[0] if x != "Hand:"]
    humanHand = [x for x in hands[1] if x != "Hand:"]
    #get computer and human piles 
    computerPile = [x for x in piles[0] if x != "Pile:"]
    humanPile = [x for x in piles[1] if x != "Pile:"]
    #get table cards
    tableCards = [x for x in table[0] if x != "Table:"]
    deck = [x for x in deck[0] if x != "Deck:"]
    
    #get next player
    nextPlayer = nextPlayer[2]
    return(deck, builds , computerScore, humanScore,loadedRound, computerHand, humanHand, tableCards, computerPile, humanPile, nextPlayer)


print("Welcome to Casino Game!")
print("Please select what you would like to do.")
print("1. Start new game.")
print("2. Load game from file.")

while(1):
    user_in = input("Please make a selection: ")
    if(user_in.isdigit() and user_in == "1" or user_in == "2"):
        break

selection = int(user_in)

if(selection == 1):
    os.system('python3 CasinoWhileLoop.py')
else:
    print("Trying to load game from serialization file.")
    deck, builds , computerScore, humanScore,loadedRound, computerHand, humanHand, tableCards, computerPile, humanPile, nextPlayer = loadNewGame()
    print(deck, builds , computerScore, humanScore,loadedRound, computerHand, humanHand, tableCards, computerPile, humanPile, nextPlayer)

