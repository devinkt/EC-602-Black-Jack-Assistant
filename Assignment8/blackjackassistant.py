import random

class BlackJackGame:
    def __init__(self, num_players=1, num_decks=1):
        self.deck = Deck(num_decks)
        self.players = [Player(f'Player {i + 1}') for i in range(num_players)]
        self.dealer = Player('Dealer')
        self.dealer.is_dealer = True

    def start_game(self):
        """Starts main game sequence shuffle--> deal --> player turns --> dealer turns--> results --> repeat"""
        while self.players is not None:                
            self.deck.shuffle()
            self.deal_initial_cards()
            self.player_turns()
            self.dealer_turns()
            self.check_winners()
            # self.display_bankrolls()
            self.dealer.hand = []
            for player in self.players:
                player.hand = []
                if(player.bankroll == 0):
                    self.players.remove(player)
        
    def deal_initial_cards(self):
        """Deal 2 cards to each player and the dealer"""
        for player in self.players + [self.dealer]:
            for _ in range(2):
                player.hit(self.deck.deal_card())
            if(player.is_dealer):
                print(player.name, player.hand[1])
            else:
                print(player.name, player.hand)
    
    def player_turns(self):
        """Each player makes their turns one at a time"""
        for player in self.players:
            player_hard_value = player.hand_value()[0]
            player_soft_value = player.hand_value()[1]
            while player_hard_value < 21 or player_soft_value < 21:
                #display user hand_value
                decision = input(f"Type {player.name} Decision (hit, stay, surrender, double, split): ") #maybe turn into ui module? later will be given suggestion by assistant
                if(decision == 'hit' or decision == 'double'):
                    if(decision == 'double'):
                        player.double = True
                    player.hit(self.deck.deal_card())
                    player_hard_value = player.hand_value()[0] 
                    player_soft_value = player.hand_value()[1]
                    print(player.name, player.hand)
                elif(decision == 'split'):
                    player.split = True
                    player.hit(self.deck.deal_card())
                    player.hit(self.deck.deal_card())
                    deck1 = [player.hand[0],player.hand[2]]
                    deck2 = [player.hand[1],player.hand[3]]
                    print(player.name,"\n",deck1, "\n", deck2)
                    player_hard_value_deck1 = player.hand_value_split()[0]
                    player_hard_value_deck2 = player.hand_value_split()[1]
                    player_soft_value_deck1 = player.hand_value_split()[2]
                    player_soft_value_deck2 = player.hand_value_split()[3]
                    while(player_hard_value_deck1 < 21 or player_soft_value_deck1 <21):
                        decision = input(f"{player.name} would you like to hit or stay on hand 1: ")
                        split_hit_value = [0, 0]
                        if(decision == 'hit'):
                            player.hit(self.deck.deal_card())
                            next_card = player.hand[-1]
                            split_hit_value = player.next_card_value(next_card)
                            print(split_hit_value)
                            player_hard_value_deck1 += split_hit_value[0]
                            player_soft_value_deck1 += split_hit_value[1]
                        else:
                            break
                    print("Hand 1 values: ", player_hard_value_deck1 , player_soft_value_deck1)
                    while(player_hard_value_deck2 < 21 or player_soft_value_deck2 <21):
                        decision = input(f"{player.name} would you like to hit or stay on hand 2: ")
                        split_hit_value = [0, 0]
                        if(decision == 'hit'):
                            player.hit(self.deck.deal_card())
                            next_card = player.hand[-1]
                            split_hit_value = player.next_card_value(next_card)
                            print(split_hit_value)
                            player_hard_value_deck1 += split_hit_value[0]
                            player_soft_value_deck1 += split_hit_value[1]
                        else:
                            break
                    print("Hand 2 values: ", player_hard_value_deck2, player_soft_value_deck2)
                #elif(decision == 'stay'):
                else:
                    player_hard_value = player.hand_value()[0] 
                    player_soft_value = player.hand_value()[1]
                    print(player.name, player.hand)
                    break

    
    def dealer_turns(self):
        """Dealer begins after all players have finished should reveal "hidden" card"""
        print("dealer hand value", self.dealer.hand_value())
        dealer_hard_value = self.dealer.hand_value()[0]
        dealer_soft_value = self.dealer.hand_value()[1]
        while(dealer_hard_value < 17 or dealer_soft_value < 17 or dealer_hard_value == 21 or dealer_soft_value == 21):
            self.dealer.hit(self.deck.deal_card())
            dealer_hard_value = self.dealer.hand_value()[0]
            dealer_soft_value = self.dealer.hand_value()[1]
    
    def check_winners(self):
        """After the dealer plays winner and player status is determined. If anyone recieved BlackJack they win automatically regardless of the dealer"""
        print("dealer hand value", self.dealer.hand_value())
        dealer_hard_value = self.dealer.hand_value()[0]
        dealer_soft_value = self.dealer.hand_value()[1]
        for player in self.players:
            if(player.split):
                player_hard_value_deck1 = player.hand_value_split()[0]
                player_hard_value_deck2 = player.hand_value_split()[1]
                player_soft_value_deck1 = player.hand_value_split()[2]
                player_soft_value_deck2 = player.hand_value_split()[3]
                hand1_values = [player_hard_value_deck1, player_soft_value_deck1]
                hand2_values = [player_hard_value_deck2, player_soft_value_deck2]
                for hand in hand1_values:
                    if(hand > 21):
                        hand1_values.remove(hand)
                for hand in hand2_values:
                    if(hand > 21):
                        hand2_values.remove(hand)
                best_hand1 = max(hand1_values)
                best_hand2 = max(hand2_values)
                if(best_hand1 is None and best_hand2 is None):
                    player.bankroll -= 10 #bust
                    print("bust")
                    print(f"{player.name} bankroll: ${player.bankroll}")
                elif(best_hand1 > max(dealer_hard_value, dealer_soft_value) and best_hand2 < max(dealer_hard_value, dealer_soft_value)):
                    if(best_hand1 == 21):
                        player.bankroll += 5
                elif(best_hand2 > max(dealer_hard_value, dealer_soft_value) and best_hand1 < max(dealer_hard_value, dealer_soft_value)):
                    if(best_hand2 == 21):
                        player.bankroll += 5
                elif(best_hand2 > max(dealer_hard_value, dealer_soft_value) and best_hand1 > max(dealer_hard_value, dealer_soft_value)):
                    if(best_hand1 == 21 and best_hand2 == 21):
                        player.bankroll += 30
                    else:
                        player.bankroll += 20
                else:
                        player.bankroll -= 20

            else:
                print(f"{player.name} hand values: ", player.hand_value()) #ui?
                player_hard_value = player.hand_value()[0]
                player_soft_value = player.hand_value()[1]
                hand_values = [player_hard_value, player_soft_value]
                for value in hand_values:
                    if(value > 21):
                        hand_values.remove(value)
                if(player_hard_value > 21 and player_soft_value > 21):
                    if(player.double):
                        player.bankroll -= 20
                    else:
                        player.bankroll -= 10 #bust
                    print("bust")
                    print(f"{player.name} bankroll: ${player.bankroll}")
                elif((max(hand_values) > max(hand_values)) or (dealer_soft_value > 21)):
                    if(player_hard_value == 21 or player_soft_value == 21):
                        if(player.double):
                            player.bankroll += 30
                        else:
                            player.bankroll += 15
                    else:
                        if(player.double):
                            player.bankroll += 20
                        else:
                            player.bankroll += 10 #win
                    print("win")
                    print(f"{player.name} bankroll: ${player.bankroll}")
                elif(max(player_hard_value, player_soft_value) == max(dealer_hard_value, dealer_soft_value)):
                    print("push")
                    print(f"{player.name} bankroll: ${player.bankroll}")
                else:
                    if(player.split):
                        player.bankroll -= 20
                    else:
                        player.bankroll -= 10 #lost
                    print("lost")
                    print(f"{player.name} bankroll: ${player.bankroll}")


