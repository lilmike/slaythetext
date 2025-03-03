import random as rd
import entities
from ansimarkup import parse, ansiprint,ansistring
import acts
from collections import Counter
import math
import save_handlery
import time
import sys
import string

turn_counter = 0
encounter_counter = 0
floor_counter = 0

gameAct = 1
actThreeFirstBossBeaten = False

game_map = acts.generate_map()
game_map_dict = acts.generate_connections(game_map)

# game_map = acts.generate_act4Map()
# game_map_dict = acts.generate_act4ConnectionDict(game_map)

seed = ""


commonCardChance = 0.63
uncommonCardChance = 0.37
rareCardChance = 0.00

generalPotionChance = 40

removeCardCost = 75

def set_seed():
    global seed
    
    
    answers = ["1","2"]
    while True:
        snap = input("Do you want to set a custom seed for your run?\n1. Yes\n2. No\n")
        if snap not in answers:
            print("You have to type either 1 or 2")            
            continue
        if snap == "1":
            seedSuggestion = input("Type your seed.\n")
            seed = seedSuggestion
            ansiprint(f"The seed is:\n{seed}")
            break
        elif snap == "2":
            seed = ''.join(rd.choices(string.ascii_uppercase + string.digits, k=20))
            ansiprint(f"The seed is:\n{seed}\n")
            break
        
def typeWriter(words):
    print(words)
    # for char in words:
    #     print(char,end='',flush=True)
    #     time.sleep(0.02)        
    # print("")
    

def count_up(turn):
    
    return turn + 1


def alternating_choices(optionsOne,optionsTwo,weightsOne = None,weightsTwo = None,k = 50):
    i = 0
    alternatedList = []
    while i < k:
        x = rd.choices(optionsOne,weightsOne)[0]
        alternatedList.append(x)
        y = rd.choices(optionsTwo,weightsTwo)[0]
        alternatedList.append(y)
        i += 1

    return alternatedList

def afterBattleScreen():
    global gameAct
    global game_map
    global game_map_dict
    global actThreeFirstBossBeaten
    
    afterBattleOptions = []
    goldGain = 0
    


    if entities.active_character[0].get_floor() == "Start":
        pass

    elif entities.active_character[0].get_floor() == "Boss":
        gameAct += 1

        if gameAct <= 3:
            entities.active_character[0].heal(math.floor(entities.active_character[0].max_health / 100 * 75))
            potentialCardWinnings = generateCardRewards(bossReward=True)
            afterBattleOptions.append("<blue>Card Reward</blue>")

            relicReward = generateRelicRewards(place="Boss Chest")
            afterBattleOptions.append("<light-red>Relic</light-red>")

            goldGain = generateGoldReward()
            afterBattleOptions.append("<yellow>Gain "+str(goldGain)+" Gold</yellow>")  
            entities.enemyEncounters = entities.fill_enemy_list()
            entities.eliteEncounters = entities.fill_elite_list()
            entities.bossEncounters = entities.fill_boss_list(gameAct)
            entities.active_character[0].set_position([0,0])
            
            if entities.active_character[0].greenKey == False:

                game_map = acts.generate_map(superElite=True)
                game_map_dict = acts.generate_connections(game_map)
        
            elif entities.active_character[0].greenKey == True:

                game_map = acts.generate_map(superElite=False)
                game_map_dict = acts.generate_connections(game_map)

        elif gameAct == 4 and actThreeFirstBossBeaten == False:
            gameAct = 3            
            actThreeFirstBossBeaten = True
            
        elif gameAct == 4 and actThreeFirstBossBeaten == True:
            
            if entities.active_character[0].allKeys == True:
                entities.active_character[0].heal(math.floor(entities.active_character[0].max_health / 100 * 75))
                gameAct += 1
                game_map = acts.generate_act4Map()
                game_map_dict = acts.generate_act4ConnectionDict(game_map)
                entities.active_character[0].set_position([0,0])            
            else:
                print("The game should be over now but I don't know how to do that.")



    elif entities.active_character[0].get_floor() == "Event":
        pass

    elif entities.active_character[0].get_floor() == "Chest":
        pass

    elif entities.active_character[0].get_floor() == "Portal":
        pass

    elif entities.active_character[0].get_floor() == "Shop$":
        pass

    elif entities.active_character[0].get_floor() == "Fires":
        pass

    else:
        
        if entities.active_character[0].get_smokebomb():
            potentialCardWinnings = generateCardRewards()
            afterBattleOptions.append("<blue>Card Reward</blue>")

            if entities.active_character[0].prayerWheel > 0 and entities.active_character[0].get_floor() == "Enemy":
                potentialCardWinnings2 = generateCardRewards()
                afterBattleOptions.append("<blue>Card Reward 2</blue>")

            if entities.active_character[0].get_floor() == "Elite":
                relicReward = generateRelicRewards(place ="Elite Fight")
                afterBattleOptions.append("<light-red>Relic</light-red>")

            if entities.active_character[0].get_floor() == "Super":
                relicReward = generateRelicRewards(place ="Super")
                afterBattleOptions.append("<light-red>Relic</light-red>")

            potentialPotion = generatePotionRewards()

            if len(potentialPotion) > 0:
                afterBattleOptions.append("<c>Potion Reward</c>")

            
            goldGain = generateGoldReward()
            afterBattleOptions.append("<yellow>Gain "+str(goldGain)+" Gold</yellow>")

    
    afterBattleOptions.append("Show Deck")
    afterBattleOptions.append("Show Relics")
    afterBattleOptions.append("Display Map")
    afterBattleOptions.append("Next Floor")
    afterBattleOptions.append("Show Seed")
    
    while True:
        print("\n")
        i = 0
        for reward in afterBattleOptions:

            ansiprint(str(i+1)+".",reward)
            i += 1
        
        try:
            snap = input("What do you want to do?\n")
            snap = int(snap)-1
            if snap not in range (len(afterBattleOptions)):
                continue
            
            if "Gold" in afterBattleOptions[snap]:
                entities.active_character[0].set_gold(goldGain)
                afterBattleOptions.pop(snap)
            
            elif "Potion" in afterBattleOptions[snap]:                
                potionCheck = pickPotion(potentialPotion)

                if potionCheck:
                    ansiprint("You can still pick up <c>"+str(potionCheck)+" Potion</c>.")
                else:
                    afterBattleOptions.pop(snap)

            elif afterBattleOptions[snap] == "<blue>Card Reward</blue>":                
                deckCheck = len(entities.active_character[0].deck)
                healthCheck = entities.active_character[0].max_health
                pickCard(potentialCardWinnings)
                if len(entities.active_character[0].deck) > deckCheck:
                    afterBattleOptions.pop(snap)
                elif healthCheck < entities.active_character[0].max_health:
                    afterBattleOptions.pop(snap)
            
            elif afterBattleOptions[snap] == "<blue>Card Reward 2</blue>":                
                deckCheck = len(entities.active_character[0].deck)
                healthCheck = entities.active_character[0].max_health
                pickCard(potentialCardWinnings2)
                if len(entities.active_character[0].deck) > deckCheck:
                    afterBattleOptions.pop(snap)
                elif healthCheck > entities.active_character[0].max_health:
                    afterBattleOptions.pop(snap)
            
            elif afterBattleOptions[snap] == "<light-red>Relic</light-red>":
                relicCheck = len(entities.active_character[0].relics)
                pickRelic(relicReward)
                if relicCheck < len(entities.active_character[0].relics):
                    afterBattleOptions.pop(snap)         

            elif "Display Map" in afterBattleOptions[snap]:
                acts.show_map(game_map,game_map_dict)
            
            elif "Show Deck" in afterBattleOptions[snap]:
                entities.active_character[0].showDeck()
            
            elif "Show Relics" in afterBattleOptions[snap]:
                entities.active_character[0].showRelics()
            
            elif "Next Floor" in afterBattleOptions[snap]:
                acts.show_map(game_map,game_map_dict)
                acts.move_after_combat(game_map,game_map_dict)
                break
            
            elif "Show Seed" in afterBattleOptions[snap]:
                print(f"\nThis is the current seed:{seed}\n")
                

        except Exception as e:
            entities.active_character[0].explainer_function(snap)
            ansiprint("You have to type a number!",e)
    
