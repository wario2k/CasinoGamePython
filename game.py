import os
import pygame, sys
from pygame.locals import *
import random
import itertools
from CasinoVariables import * #this is just a file that defines the window for the game
from CasinoCardGraphics import *
from CasinoBoardGraphics import*
from CasinoInteractive import getCard, getTableCards, getSelectedBuildRank, buildChoicesSpots, buildFromCoordinates
from CasinoComputerPlayer import cardsValue, discardValue, getComputerMove
from CasinoLogic import suits, Card, Deck, Player, ComputerPlayer,Help, HumanPlayer, Table, multiplesCheck, Move, TakeLastCards, Save,Discard, Take, Build, rankChoices4Build
from GameState import GameState

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
    _deck, _builds , computerScore, humanScore,loadedRound, computerHand, humanHand, table_Cards, computerPile, humanPile, nextPlayer = loadNewGame()
    
    tableCards = []
    for x in table_Cards:
        if x not in _builds:
            if (x.find("[") == -1):
                tableCards.append(x)
    
    build_cards = []
    for cards in _builds:
        build_cards.append(cards[0])
        
    gameNumber = int(loadedRound)
    
    handNumber = 0 #0-5 counts what turn it is to make sure the deck ending ends the game
    turnNumber = 0 #0-7 because 8 cards in each players hand when dealt 

    firstTime = True #keeps track of whether its the computer's first move or not, to display what move it made
                    
    deck = Deck()
    #load deck from serialized file
    deck.loadDeck(_deck)
    table = Table()
    #load table from serialized file
    table.loadTable(tableCards)
    print("table = " , table.get_available())
    h_turn = False
    c_turn = True
    if(nextPlayer == "Human"):
        h_turn = True
        c_turn = False
    dealer = not h_turn
    pygame.init()
    pygame.display.set_caption('Loaded Casino Game')
    
    gameState = GameState()
    gameState.clear()
    gameState.loaded = True
    #init human and computer players
    player1 = HumanPlayer(dealer, "Human")
    player2 = ComputerPlayer(not dealer)
    #load human and computer scores 
    player1.totalPoints = int(humanScore)
    player2.totalPoints = int(computerScore)
    #load hand and piles for human and computer
    player1.loadHand(humanHand)
    player1.loadPile(humanPile)
    print("Human HAND = " , player1.printHand())
    player2.loadHand(computerHand)
    print("CPU HAND = " , player2.printHand())
    player2.loadPile(computerPile)
    turnNumber = 7 - (len(player1.hand) + len(player2.hand)-1)
    deck_size = deck.count()
    if(deck_size == 40):
        handNumber = 0
    elif(deck_size == 32):
        handNumber = 1
    elif(deck_size == 24):
        handNumber = 2
    elif(deck_size == 16):
        handNumber = 3
    elif(deck_size == 8):
        handNumber = 4    
    else:
        handNumber = 5
   
    #keeps track of what move the computer is currently working on
    computerMoveType = None
    computerMove = None
    tup = None

    buildRank = 0 #what build we're currently talking about

    illegalMove = False #once the player presses enter, was that an illegal move or not?

    #keeps track of whether the last move they made was taking or not, to see who picks up all of the last cards
    p1Last = 0
    p2Last = 0
    
    while True: # main game loop    
        #-- Managing all of the waiting states (give the while loop an opportunity to go all the way through and refresh the cards) --#        
        if gameState.waitGM:
            gameState.clear()
            gameState.gettingMove = True
            
        elif gameState.waitP:
            gameState.clear()
            gameState.prep = True
            
        elif gameState.waitGO:
            pygame.time.wait(4000) #give the player time to see the results of "last"
            gameState.clear()
            gameState.gameOver = True
            
        elif gameState.waitCM:
            if turnNumber == 0:
                pygame.time.wait(3000)
                #if handNumber == 0: it would be nice to put something here saying "its a new game! you're the dealer!"
            gameState.clear()
            gameState.computerMove = True
            
        elif gameState.displayCM:
            gameState.clear()
            pygame.time.wait(1000) #give the player time to see the computer's selections
            print("TURN NUMBER = " ,turnNumber)
            print("Hand NUMBER = " ,handNumber)
            if turnNumber == 7:
                gameState.waitP = True
                turnNumber = 0
                if handNumber == 5:
                    gameState.clear()
                    gameState.last = True
                else:
                    handNumber += 1
            else:
                turnNumber += 1
                gameState.waitGM = True
    
        elif gameState.waitCM2:
            gameState.clear()
            gameState.displayCM = True

        elif gameState.waitRO:
            pygame.time.wait(3000)
            gameState.clear()
            gameState.roundOver = True


        #-- the prep state: dealing cards to the two players and possibly the table --#
        if gameState.loaded:

            dealToTableUI(table.allCards)
            print("Computer hand = ", player2.printHand())
            print("Compute pile = ",player2.printPile())
            print("Human hand    = ", player1.printHand())
            print("Human pile = ",player1.printPile())
            populateHandsUI(player1, player2)
            print("Current deck = " , deck.getDeck())
            buildChoicesDict = updatedBuildChoicesDict(player1)

            #changing the state based on who is the dealer
            gameState.clear()
            if dealer:
                gameState.waitCM = True
            else:
                gameState.waitGM = True
        


        #-- Rendering screen--#
        w.fill(GREEN)
        buildScore(player1, player2)
        buildInstructions()
        
        if firstTime == False:
            buildComputerMove(tup, computerMoveType)
        
        if gameState.gettingMove:
            if moveType != None:
                buildMoveType(moveType)
            if illegalMove != False:
                buildIllegalMove(illegalMove)

        if moveType == "Build":
            if buildRank > 0:
                selectBuildChoice(buildRank, buildChoicesDict)
            buildBuildChoices(player1, buildChoicesDict)

        if handNumber == 5:
            buildLast()

        if gameState.last:
            if p1Last > p2Last: #I tried to do this by saying lastPlayer = player1 or 2, but the score didn't get added
                selectLastCardsUI(player1)
                TakeLastCards(table, None, player1, player2).execute()
            else:
                selectLastCardsUI(player2)
                TakeLastCards(table, None, player2, player1).execute()

            gameState.clear()
            gameState.waitGO = True

        if gameState.newGame:
            pygame.time.wait(4000) #gives them time to see the score of the last round

            #reset all of the variables and stuff
            gameNumber += 1
            handNumber = 0
            turnNumber = 0

            firstTime = True
                            
            deck = Deck()
            deck.shuffle()
            table = Table()

            moveType = None

            computerMoveType = None
            computerMove = None
            tup = None

            buildRank = 0

            illegalMove = False

            p1Last = 0
            p2Last = 0

            for spot in cardSpots:
                spot.removeCard()
                

            
            #clearing the hands, piles, etc.
            player1.clearEverything()
            player2.clearEverything()

            #switching who is dealer
            oneWasDealer = player1.dealer
            
            if oneWasDealer:
                player1.dealer = False
                player2.dealer = True
            else:
                player1.dealer = True
                player2.dealer = False

            gameState.clear()
            gameState.prep = True


        if gameState.roundOver:
            buildRoundScore(player1, player2)
            

        if gameState.gameOver:
            player1.totalPoints += player1.calculatePoints()
            player2.totalPoints += player2.calculatePoints()
            buildGameScore(player1, player2)

            gameState.clear()
            if player1.totalPoints < 21 and player2.totalPoints < 21:
                gameState.newGame = True
            else:
                for spot in cardSpots:
                    spot.removeCard()
                gameState.waitRO = True

            
        else:
            buildNametags()
            paintAllCards()


        if gameState.displayCM: #here is when we actually execute the move
            if computerMoveType == "Discard":
                computerMove = Discard(table, tup[0], player2, player1)
                discardUI(tup[0])
            elif computerMoveType == "Take":
                computerMove = Take(table, tup[0], player2, player1, tup[1], tup[2])
                takeFromTableUI(tup[0], tup[1]) #hand card, table card list
                if tup[2] > 0:
                    takeBuildUI(tup[2])
                    for i in range(4): #reset this build spot to have nothing in it.
                        if buildRankDict[i] == tup[2]:
                            buildRankDict[i] = 0
                
                if handNumber == 5:
                    p2Last = turnNumber

            else:
                computerMove = Build(table, tup[0], player2, player1, tup[1], tup[2])
                if tup[2] not in buildRankDict.values(): #create the build in the dictionary if its new
                    for i in range(4): 
                        if buildRankDict[i] == 0:
                            buildRankDict[i] = tup[2]
                            break
                    addToBuildUI(tup[0], tup[1], tup[2])
                    buildRank = 0

                if handNumber == 5:
                    p2Last = turnNumber

            computerMove.execute()
            for spot in cardSpots:
                spot.unselect()

        if  gameState.computerMove:
                computerMoveType, tup = getComputerMove(player2, player1, table)
                toSelect = [tup[0]]+tup[1]
                if tup[2] > 0 and tup[2] in table.builds:
                    toSelect += table.builds[tup[2]]
                for spot in cardSpots:
                    if spot.card in toSelect:
                        spot.select()
                    if spot.card == tup[0]:
                        spot.side = "Front"
                    
                firstTime = False
                
                gameState.clear()
                gameState.waitCM2 = True



    #----------- going through the mouse clicks and key presses -------------#    
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()



            if gameState.gettingMove:
                if (event.type == KEYDOWN and event.key == K_t):
                    moveType = "Discard"
                    illegalMove = False
                elif (event.type == KEYDOWN and event.key == K_c):
                    moveType = "Take"
                    illegalMove = False
                elif (event.type == KEYDOWN and event.key == K_b):
                    moveType = "Build"
                    illegalMove = False
                    #press down s to save game
                elif(event.type == KEYDOWN and event.key == K_s):
                    moveType ="Save"
                    illegalMove = False
                #   get help for human
                elif(event.type == KEYDOWN and event.key == K_h):
                    moveType = "Help"
                    illegalMove = False



                elif (event.type == KEYUP and (event.key == K_KP_ENTER or event.key == K_RETURN)):                
                    cardPlayed = getCard()
                    if cardPlayed == None:
                        illegalMove = "noHandCard"

                    else:
                        if moveType == "Discard":
                            #need to add check to see if can caputre anything on table
                            move = Discard(table, cardPlayed, player1, player2)
                        elif moveType =="Save":
                            #currentTable, human, computer, currentDeck, roundNumber
                            move = Save(table,player1,player2,deck,gameNumber+1)
                        elif moveType =="Help":
                            move = Help(player1, player2, table) #human player , comp , table
                    
                        elif moveType == "Take":
                            tableCardList = getTableCards()
                            buildTaken = getSelectedBuildRank()          

                            if tableCardList == [] and buildTaken == 0: #if they didn't select any cards to take
                                illegalMove = "noTableCards"
                            else:
                                move = Take(table, cardPlayed, player1, player2, tableCardList, buildTaken)
                                
                                if handNumber == 5:
                                    p1Last = turnNumber

                        elif moveType == "Build":
                            tableCardList = getTableCards()
    ##
    ##                        if tableCardList == []: #if they didn't select any cards to take
    ##                            illegalMove = "noTableCards"
                            if True:
                                if buildRank == 0:
                                    illegalMove = "noBuildRank"
                                else:
                                    move = Build(table, cardPlayed, player1, player2, tableCardList, buildRank)

                                    if handNumber == 5:
                                        humanPlayerLast = turnNumber                    
                            
                        if moveType != None and illegalMove == False:
                            if move.legal():
                                if moveType == "Discard":
                                    discardUI(cardPlayed)
                                elif moveType == "Take":
                                    takeFromTableUI(cardPlayed, tableCardList)
                                    if buildTaken > 0:
                                        takeBuildUI(buildTaken)
                                        for i in range(4): #reset this build spot to have nothing in it.
                                            if buildRankDict[i] == buildTaken:
                                                buildRankDict[i] = 0
                                elif moveType == "Build":
                                    if buildRank not in buildRankDict.values(): #create the build in the dictionary if its new
                                        for i in range(4): 
                                            if buildRankDict[i] == 0:
                                                buildRankDict[i] = buildRank
                                                break
                                    addToBuildUI(cardPlayed, tableCardList, buildRank)
                                    buildRank = 0
                                    buildChoicesDict = updatedBuildChoicesDict(player1)

                                move.execute()

                                gameState.clear()

                                if turnNumber == 7:
                                    gameState.waitP = True
                                    turnNumber = 0
                                    if handNumber == 5:
                                        gameState.clear()
                                        gameState.last = True
                                    else:
                                        handNumber += 1
                                else:
                                    turnNumber += 1
                                    gameState.waitCM = True
                                
                            else:
                                illegalMove = "badMath"
                                
                        if moveType == None:
                            illegalMove = "noMoveType"
                    for spot in cardSpots:
                        spot.unselect()
                    moveType = None
                    buildChoicesDict = updatedBuildChoicesDict(player1)


                            
                
                if event.type == MOUSEBUTTONUP:
                    mousex, mousey = event.pos
                    mouseClicked = True
                    spot = spotFromCoordinates(mousex, mousey)
                    if spot != None:
                        if spot.card != None:
                                illegalMove = False
                                if spot.selected == True:
                                    spot.unselect()
                                else:
                                    spot.select()
                    else:
                        buildChoiceSpot = buildFromCoordinates(mousex, mousey)
                        if buildChoiceSpot != None:
                            if buildChoiceSpot in buildChoicesDict.keys():
                                if buildChoicesDict[buildChoiceSpot] != None:
                                    buildRank = buildChoicesDict[buildChoiceSpot]
                            
        pygame.display.update()