class Deck:
    def __init__(self, num_decks=1):
        self.num_decks = num_decks
        self.cards = self.generate_deck()
    
    def generate_deck(self):
        """Generate a standard deck of cards"""
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
        return [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks] * self.num_decks

    def shuffle(self):
        """Randomise the cards"""
        random.shuffle(self.cards)

    #this will need to be changed to pop based on open cv input
    def deal_card(self):
        """Deal first card from last index"""
        return self.cards.pop()

class Player:
    def __init__(self, name, bankroll = 100):
        self.name = name
        self.bankroll = bankroll
        self.hand = []
        self.is_dealer = False
        self.split = False
        self.double = False
    
    def hand_value(self):
        """Calculate hand value of the player"""
        hard_value = 0
        soft_value = 0
        for card in self.hand:
            if card['rank'] in ['J', 'Q', 'K']:
                hard_value += 10
                soft_value += 10
            elif card['rank'] in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
                hard_value += card['rank']
                soft_value += card['rank']
            else:
                hard_value += 11
                soft_value += 1
        return hard_value, soft_value

    def hit(self, card):
        """Player elects to hit add to hand"""
        self.hand.append(card)

    def hand_value_split(self, ):
        """Calculate hand values for a split hand return as hard value of hand 1, hard value of hand 2, soft value of hand 1, sof value of hand 2"""
        hard_value_hand1 = 0
        hard_value_hand2 = 0
        soft_value_hand1 = 0
        soft_value_hand2 = 0
        hand1 = []
        hand2 = []
        i = 0
        # hand1 = [self.hand[0], self.hand[2]]
        # hand2 = [self.hand[1], self.hand[3]]
        for card in self.hand:
            if(i%2 == 0):
                hand1.append(card)
            else:
                hand2.append(card)
            i+=1
        for card in hand1:
            if card['rank'] in ['J', 'Q', 'K']:
                hard_value_hand1 += 10
                soft_value_hand1 += 10
            elif card['rank'] in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
                hard_value_hand1 += card['rank']
                soft_value_hand1 += card['rank']
            else:
                hard_value_hand1 += 11
                soft_value_hand1 += 1
        for card in hand2:
            if card['rank'] in ['J', 'Q', 'K']:
                hard_value_hand2 += 10
                soft_value_hand2 += 10
            elif card['rank'] in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
                hard_value_hand2 += card['rank']
                soft_value_hand2 += card['rank']
            else:
                hard_value_hand2 += 11
                soft_value_hand2 += 1
        return hard_value_hand1, hard_value_hand2, soft_value_hand1, soft_value_hand2
    
    def next_card_value(self, card):
        """card value calculation for additional cards in split instance"""
        hard_value = 0
        soft_value = 0
        if card['rank'] in ['J', 'Q', 'K']:
            hard_value += 10
            soft_value += 10
        elif card['rank'] in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
            hard_value += card['rank']
            soft_value += card['rank']
        else:
            hard_value += 11
            soft_value += 1
        return hard_value, soft_value


game1 = BlackJackGame(num_players=2)
game1.start_game()