def generateGoldReward(monster: str = None):
    goldenIdol = False
    for relic in entities.active_character[0].relics:
        if relic.get("Name") == "Golden Idol":
            goldenIdol = True

    if monster:
        if monster == "Creep":
            goldGain = rd.randint(10,20)
        elif monster == "Elite":
            goldGain = rd.randint(25,35)
        elif monster == "Boss":
            goldGain = rd.randint(95,105)
    else:
        if entities.active_character[0].get_floor() == "Creep":
            goldGain = rd.randint(10,20)
        elif entities.active_character[0].get_floor() == "Elite":
            goldGain = rd.randint(25,35)
        elif entities.active_character[0].get_floor() == "Super":
            goldGain = rd.randint(25,35)
        elif entities.active_character[0].get_floor() == "Boss":
            goldGain = rd.randint(95,105)
        else:
            goldGain = 0

    if goldenIdol:
        goldGain += math.floor(goldGain/4)

    return goldGain

def afterEventBattleRewardScreen(gold: int = None,potion:dict = None,cards: list = None,relic: dict =None,secondRelic:dict=None,multipleCardRewards:list= False):
    eventBattleRewards = []
    potionName = "SUPER POTION 1 MILLION"
    
    if entities.active_character[0].get_smokebomb():
        if potion:
            for drink in potion:
                eventBattleRewards.append("Receive <c>"+drink["Name"]+"</c>.")
            potionName = drink.get("Name")
        
        if gold:      
            eventBattleRewards.append("Receive <yellow>"+str(gold)+" Gold</yellow>.")
        
        if cards:
            eventBattleRewards.append("Check <blue>Card Reward</blue>.")

        if relic:
            eventBattleRewards.append("Receive <light-red>"+relic.get("Name")+"</light-red>.")
            
        if secondRelic:
            eventBattleRewards.append("Receive <light-red>"+secondRelic.get("Name")+"</light-red>.")

        if multipleCardRewards:
            i = 0
            while i < len(multipleCardRewards):
                eventBattleRewards.append("Check <blue>Card Reward</blue> "+str(i+1)+".")
            i+=1
    
    eventBattleRewards.append("[Leave] All Rewards that weren't claimed will be gone!")
    
    while True:
        i = 0
        for reward in eventBattleRewards:
            ansiprint(str(i+1)+".",reward)
            i += 1
        try:
            snap = input("What do you want to do?\n")
            snap = int(snap)-1
            if snap not in range(len(eventBattleRewards)):
                print("You have to type one of the corresponding numbers.")
                continue
            
            if snap == len(eventBattleRewards)-1:
                break
            
            elif eventBattleRewards[snap] == "Receive <yellow>"+str(gold)+" Gold</yellow>.":
                entities.active_character[0].set_gold(gold)
                eventBattleRewards.pop(snap)
            
            elif potionName in eventBattleRewards[snap]:
                
                entities.active_character[0].add_potion(drink)
                eventBattleRewards.pop(snap)
            
            elif eventBattleRewards[snap] == "Check <blue>Card Reward</blue>.":                
                deckCheck = len(entities.active_character[0].deck)
                healthCheck = entities.active_character[0].max_health
                pickCard(cards)
                if len(entities.active_character[0].deck) > deckCheck:
                    eventBattleRewards.pop(snap)

                elif healthCheck > entities.active_character[0].max_health:
                    eventBattleRewards.pop(snap)

            elif eventBattleRewards[snap] == "Check <blue>Card Reward</blue> 1.":                
                deckCheck = len(entities.active_character[0].deck)
                healthCheck = entities.active_character[0].max_health
                pickCard(multipleCardRewards[0])
                if len(entities.active_character[0].deck) > deckCheck:
                    eventBattleRewards.pop(snap)

                elif healthCheck > entities.active_character[0].max_health:
                    eventBattleRewards.pop(snap)

            elif eventBattleRewards[snap] == "Check <blue>Card Reward</blue> 2.":                
                deckCheck = len(entities.active_character[0].deck)
                healthCheck = entities.active_character[0].max_health
                pickCard(multipleCardRewards[1])
                if len(entities.active_character[0].deck) > deckCheck:
                    eventBattleRewards.pop(snap)

                elif healthCheck > entities.active_character[0].max_health:
                    eventBattleRewards.pop(snap)

            elif eventBattleRewards[snap] == "Check <blue>Card Reward</blue> 3.":                
                deckCheck = len(entities.active_character[0].deck)
                healthCheck = entities.active_character[0].max_health
                pickCard(multipleCardRewards[2])
                if len(entities.active_character[0].deck) > deckCheck:
                    eventBattleRewards.pop(snap)

                elif healthCheck > entities.active_character[0].max_health:
                    eventBattleRewards.pop(snap)
            
            elif eventBattleRewards[snap] == "Receive <light-red>"+relic.get("Name")+"</light-red>.":
                entities.active_character[0].add_relic(relic)
                eventBattleRewards.pop(snap)

            elif eventBattleRewards[snap] == "Receive <light-red>"+secondRelic.get("Name")+"</light-red>.":
                entities.active_character[0].add_relic(secondRelic)
                eventBattleRewards.pop(snap)
        
        except ValueError:
            entities.active_character[0].explainer_function(snap)
            print("You have to type a number.")
        except Exception as e:
            print(e)
            

def generateRelicRewards(place="Elite Fight",specificType = None):
    
    relic_commons = {k:v for k,v in entities.relics.items() if v.get("Rarity") == "Common" and (v.get("Owner") == entities.active_character[0].name or v.get("Owner") == "The Spire")}
    relic_uncommons = {k:v for k,v in entities.relics.items() if v.get("Rarity") == "Uncommon" and (v.get("Owner") == entities.active_character[0].name or v.get("Owner") == "The Spire")}
    relic_rares = {k:v for k,v in entities.relics.items() if v.get("Rarity") == "Rare" and (v.get("Owner") == entities.active_character[0].name or v.get("Owner") == "The Spire")}
    relic_boss = {k:v for k,v in entities.relics.items() if v.get("Rarity") == "Boss" and (v.get("Owner") == entities.active_character[0].name or v.get("Owner") == "The Spire")}
    relic_shop = {k:v for k,v in entities.relics.items() if v.get("Rarity") == "Shop"  and (v.get("Owner") == entities.active_character[0].name or v.get("Owner") == "The Spire")}

    places =["Boss Chest","Small Chest","Medium Chest","Large Chest","Elite Fight","Shop","Else"]
    relicAmount = 1
    rewardRelics = []

    for relic in entities.active_character[0].relics:
        if relic.get("Name") == "Matryoshka":
            if place == "Small Chest" or place == "Medium Chest" or place == "Large Chest":
                matryoshkaIndex = entities.active_character[0].relics.index(relic)

                if entities.active_character[0].relics[matryoshkaIndex]["Counter"] > 0:
                    relicAmount += 1
                    entities.active_character[0].relics[matryoshkaIndex]["Counter"] -= 1
        
        elif relic.get("Name") == "Black Star":
            if place == "Elite Fight" or place == "Super":
                relicAmount += 1


    if place == "Elite Fight":
        commonRelicChance = 0.5
        uncommonRelicChance = 0.33
        rareRelicChance = 0.17 
        bossRelicChance = 0
    
    elif place == "Super":
        commonRelicChance = 0.5
        uncommonRelicChance = 0.33
        rareRelicChance = 0.17 
        bossRelicChance = 0

    elif place == "Small Chest":
        commonRelicChance = 0.75
        uncommonRelicChance = 0.25
        rareRelicChance = 0
        bossRelicChance = 0
        
    elif place == "Medium Chest":
        commonRelicChance = 0.35
        uncommonRelicChance = 0.50
        rareRelicChance = 0.15
        
        bossRelicChance = 0
        
    elif place == "Large Chest":
        commonRelicChance = 0
        uncommonRelicChance = 0.75
        rareRelicChance = 0.25
        
        bossRelicChance = 0
        
    elif place == "Boss Chest":
        commonRelicChance = 0
        uncommonRelicChance = 0
        rareRelicChance = 0
        
        bossRelicChance = 1
        relicAmount = 3

    elif place == "Shop":
        
        commonRelicChance = 0.5
        uncommonRelicChance = 0.33
        rareRelicChance = 0.17 
        bossRelicChance = 0
        
        relicAmount = 2

    elif place == "Event":
        commonRelicChance = 0.5
        uncommonRelicChance = 0.33
        rareRelicChance = 0.17 
        bossRelicChance = 0

    if specificType == "Common":
        relicList = [0]
    elif specificType == "Uncommon":
        relicList = [1]
    elif specificType == "Rare":    
        relicList = [2]
    else:
        relicList = list(nchoices_with_restrictions(weights = [commonRelicChance,uncommonRelicChance,rareRelicChance,bossRelicChance], k = relicAmount))

    if place == "Shop":
        #two regularly generated Relics will be generated and then a fixed third shopRelic is being applied.
        relicList = list(relicList)
        relicList.append(4)

    while True:
        alreadySeen = False
        noBottleCard = False
        goldShopItem = False
        
        for relic in relicList:
            
            if relic == 0:
                rewardRelics.append(rd.choices(list(relic_commons.items()))[0][1])
            elif relic == 1:
                rewardRelics.append(rd.choices(list(relic_uncommons.items()))[0][1])
            elif relic == 2:
                rewardRelics.append(rd.choices(list(relic_rares.items()))[0][1])
            elif relic == 3:
                rewardRelics.append(rd.choices(list(relic_boss.items()))[0][1])
            elif relic == 4:
                rewardRelics.append(rd.choices(list(relic_shop.items()))[0][1])

        
        for relic in rewardRelics:
            
            if relic.get("Name") in entities.relics_seen_list:
                ansiprint(relic.get("Name"),"has already been generated.")
                alreadySeen = True

            elif relic.get("Name") == "Bottled Flame":
                attackCheck = [card for card in entities.active_character[0].deck if card.get("Type") == "Attack"]
                
                if len(list(attackCheck)) == 0:
                    rewardRelics = []                    
                    noBottleCard = True

            elif relic.get("Name") == "Bottled Lightning":
                skillCheck = [card for card in entities.active_character[0].deck if card.get("Type") == "Skill"]
                if len(list(skillCheck)) == 0:
                    rewardRelics = []
                    noBottleCard = True

            elif relic.get("Name") == "Bottled Tornado":
                powerCheck = [card for card in entities.active_character[0].deck if card.get("Type") == "Power"]
                if len(list(powerCheck)) == 0:
                    rewardRelics = []
                    noBottleCard = True

            elif relic.get("Name") == "Maw Bank" and entities.active_character[0].get_floor() == "Shop$":
                goldShopItem = True
                print("Maw Bank can't spawn in the Shop")

            elif relic.get("Name") == "Old Coin" and entities.active_character[0].get_floor() == "Shop$":
                goldShopItem = True
                print("Old Coin can't spawn in the Shop")
        
        if alreadySeen or noBottleCard or goldShopItem:
            rewardRelics = []
            continue
        
        try:

            test = any(rewardRelics.count(x) > 1 for x in rewardRelics)

            if test:
                rewardRelics = []
                continue
            else:
                for relic in rewardRelics:
                    entities.relics_seen_list.append(relic.get("Name"))
                break
        except Exception as e:
            print("There is an issue in helpingfunctions Generate Relics. This is the issue-->\n",e)
       
        #print("Hi",place)
        
    if place == "Super":
        rewardRelics.append({"Name":"Green Key","Rarity":"Special","Owner":"The Spire","Type":"Relic","Info":"You need to obtain the <red>Red</red>,<green>Green</green> and <blue>Blue</blue> Key. Why? Find out yourself!"})
        
    return rewardRelics

def generateCardRewards(colorless=False,bossReward=False):
    
    global commonCardChance
    global uncommonCardChance
    global rareCardChance
    global gameAct
    
    moltenEgg = False
    toxicEgg = False
    frozenEgg = False
    nlothsGift = False
    prismaticShard = False
    cardRewardAmount = 3

    for relic in entities.active_character[0].relics:
        if relic.get("Name") == "Question Mark":
            cardRewardAmount += 1
        elif relic.get("Name") == "Busted Crown":
            cardRewardAmount -= 2
        elif relic.get("Name") == "N'loth's Gift":
            nlothsGift = True
        elif relic.get("Name") == "Molten Egg":
            moltenEgg = True
        elif relic.get("Name") == "Toxic Egg":
            toxicEgg = True
        elif relic.get("Name") == "Frozen Egg":
            frozenEgg = True
        elif relic.get("Name") == "Prismatic Shard":
            prismaticShard = True
            

    if prismaticShard == False:
        player_commons = {k:v for k,v in entities.cards.items() if v.get("Rarity") == "Common" and v.get("Owner") == entities.active_character[0].name and v.get("Upgraded") == None}
        player_uncommons = {k:v for k,v in entities.cards.items() if v.get("Rarity") == "Uncommon" and v.get("Owner") == entities.active_character[0].name and v.get("Upgraded") == None}
        player_rares = {k:v for k,v in entities.cards.items() if v.get("Rarity") == "Rare" and v.get("Owner") == entities.active_character[0].name and v.get("Upgraded") == None}
        colorless_rare_cards = {k:v for k,v in entities.cards.items() if v.get("Owner") == "Colorless" and v.get("Rarity") == "Rare" and v.get("Upgraded") != True}
        colorless_uncommon_cards = {k:v for k,v in entities.cards.items() if v.get("Owner") == "Colorless" and v.get("Rarity") == "Uncommon" and v.get("Upgraded") != True}
    elif prismaticShard == True:
        player_commons = {k:v for k,v in entities.cards.items() if v.get("Rarity") == "Common" and v.get("Owner") != "The Spire" and v.get("Upgraded") == None}
        player_uncommons = {k:v for k,v in entities.cards.items() if v.get("Rarity") == "Uncommon" and v.get("Owner") != "The Spire" and v.get("Upgraded") == None}
        player_rares = {k:v for k,v in entities.cards.items() if v.get("Rarity") == "Rare" and v.get("Owner") != "The Spire" and v.get("Upgraded") == None}
        colorless_rare_cards = {k:v for k,v in entities.cards.items() if v.get("Owner") == "Colorless" and v.get("Rarity") == "Rare" and v.get("Upgraded") != True}
        colorless_uncommon_cards = {k:v for k,v in entities.cards.items() if v.get("Owner") == "Colorless" and v.get("Rarity") == "Uncommon" and v.get("Upgraded") != True}


    if nlothsGift:
        nlothsRareCardChance = rareCardChance*3
        commonCardChance -= nlothsRareCardChance - rareCardChance
        rareCardChance = nlothsRareCardChance
    
    if gameAct == 1:
        upgradeChance = 0    

    elif gameAct == 2:
        upgradeChance = 125
    
    elif gameAct == 3:
        upgradeChance = 250

    else:
        upgradeChance = 250

    cardList = []
    if bossReward == True:
        i = 0
        while i < cardRewardAmount:
            cardList.append(2)
            i+=1
    
    elif colorless == True:
        i = 0
        while i < cardRewardAmount:
            if rd.randint(0,1) == 0:
                cardList.append(3)
            else:
                cardList.append(4)
            i+=1
    else:
        cardList = list(nchoices_with_restrictions(weights = [commonCardChance,uncommonCardChance,rareCardChance], k = cardRewardAmount))


    cardRewards = []
    while True:
        
        for card in cardList:

            if card == 0:
                cardRewards.append(rd.choices(list(player_commons.items()))[0][1])
            elif card == 1:
                cardRewards.append(rd.choices(list(player_uncommons.items()))[0][1])
            elif card == 2:
                cardRewards.append(rd.choices(list(player_rares.items()))[0][1])
            elif card == 3:
                cardRewards.append(rd.choices(list(colorless_uncommon_cards.items()))[0][1])
            elif card == 4:
                cardRewards.append(rd.choices(list(colorless_rare_cards.items()))[0][1])
        try:

            test = any(cardRewards.count(x) > 1 for x in cardRewards)

            if test:
                cardRewards = []
                continue
            else:
                break

        except Exception as e:
            print("Issue when creating cardRewards in generateCardRewards()--->", e,"\n Do you have N'loths Gift?")
            print(list(cardList))

            print("Common Card Chance:",commonCardChance,"\nUncommon Card Chance:",uncommonCardChance,"\nRare Card Chance:",rareCardChance,"\nCombined Card Chance:",commonCardChance+uncommonCardChance+rareCardChance)
            cardList = [0,0,0]

    if colorless == False and bossReward == False:
        for card in cardRewards:
            if card.get("Rarity") == "Common":
                rareCardChance += 0.01
                commonCardChance -= 0.01
            elif card.get("Rarity") == "Rare":
                rareCardChance = 0.00
                commonCardChance = 0.63
    
    i = 0
    while i < len(cardRewards):

        if moltenEgg == True and cardRewards[i].get("Type") == "Attack":
            newUpgradedCard = upgradeCard(cardRewards.pop(i),"External Function")
            cardRewards.insert(i,newUpgradedCard)
            i+=1
        elif toxicEgg == True and cardRewards[i].get("Type") == "Skill":
            newUpgradedCard = upgradeCard(cardRewards.pop(i),"External Function")
            cardRewards.insert(i,newUpgradedCard)
            i+=1
        
        elif frozenEgg == True and cardRewards[i].get("Type") == "Power":
            newUpgradedCard = upgradeCard(cardRewards.pop(i),"External Function")
            cardRewards.insert(i,newUpgradedCard)
            i+=1
        
        elif cardRewards[i].get("Rarity") != "Rare": 
            if rd.randint(1,1000) < upgradeChance:
                newUpgradedCard = upgradeCard(cardRewards.pop(i),"External Function")
                cardRewards.insert(i,newUpgradedCard)
                i+=1
            else:
                i+=1
        else:
            i+=1
    return cardRewards
    #whathappenschshere

def generatePotionRewards(event:bool = False,amount: int = 1):
    global generalPotionChance

    for relic in entities.active_character[0].relics:
        if relic.get("Name") == "White Beast Statue":
            generalPotionChance = 100       

    commonPotionChance = 0.65
    uncommonPotionChance = 0.25
    rarePotionChance = 0.10

    commonPotions = {k:v for k,v in entities.potions.items() if v.get("Rarity") == "Common" and (v.get("Owner") == entities.active_character[0].name or v.get("Owner") == "The Spire")}
    uncommonPotions = {k:v for k,v in entities.potions.items() if v.get("Rarity") == "Uncommon" and (v.get("Owner") == entities.active_character[0].name or v.get("Owner") == "The Spire")}
    rarePotions = {k:v for k,v in entities.potions.items() if v.get("Rarity") == "Rare" and (v.get("Owner") == entities.active_character[0].name or v.get("Owner") == "The Spire")}
    
    potionList = list(nchoices_with_restrictions([commonPotionChance,uncommonPotionChance,rarePotionChance],k = amount))

    potionReward = []

    while True:
        for potion in potionList:

            if potion == 0:
                potionReward.append(rd.choices(list(commonPotions.items()))[0][1]) #this may still draw a similar potion
                
            elif potion == 1:
                potionReward.append(rd.choices(list(uncommonPotions.items()))[0][1])
            
            elif potion == 2:
                potionReward.append(rd.choices(list(rarePotions.items()))[0][1]) #this may still draw a the same card twice

        test = any(potionReward.count(x) > 1 for x in potionReward)
        

        if test:
            potionReward = []
            continue
        else:
            break

    if event == True:
        #this makes sure that the potion is always sent back eve
        return potionReward
    else:
        if rd.randint(1,100) <= generalPotionChance:
            generalPotionChance -= 10
            return potionReward
        else:
            generalPotionChance += 10
            potionReward = []
            return potionReward


def pickCard(cardPrize: list,place:str = "Deck"):

    while True:
        i = 0
        for card in cardPrize:
            if card.get("Type") == "Attack":
                ansiprint (f"{i+1}. <red>{card.get('Name')}</red> | {card.get('Info')} | <yellow>Energy</yellow>: {card.get('Energy')}")
            elif card.get("Type") == "Skill":
                ansiprint (f"{i+1}. <green>{card.get('Name')}</green> | {card.get('Info')} | <yellow>Energy</yellow>: {card.get('Energy')}")
            elif card.get("Type") == "Power":
                ansiprint (f"{i+1}. <blue>{card.get('Name')}</blue> | {card.get('Info')} | <yellow>Energy</yellow>: {card.get('Energy')}")
            i += 1
        
        singingBowl = False
        if place == "Deck":
            for relic in entities.active_character[0].relics:
                if relic.get("Name") == "Singing Bowl":
                    ansiprint(str(i+1)+". Increase <red>Max HP</red> by 2","<light-red>Singing Bowl</light-red>")
                    i+=1
                    singingBowl = True
        
        print(str(i+1)+". Skip")    
        i+=1

        try:

            card_index = input("Pick the number of the card you want to add to your deck\n")
            card_index = int(card_index)-1
            if card_index == i-1:
                print("You have chosen to skip!")
                break
            elif card_index == i-2 and singingBowl == True:
                entities.active_character[0].set_maxHealth(2)
                break
            if card_index in range(len(cardPrize)):
                break
            else:
                ansiprint ("You don't have this card!")
                pass
        except Exception as e:
            entities.active_character[0].explainer_function(card_index)
            ansiprint("Type a corresponding number.")
            pass

    if card_index == i-1:
        pass
    elif card_index == i-2 and singingBowl == True:
        ansiprint("You have chosen to increase your <red>Max HP</red> by 2!")

    elif place == "Deck":
        entities.active_character[0].add_CardToDeck(cardPrize[card_index])
    elif place == "Drawpile":
        entities.active_character[0].add_CardToDrawpile(cardPrize[card_index])
    elif place == "Hand":
        entities.active_character[0].add_CardToHand(cardPrize[card_index])
    
    else:
        print("Please let me know what is written here:-->",cardPrize[card_index])

def pickPotion(potionPrize: list):

    while len(potionPrize) > 0:
        i = 0
        for potion in potionPrize:
            i += 1
            ansiprint(str(i)+". <c>" + potion.get("Name")+"</c>")
        i+=1
        ansiprint(str(i)+". Skip")
        try:

            potion_index = input("Pick the number of the Potion you want to add to your deck\n")
            potion_index = int(potion_index)-1
            if potion_index == i-1:
                print("You have chosen to skip!")
                #break
                return len(potionPrize)
            
            if potion_index in range(len(potionPrize)):
                entities.active_character[0].add_potion(potionPrize.pop(potion_index))
        
            else:
                ansiprint("There is no potion at that place! Pick again.")
                pass
        except Exception as e:
            entities.active_character[0].explainer_function(potion_index)
            print("Type a corresponding number")
            pass

def pickRelic(relicPrize:list):
    key = False
    for relic in relicPrize:
        if relic.get("Name") == "Blue Key":
            key = True

    while len(relicPrize) > 0:
        i = 0
        for relic in relicPrize:
            i += 1
            if relic.get("Name") == "Blue Key":
                ansiprint(str(i)+".","<blue>" + relic.get("Name")+"</blue>")    
            elif relic.get("Name") == "Green Key":
                ansiprint(str(i)+".","<green>" + relic.get("Name")+"</green>")    
            else:

                ansiprint(str(i)+".","<light-red>" + relic.get("Name")+"</light-red>")
        i+=1
        print(str(i)+". Skip")    
        try:

            relic_index = input("Pick the number of the relic you want to add to your deck\n")
            relic_index = int(relic_index)-1
            if relic_index == i-1:
                print("You have chosen to skip!")
                #break
                return len(relicPrize)
            
            if relic_index in range(len(relicPrize)):

                entities.active_character[0].add_relic(relicPrize.pop(relic_index))
                if entities.active_character[0].get_floor() == "Start":
                    #this means that if you have the option to pick up more than one relic after the boss you can only pickup one. it's start because you are at Start after a boss!
                    break
                
                elif key == True and len(relicPrize) == 1:
                    ansiprint("You had to decide between the <blue>Blue Key</blue> and the <light-red>Relic</light-red>")
                    break                

            else:
                ansiprint ("There is no relic at that place! Pick again.")
                pass
        except Exception as e:
            entities.active_character[0].explainer_function(relic_index)
            ansiprint("Type one of the corresponding numbers.")
            pass

def transformCard(card,place:str = "Deck",index = None): 
    transformationPool = {}
    
    if card["Type"] == "Curse":
        transformationPool = {k:v for k,v in entities.cards.items() if v.get("Type") == "Curse" and v.get("Name") != card["Name"] and v.get("Rarity") != "Special" and v.get("Upgraded") != True}

    elif card["Owner"] == entities.active_character[0].name:
        transformationPool = {k:v for k,v in entities.cards.items() if v.get("Owner") == entities.active_character[0].name and v.get("Name") != card["Name"] and "+" not in v.get("Name") and v.get("Rarity") != "Basic" and v.get("Upgraded") != True and v.get("Rarity") != "Special"}

    elif card["Owner"] == "Colorless":
        transformationPool = {k:v for k,v in entities.cards.items() if v.get("Owner") == "Colorless" and v.get("Name") != card["Name"] and "+" not in v.get("Name") and v.get("Rarity") != "Special" and v.get("Upgraded") != True}

    else:
        print("It didn't transform. Why?\n",card)   

    card_add = rd.choices(list(transformationPool.items()))[0][1]
    
    if place == "Deck":
        entities.active_character[0].add_CardToDeck(card_add,index)
    
    elif place == "Hand":
        entities.active_character[0].add_CardToHand(card_add,index)    

    elif place == "Drawpile":
        entities.active_character[0].add_CardToDrawpile(card_add,index)

    elif place == "Discardpile":
        entities.active_character[0].add_CardToDiscardpile(card_add,index)

    elif place == "Exhaustpile":
        entities.active_character[0].add_CardToExhaustpile(card_add,index)

    elif place == "External Function":
        return card_add
    
    else:
        print("This is what's wrong helpingfunctiontransformCard()--->",place)


def upgradeCard(card,place,index=None): 
    
    if card.get("Name").startswith("Searing Blow"):
        card_add = card.copy()
        print(card_add.get("Damage Gain"))
        card_add["Name"] = "Searing Blow +"
        card_add["Damage"] += card_add["Damage Gain"]
        card_add["Damage Gain"] += 1
    else:
        upgradePool = {k:v for k,v in entities.cards.items() if v.get("Upgraded") == True and v.get("Name").startswith(card["Name"]) == True}

        card_add = rd.choices(list(upgradePool.items()))[0][1]
        card_add["Unique ID"] = card.get("Unique ID")
    
        if card.get("Name") == "Ritual Dagger":
            card_add["Damage"] = card.get("Damage")

    if place == "Deck":
        entities.active_character[0].add_CardToDeck(card_add,index)
    
    elif place == "Hand":
        entities.active_character[0].add_CardToHand(card_add,index)    

    elif place == "Drawpile":
        entities.active_character[0].add_CardToDrawpile(card_add,index)    

    elif place == "Discardpile":
        entities.active_character[0].add_CardToDiscardpile(card_add,index)    
    
    elif place == "Exhaustpile":
        entities.active_character[0].add_CardToExhaustpile(card_add,index)

    elif place == "External Function":
        return card_add
    else:
        print("This is what's wrong--->",place)
        

def getRandomSpecifiedCardIndex(specifics,place: str = "Deck"):
    #thisNeedsToBe updated at some point to handle removing random cards as well.
    #shuffle list
    index = None

    test = [card for card in entities.active_character[0].deck if card.get("Upgraded") != True and card.get("Type") != "Curse"]
        
    attackUpgradedTest = [card for card in entities.active_character[0].deck if card.get("Upgraded") != True and card.get("Type") == "Attack"]
    skillUpgradedTest = [card for card in entities.active_character[0].deck if card.get("Upgraded") != True and card.get("Type") == "Skill"]
    attackTest = [card for card in entities.active_character[0].deck if card.get("Type") == "Attack"]
    skillTest = [card for card in entities.active_character[0].deck if card.get("Type") == "Skill"]
    powerTest = [card for card in entities.active_character[0].deck if card.get("Type") == "Power"]

    while True:
        if place == "Deck":
            index = rd.randint(0,len(entities.active_character[0].deck)-1)
        
        
        if specifics == "Upgrade":
            if len(list(test)) == 0:
                index = None
                break
            
            if entities.active_character[0].deck[index].get("Upgraded") != True and entities.active_character[0].deck[index].get("Type") != "Curse":
                break
            else:
                continue

        elif specifics == "Attack Upgrade":
            
            if len(list(attackUpgradedTest)) == 0:
                index = None
                break
            
            if entities.active_character[0].deck[index].get("Upgraded") != True and entities.active_character[0].deck[index].get("Type") == "Attack":
                break
            else:
                continue


        elif specifics == "Skill Upgrade":
            
            if len(list(skillUpgradedTest)) == 0:
                index = None
                break
            
            if entities.active_character[0].deck[index].get("Upgraded") != True and entities.active_character[0].deck[index].get("Type") == "Skill":
                break
            else:
                continue

        elif specifics == "Attack":
            if len(list(attackTest)) == 0:
                index = None
                break

            if entities.active_character[0].deck[index].get("Type") == "Attack":
                break
            else:
                continue

        elif specifics == "Skill":
            if len(list(skillTest)) == 0:
                index = None
                break

            if entities.active_character[0].deck[index].get("Type") == "Skill":
                break
            else:
                continue

        elif specifics == "Power":
            if len(list(powerTest)) == 0:
                index = None
                break
            if entities.active_character[0].deck[index].get("Type") == "Power":
                break
            else:
                continue

    return index

def check_Duplicates(test):
    # second element of the tuple has number of repetitions
    return Counter(test).most_common()[0][1] > 1

def generateShop(singleItem: str = None):
    theCourier = False
    membershipCard = False

    moltenEgg = False
    toxicEgg = False
    frozenEgg = False
    
    for relic in entities.active_character[0].relics:
        if relic.get("Name") == "The Courier":
            theCourier = True
        elif relic.get("Name") == "Membership Card":
            membershipCard = True
        elif relic.get("Name") == "Meal Ticket":
            entities.active_character[0].heal(15)
            ansiprint("You <red>healed 15</red> because of <light-red>Meal Ticket</light-red>!")
        elif relic.get("Name") == "Molten Egg":
            moltenEgg = True
        
        elif relic.get("Name") == "Toxic Egg":
            toxicEgg = True
        
        elif relic.get("Name") == "Frozen Egg":
            frozenEgg = True

    shoplist = []
    miniList = []
    all_player_cards = {k:v for k,v in entities.cards.items() if v.get("Owner") == entities.active_character[0].name and v.get("Upgraded") == None and v.get("Rarity") != "Basic"}
    player_commons = {k:v for k,v in entities.cards.items() if v.get("Rarity") == "Common" and v.get("Owner") == entities.active_character[0].name and v.get("Upgraded") == None}
    player_uncommons = {k:v for k,v in entities.cards.items() if v.get("Rarity") == "Uncommon" and v.get("Owner") == entities.active_character[0].name and v.get("Upgraded") == None}
    player_rares = {k:v for k,v in entities.cards.items() if v.get("Rarity") == "Rare" and v.get("Owner") == entities.active_character[0].name and v.get("Upgraded") == None}
    
    colorless_uncommon_cards = {k:v for k,v in entities.cards.items() if v.get("Owner") == "Colorless" and v.get("Rarity") == "Uncommon" and v.get("Upgraded") == None}
    colorless_rare_cards = {k:v for k,v in entities.cards.items() if v.get("Owner") == "Colorless" and v.get("Rarity") == "Rare" and v.get("Upgraded") == None}
    
    commonCardCost = rd.randint(49,60)
    uncommonCardCost = rd.randint(74,90)
    rareCardCost = rd.randint(148,181)

    uncommonColorlessCost = rd.randint(89,108)
    rareColorlessCost = rd.randint(178,217)

    commonPotionCost = rd.randint(52,57)
    uncommonPotionCost = rd.randint(79,85)
    rarePotionCost = rd.randint(104,115)
    color = ""
    
    commonChance = 0.54
    uncommonChance = 0.37
    rareChance = 0.09

    if singleItem == None:
        
        while True:
            shopClassCards = list(nchoices_with_restrictions([commonChance,uncommonChance,rareChance],k = 5))
            if shopClassCards[4] == 0:
                continue
            else:
                break

        while True:
            
            miniList.append(rd.choices(list(all_player_cards.items()))[0][1])
            cardRarity = defineCardRarity(shopClassCards[0])
            if miniList[0].get("Type") != "Attack" or miniList[0].get("Rarity") != cardRarity:
                miniList = []
                continue
            break
        
        if miniList[0].get("Rarity") == "Common":
            miniList.append(rd.randint(49,60))
        elif miniList[0].get("Rarity") == "Uncommon":
            miniList.append(rd.randint(74,90))
        elif miniList[0].get("Rarity") == "Rare":
            miniList.append(rd.randint(148,181))
        shoplist.append(miniList)
        miniList = []
        
        while True:

            miniList.append(rd.choices(list(all_player_cards.items()))[0][1])
            cardRarity = defineCardRarity(shopClassCards[1])
            if shoplist[0][0]["Name"] == miniList[0]["Name"] or miniList[0].get("Type") != "Attack" or miniList[0].get("Rarity") != cardRarity:
                miniList = []
                continue
            break
        
        if miniList[0].get("Rarity") == "Common":
            miniList.append(rd.randint(49,60))
        elif miniList[0].get("Rarity") == "Uncommon":
            miniList.append(rd.randint(74,90))
        elif miniList[0].get("Rarity") == "Rare":
            miniList.append(rd.randint(148,181))
        shoplist.append(miniList)
        miniList = []
        
        while True:
            miniList.append(rd.choices(list(all_player_cards.items()))[0][1])
            cardRarity = defineCardRarity(shopClassCards[2])
            if miniList[0].get("Type") != "Skill" or miniList[0].get("Rarity") != cardRarity:
                miniList = []
                continue
            break
        
        if miniList[0].get("Rarity") == "Common":
            miniList.append(rd.randint(49,60))
        elif miniList[0].get("Rarity") == "Uncommon":
            miniList.append(rd.randint(74,90))
        elif miniList[0].get("Rarity") == "Rare":
            miniList.append(rd.randint(148,181))


        shoplist.append(miniList)
        miniList = []
        
        while True:
            miniList.append(rd.choices(list(all_player_cards.items()))[0][1])
            cardRarity = defineCardRarity(shopClassCards[3])
            if shoplist[2][0]["Name"] == miniList[0]["Name"] or miniList[0].get("Type") != "Skill" or miniList[0].get("Rarity") != cardRarity:
                miniList = []
                continue
            break
        
        if miniList[0].get("Rarity") == "Common":
            miniList.append(rd.randint(49,60))
        elif miniList[0].get("Rarity") == "Uncommon":
            miniList.append(rd.randint(74,90))
        elif miniList[0].get("Rarity") == "Rare":
            miniList.append(rd.randint(148,181))
        shoplist.append(miniList)
        miniList = []
        
        while True:

            miniList.append(rd.choices(list(all_player_cards.items()))[0][1])
            cardRarity = defineCardRarity(shopClassCards[4])
            if miniList[0].get("Type") != "Power" or miniList[0].get("Rarity") != cardRarity:
                miniList = []
                continue
            break
        
        if miniList[0].get("Rarity") == "Common":
            miniList.append(rd.randint(49,60))
        elif miniList[0].get("Rarity") == "Uncommon":
            miniList.append(rd.randint(74,90))
        elif miniList[0].get("Rarity") == "Rare":
            miniList.append(rd.randint(148,181))
        shoplist.append(miniList)
        miniList = []
        
        #sale
        sale = rd.randint(0,4)
        shoplist[sale][1] = shoplist[sale][1] - math.floor((shoplist[sale][1]/100)*50)

        #COLORLESS UNCOMMON CARD
        miniList.append(rd.choices(list(colorless_uncommon_cards.items()))[0][1])
        miniList.append(rd.randint(89,108))
        shoplist.append(miniList)
        miniList = []

        #COLORLESS RARE CARD
        miniList.append(rd.choices(list(colorless_rare_cards.items()))[0][1])
        miniList.append(rd.randint(178,217))
        shoplist.append(miniList)
        miniList = []

        i = 0
        while i < len(shoplist):

            if moltenEgg == True and shoplist[i][0].get("Type") == "Attack":
                newUpgradedCard = upgradeCard(shoplist[i].pop(0),"External Function")
                shoplist[i].insert(0,newUpgradedCard)
                i+=1

            elif toxicEgg == True and shoplist[i][0].get("Type") == "Skill":
                newUpgradedCard = upgradeCard(shoplist[i].pop(0),"External Function")
                shoplist[i].insert(0,newUpgradedCard)
                i+=1

            elif frozenEgg == True and shoplist[i][0].get("Type") == "Power":
                newUpgradedCard = upgradeCard(shoplist[i].pop(0),"External Function")
                shoplist[i].insert(0,newUpgradedCard)
                i+=1

            else:
                i+=1

        shopPotions = generatePotionRewards(event = True, amount = 3)

        for potion in shopPotions:
            if potion.get("Rarity") == "Common":
                miniList.append(potion)
                miniList.append(rd.randint(52,57))
                shoplist.append(miniList)
                miniList = []
            elif potion.get("Rarity") == "Uncommon":
                miniList.append(potion)
                miniList.append(rd.randint(79,85))
                shoplist.append(miniList)
                miniList = []
            elif potion.get("Rarity") == "Rare":
                miniList.append(potion)
                miniList.append(rd.randint(104,115))
                shoplist.append(miniList)
                miniList = []
        
        shipShipRelics = generateRelicRewards(place = "Shop")
        #add relic prize to
        for relic in shipShipRelics:
            
            if relic.get("Rarity") == "Common":
                miniList.append(relic)
                miniList.append(rd.randint(157,172))
                shoplist.append(miniList)
                miniList = []

            elif relic.get("Rarity") == "Uncommon":
                miniList.append(relic)
                miniList.append(rd.randint(261,288))
                shoplist.append(miniList)
                miniList = []            

            elif relic.get("Rarity") == "Rare":
                miniList.append(relic)
                miniList.append(rd.randint(313,346))
                shoplist.append(miniList)
                miniList = []            

            elif relic.get("Rarity") == "Shop":
                miniList.append(relic)
                miniList.append(rd.randint(157,172))
                shoplist.append(miniList)
                miniList = []            

        if theCourier == True and membershipCard == True:
            for item in shoplist:
                newPrice = item[1] - math.floor((item[1]/100)*60)
                item[1] = newPrice
        elif theCourier == True:
            for item in shoplist:
                newPrice = item[1] - math.floor((item[1]/100)*20)
                item[1] = newPrice
        elif membershipCard == True:
            for item in shoplist:
                newPrice = item[1] - math.floor((item[1]/100)*50)
                item[1] = newPrice

        return shoplist

    elif singleItem == "Attack":
        while True:            
            shoplist.append(rd.choices(list(all_player_cards.items()))[0][1])
            if shoplist[0].get("Type") != "Attack":
                shoplist = []
                continue
            break

        shoplist.append(defineCardPrize(shoplist[0]))
        color = entities.active_character[0].get_cardColor(shoplist[0].get("Type"))

    elif singleItem == "Skill":
        while True:
            shoplist.append(rd.choices(list(all_player_cards.items()))[0][1])
            if shoplist[0].get("Type") != "Skill":
                shoplist = []
                continue
            break

        shoplist.append(defineCardPrize(shoplist[0]))
        color = entities.active_character[0].get_cardColor(shoplist[0].get("Type"))        
    
    elif singleItem == "Power":
        while True:
            shoplist.append(rd.choices(list(all_player_cards.items()))[0][1])
            if shoplist[0].get("Type") != "Power":
                shoplist = []
                continue
            break

        shoplist.append(defineCardPrize(shoplist[0]))
        color = entities.active_character[0].get_cardColor(shoplist[0].get("Type"))
    
    elif singleItem == "Colorless":
        while True:
            shopClassCards = list(nchoices_with_restrictions([commonChance,uncommonChance,rareChance],k = 1))
            if shopClassCards[0] == 0:
                continue
            break

        if shopClassCards[0] == 2:
            shoplist.append(rd.choices(list(colorless_rare_cards.items()))[0][1])
        else:
            shoplist.append(rd.choices(list(colorless_uncommon_cards.items()))[0][1])
        shoplist.append(defineCardPrize(shoplist[0]))
        color = entities.active_character[0].get_cardColor(shoplist[0].get("Type"))
    
    elif singleItem == "Potion":
        shopPotion = generatePotionRewards(event = True, amount = 1)[0]
        shoplist.append(shopPotion)
        shoplist.append(definePotionPrize(shopPotion))
        color = "c"
    elif singleItem == "Relic":
        shipShipRelic = generateRelicRewards()[0]
        shoplist.append(shipShipRelic)
        shoplist.append(defineRelicPrize(shipShipRelic))
        color = "light-red"

    ansiprint(f"<light-red>The Courier</light-red> replenished your Shop with a <{color}>{shoplist[0].get('Name')}</{color}>")
    return shoplist
    
def defineCardPrize(card):
    theCourier = False
    membershipCard = False
    
    for relic in entities.active_character[0].relics:
        if relic.get("Name") == "The Courier":
            theCourier = True
        elif relic.get("Name") == "Membership Card":
            membershipCard = True
    
    if card.get("Owner") == "Colorless":
        if card.get("Rarity") == "Rare":
            prize = rd.randint(89,108)
        elif card.get("Rarity") == "Uncommon":
            prize = rd.randint(178,217)
    
    elif card.get("Rarity") == "Common":
        prize = rd.randint(49,60)
    
    elif card.get("Rarity") == "Uncommon":
        
        prize = rd.randint(74,90)

    elif card.get("Rarity") == "Rare":
        
        prize = rd.randint(148,181)
        
    if membershipCard == True:
        prize = math.floor(prize/2)

    if theCourier == True:
        prize = math.floor(prize - prize/100*20)

    return prize

def defineCardRarity(rarityNumber):
    rarity = ""
    
    if rarityNumber == 0:
        rarity = "Common"
    elif rarityNumber == 1:
        rarity = "Uncommon"
    elif rarityNumber == 2:
        rarity = "Rare"
    
    return rarity
def defineRelicPrize(relic):
    theCourier = False
    membershipCard = False
    
    for relict in entities.active_character[0].relics:
        if relict.get("Name") == "The Courier":
            theCourier = True
        elif relict.get("Name") == "Membership Card":
            membershipCard = True
    
    if relic.get("Rarity") == "Common":
        
        prize = rd.randint(157,172)
        
    elif relic.get("Rarity") == "Uncommon":
        
        prize = rd.randint(261,288)

    elif relic.get("Rarity") == "Rare":
        
        prize = rd.randint(313,346)

    elif relic.get("Rarity") == "Shop":
        
        prize = rd.randint(157,172)
        
    if membershipCard == True:
        prize = math.floor(prize/2)

    if theCourier == True:
        prize = math.floor(prize - prize/100*20)

    return prize

def definePotionPrize(potion):
    theCourier = False
    membershipCard = False
    
    for relic in entities.active_character[0].relics:
        if relic.get("Name") == "The Courier":
            theCourier = True
        elif relic.get("Name") == "Membership Card":
            membershipCard = True
    
    if potion.get("Rarity") == "Common":
        prize = rd.randint(52,57)
                
    elif potion.get("Rarity") == "Uncommon":
        prize =rd.randint(79,85)
            
    elif potion.get("Rarity") == "Rare":
        prize = rd.randint(104,115)
                
    if membershipCard == True:
        prize = math.floor(prize/2)

    if theCourier == True:
        prize = math.floor(prize - prize/100*20)

    return prize

def displayShop(shoplist):
    ansiprint("\"Welcome to my Shop\", says the wondrous <blue>blue robed figure</blue> sitting in front of you on odd <green>green flooring</green>. \"Have a look at my wares\".")
    global removeCardCost

    changePrize = False
    theCourier = False
    mawBank = False
    for relic in entities.active_character[0].relics:
        if relic.get("Name") == "Smilling Mask":
            removeCardCost = 50
        elif relic.get("Name") == "Maw Bank":
            mawBank = True
        
        elif relic.get("Name") == "The Courier":
            theCourier = True

    shoplist.append([{"Name":"Remove Card"},removeCardCost])
    shoplist.append([{"Name":"Show Deck"}])
    shoplist.append([{"Name":"Display Map"}])
    shoplist.append([{"Name":"Leave"}])


    while True:
        
        ansiprint("You currently have <yellow>"+str(entities.active_character[0].gold)+" Gold</yellow>.")
        i = 0

        for item in shoplist:
            
            lineSpacing = " " * (30-len(item[0].get("Name")))
            
            if i+1 < 10:
                numberSpacing = "  "

            else:
                numberSpacing = " "
                #item[0] is name item [1] is price.
            if item[0].get("Type") == "Potion":
                ansiprint(f"{i+1}.{numberSpacing}<c>{item[0].get('Name')}</c>{lineSpacing}<yellow>{item[1]}</yellow>")
                
            elif item[0].get("Owner") == "Colorless":
                ansiprint(f"{i+1}.{numberSpacing}{item[0].get('Name')}{lineSpacing}<yellow>{item[1]}</yellow>")
            
            elif item[0].get("Type") == "Relic":
                ansiprint(f"{i+1}.{numberSpacing}<light-red>{item[0].get('Name')}</light-red>{lineSpacing}<yellow>{item[1]}</yellow>")
                
            elif item[0].get("Owner") == entities.active_character[0].name:
                if item[0].get("Type") == "Attack":
                    ansiprint(f"{i+1}.{numberSpacing}<red>{item[0].get('Name')}</red>{lineSpacing}<yellow>{item[1]}</yellow>")
                elif item[0].get("Type") == "Skill":
                    ansiprint(f"{i+1}.{numberSpacing}<green>{item[0].get('Name')}</green>{lineSpacing}<yellow>{item[1]}</yellow>")
                elif item[0].get("Type") == "Power":
                    ansiprint(f"{i+1}.{numberSpacing}<blue>{item[0].get('Name')}</blue>{lineSpacing}<yellow>{item[1]}</yellow>")

            elif item[0].get("Name") == "Remove Card":
                ansiprint(f"{i+1}.{numberSpacing}<light-blue>{item[0].get('Name')}</light-blue>{lineSpacing}<yellow>{item[1]}</yellow>")
                removeCardCost += 25

            elif item[0].get("Name") == "Leave":
                ansiprint(f"{i+1}.{numberSpacing}<red>{item[0].get('Name')}</red>{lineSpacing}")

            elif item[0].get("Name") == "Display Map":
                ansiprint(f"{i+1}.{numberSpacing}<red>{item[0].get('Name')}</red>{lineSpacing}")

            elif item[0].get("Name") == "Show Deck":
                ansiprint(f"{i+1}.{numberSpacing}<red>{item[0].get('Name')}</red>{lineSpacing}")
            
            i+=1

        try:
            snap = input("What do you want to buy? Type the corresponding number\n")
            snap = int(snap)-1
            if snap not in range (len(shoplist)):
                continue
            
            if shoplist[snap][0].get("Name") == "Leave":
                break 

            elif shoplist[snap][0].get("Name") == "Display Map":
                acts.show_map(game_map,game_map_dict)

            elif shoplist[snap][0].get("Name") == "Show Deck":
                entities.active_character[0].showDeck()

            elif shoplist[snap][1] <= entities.active_character[0].gold:
                entities.active_character[0].set_gold(-shoplist[snap][1])
                
                if shoplist[snap][0].get("Type") == "Potion":
                    entities.active_character[0].add_potion(shoplist[snap][0])
                
                elif shoplist[snap][0].get("Owner") == "Colorless":
                    entities.active_character[0].add_CardToDeck(shoplist[snap][0])

                elif shoplist[snap][0].get("Type") == "Relic":
                    entities.active_character[0].add_relic(shoplist[snap][0])
                    
                    if shoplist[snap][0].get("Name") == "Membership Card":
                        for item in shoplist:
                            if len(item) > 1:
                               item[1] = math.floor(item[1]/2)

                    elif shoplist[snap][0].get("Name") == "Smilling Mask":
                        for item in shoplist:
                            if item[0] == "Remove Card":
                                item[1] = 50
                            
                    elif shoplist[snap][0].get("Name") == "The Courier":
                        for item in shoplist:
                            if len(item) > 1:
                                item[1] = math.floor(item[1] - item[1]/100*20)
                        theCourier = True


                elif shoplist[snap][0].get("Owner") == entities.active_character[0].name:
                    entities.active_character[0].add_CardToDeck(shoplist[snap][0])

                elif shoplist[snap][0].get("Name") == "Remove Card":
                    entities.active_character[0].removeCardsFromDeck(amount=1,removeType="Remove")

                
                if theCourier == True:
                    try:
                        if shoplist[snap][0].get("Type") == "Potion":
                            shoplist.insert(snap,generateShop("Potion"))
                        elif shoplist[snap][0].get("Type") == "Relic":
                            shoplist.insert(snap,generateShop("Relic"))    
                        elif shoplist[snap][0].get("Owner") == "Colorless":                            
                            shoplist.insert(snap,generateShop("Colorless"))
                        elif shoplist[snap][0].get("Type") == "Attack":
                            shoplist.insert(snap,generateShop("Attack"))
                        elif shoplist[snap][0].get("Type") == "Skill":
                            shoplist.insert(snap,generateShop("Skill"))
                        elif shoplist[snap][0].get("Type") == "Power":
                            shoplist.insert(snap,generateShop("Power"))
                    except Exception as e:
                        print(e,"<-Issue with <light-red>The Courier</light-red> replenishing cards.")
                
                if shoplist[snap][0].get("Type") == None:
                    shoplist.pop(snap)
                   
                elif theCourier == True:
                    shoplist.pop(snap+1)

                else:
                    shoplist.pop(snap)
                
                if mawBank:
                    for relic in self.active_character[0].relics:
                        if relic.get("Name") == "Maw Bank":
                            relic["Working"] = False
                            ansiprint("You bought something at this Merchant and your <light-red>Maw Bank</light-red> broke!")

            elif shoplist[snap][1] > entities.active_character[0].gold:
                ansiprint("You don't have enough gold to do that!\n")
                continue

        except Exception as e:
            entities.active_character[0].explainer_function(snap)
            ansiprint("You have to type a corresponding number.")


def explainer(question):
    if type(question) != str:
        return

def spireSpearAttacks():
    attackList = []
    i = 0
    while i < 33:
        attackList.append(0)
        attackList.extend(rd.sample([1,2],k=2))
        i+=1

    return attackList

def checkSpireBros(target):
    global gameAct
    try:
        if len(entities.list_of_enemies) > 0:
            if gameAct == 4 and entities.list_of_enemies[0].name != "Corrupt Heart":            
                if len(entities.list_of_enemies) == 2:
                    for enemy in entities.list_of_enemies:
                        enemy.spireBroAttacked = True
                    entities.list_of_enemies[target].spireBroAttacked = False

                else:
                    entities.list_of_enemies[target].spireBroAttacked = False                
    except Exception as e:
        print(e)

def nchoices_with_restrictions(weights=None, restrictions=None,k = 100):
    if restrictions == None:
        restrictions = {}
    N = 0 # count how many values we have yielded so far
    last_value = None # last value that was yielded
    repeat_count = 0 # how often it has been yielded in a row
    while N < k:
        while True:
            x = rd.choices(range(len(weights)), weights)[0]
            if x == last_value and repeat_count == restrictions.get(x, 0):
                continue
            break
        yield x
        N += 1
        if x == last_value:
            repeat_count += 1
        else:
            repeat_count = 1
            last_value = x

def nchoices_with_restrictions_minions(weightsAndRestrictions,k = None):
    if k == None:
        k = 100
    #print("weightsAndRestrictions:",weightsAndRestrictions)
    weights = weightsAndRestrictions[0]
    if len(weightsAndRestrictions) == 1:
        restrictions = {}
    else:
        restrictions = weightsAndRestrictions[1]


    N = 0 # count how many values we have yielded so far
    last_value = None # last value that was yielded
    repeat_count = 0 # how often it has been yielded in a row
    while N < k:
        while True:
            x = rd.choices(range(len(weights)), weights)[0]
            if x == last_value and repeat_count == restrictions.get(x, 0):
                continue
            break
        yield x
        N += 1
        if x == last_value:
            repeat_count += 1
        else:
            repeat_count = 1
            last_value = x


# def create_intentions_list(enemy):
#     intentions = []
    
#     if enemy == "Red Louse":
#         #intentions = list(nchoices_with_restrictions([0.75,0.25],{0:2,1:1}))
#         intentions = rd.choices([0,1],weights= [0.75,0.25],k=100)

#     elif enemy == "Green Louse":
#         #intentions = list(nchoices_with_restrictions([0.75,0.25],{0:2,1:1}))
#         intentions = rd.choices([0,1],weights= [0.75,0.25],k=100)

#     return intentions
