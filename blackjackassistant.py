# Copyright 2024 Devin Kot-Thompson devinkt@bu.edu
    
import cv2
import numpy as np
import random
import os

"""This is assignment 9 and an expansion on assignment 8: BlackJack Assistant. It uses OpenCV to capture an image of a card with the web cam and compare it to templates. 
   The matched card is drawn from the deck and added to the hand. The template matching success depends greatly on lighting conditions and template quality and size. 
   Parameters may need to be adjusted for accuracy of card recognition."""

"""This is a game assistant for BlackJack it uses the hi-low strategy for card counting where card ranks 2-6 increase the count by +1 
    and ranks 10-A decrease the count by -1. This Running Count is then divided by the number of decks in use (if more than one) to calculate 
    the True Count. A high positive True Count indicates probability slightly favors the player. This is because there is a higher
    concentration of 10 value cards meaning the probability of Black Jack is higher. Additionally, if +10 to the player current hand will not bust
    the hand it is suggested to double down. Finally the dealer must hit until their hand is >17 increasing the likelyhood that they will bust
    A percentage counter also shows the likelyhood of every card to be drawn next further increasing the edge toward the player. My sources for this
    assignment were the following:
    https://www.youtube.com/watch?v=qd5oc9hLrXg
    https://www.youtube.com/watch?v=3kGlk1E_Cnw
    https://www.youtube.com/watch?v=QLYsck5fsLU"""


class BlackJackGame:
    def __init__(self, num_players=1, num_decks=1):
        self.deck = Deck(num_decks)
        self.players = [Player(f'Player {i + 1}') for i in range(num_players)]
        self.dealer = Player('Dealer')
        self.assistant = Assistant(self.deck, num_decks)
        self.dealer.is_dealer = True
        self.num_players = num_players

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
                card = self.deck.deal_card()
                while(card is None):
                    card = self.deck.deal_card()
                player.hit(card)
                self.assistant.update_count(card)
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
                true_count = self.assistant.get_true_count()
                print(f"True Count: {true_count:.2f}")
                print(self.assistant.suggest_action(player.hand, self.dealer.hand[1], player.hand_value(), true_count))
                self.assistant.percentage_chance_next_card()
                decision = input(f"Type {player.name} Decision (hit, stay, surrender, double, split): ") #maybe turn into ui module? later will be given suggestion by assistant
                if(decision == 'hit' or decision == 'double'):
                    if(decision == 'double'):
                        player.double = True
                    card = self.deck.deal_card()
                    while(card is None):
                        card = self.deck.deal_card()
                    player.hit(card)
                    self.assistant.update_count(card)
                    player_hard_value = player.hand_value()[0] 
                    player_soft_value = player.hand_value()[1]
                    print(player.name, player.hand)
                elif(decision == 'split'):
                    player.split = True
                    card1 = self.deck.deal_card()
                    while(card1 is None):
                        card1 = self.deck.deal_card()
                    card2 = self.deck.deal_card()
                    while(card is None):
                        card2 = self.deck.deal_card()
                    player.hit(card1)
                    self.assistant.update_count(card1)
                    player.hit(card2)
                    self.assistant.update_count(card2)
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
                            card = self.deck.deal_card()
                            while(card is None):
                                card = self.deck.deal_card()
                            player.hit(card)
                            self.assistant.update_count(card)
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
                            card = self.deck.deal_card()
                            while(card is None):
                                card = self.deck.deal_card()
                            player.hit(card)
                            self.assistant.update_count(card)
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
            card = self.deck.deal_card()
            while(card is None):
                card = self.deck.deal_card()
            self.dealer.hit(card)
            self.assistant.update_count(card)
            dealer_hard_value = self.dealer.hand_value()[0]
            dealer_soft_value = self.dealer.hand_value()[1]
    
    def check_winners(self):
        """After the dealer plays winner and player status is determined. If anyone recieved BlackJack they win automatically regardless of the dealer"""
        print("dealer hand value", self.dealer.hand_value())
        dealer_hard_value = self.dealer.hand_value()[0]
        dealer_soft_value = self.dealer.hand_value()[1]
        dealer_values = [dealer_hard_value, dealer_soft_value]
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
                elif((max(hand_values) > max(dealer_values)) or (dealer_soft_value > 21)):
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


RANK_TEMPLATES = {}
SUIT_TEMPLATES = {}

preprocessed_folder = "C:\\templates"

for filename in os.listdir(preprocessed_folder):
    if filename.endswith(".png"):
        template_path = os.path.join(preprocessed_folder, filename)
        grayscale_template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        
        if "rank" in filename:
            standard_width, standard_height = 150, 200  
            resized_template = cv2.resize(grayscale_template, (standard_width, standard_height), interpolation=cv2.INTER_AREA)  
            rank = filename.split("_")[0]
            RANK_TEMPLATES[rank] = resized_template
        elif "suit" in filename:
            standard_width, standard_height = 50, 60  
            resized_template = cv2.resize(grayscale_template, (standard_width, standard_height), interpolation=cv2.INTER_AREA)  
            suit = filename.split("_")[0]
            SUIT_TEMPLATES[suit] = resized_template


def detect_rank_and_suit(card_image):
    """Template matches rank and suit against card image taken from drawn card"""
    # cv2.imshow("Original Card Image", card_image)
    cv2.waitKey(0)

    gray_card = cv2.cvtColor(card_image, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("Grayscale Card", gray_card)
    cv2.waitKey(0)

    _, thresh = cv2.threshold(gray_card, 127, 255, cv2.THRESH_BINARY)
    # cv2.imshow("Thresholded Card", thresh)
    cv2.waitKey(0)
    #print(f"Threshshape: {thresh.shape}")

    best_rank, best_suit = None, None
    best_rank_val, best_suit_val = 0, 0

    for rank, template in RANK_TEMPLATES.items():
        #print(f"Rank {rank} template size: {template.shape}")
        match = cv2.matchTemplate(gray_card, template, cv2.TM_CCOEFF_NORMED)
        # cv2.imshow(f"template - {rank}", template)
        # cv2.imshow("Match", match)
        _, max_val, _, max_loc = cv2.minMaxLoc(match)
        # print(f"Rank {rank} - Max Value: {max_val}")

        # cv2.imshow(f"Rank Match Heatmap - {rank}", match_normalized)

        h, w = template.shape[:2]  # Get template size
        match_overlay = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)  
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(match_overlay, top_left, bottom_right, (0, 255, 0), 2)  
        # cv2.imshow(f"Overlay Match - {rank}", match_overlay)
        # cv2.waitKey(0)

        # cv2.destroyAllWindows()  

        if max_val > best_rank_val:
            best_rank_val = max_val
            best_rank = rank

    for suit, template in SUIT_TEMPLATES.items():
        #print(f"Suit {suit} template size: {template.shape}")
        match = cv2.matchTemplate(gray_card, template, cv2.TM_CCOEFF_NORMED)
        # cv2.imshow(f"template - {suit}", template)
        # cv2.imshow("Match", match)
        _, max_val, _, max_loc = cv2.minMaxLoc(match)
        # print(f"Suit {suit} - Max Value: {max_val}")

        # cv2.imshow(f"Suit Match Heatmap - {suit}", match_normalized)

        h, w = template.shape[:2]  # Get template size
        match_overlay = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)  
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(match_overlay, top_left, bottom_right, (0, 255, 0), 2)  
        # cv2.imshow(f"Overlay Match - {suit}", match_overlay)
        cv2.waitKey(0)

        cv2.destroyAllWindows()  

        if max_val > best_suit_val:
            best_suit_val = max_val
            best_suit = suit

    # print(f"Best Rank: {best_rank} (Value: {best_rank_val})")
    # print(f"Best Suit: {best_suit} (Value: {best_suit_val})")

    if best_rank and best_suit:
        return {'rank': best_rank, 'suit': best_suit}
    else:
        return None

def recognize_card():
    """captures a image of the card to draw from the deck"""
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to capture image.")
        return None

    # cv2.imshow("Original Frame", frame)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    height, width = thresh.shape
    border_mask = np.zeros_like(thresh)
    cv2.rectangle(border_mask, (10, 10), (width - 10, height - 10), 255, -1)
    thresh_cleaned = cv2.bitwise_and(thresh, thresh, mask=border_mask)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thresh_cleaned = cv2.morphologyEx(thresh_cleaned, cv2.MORPH_CLOSE, kernel)

    # cv2.imshow("Threshold Cleaned", thresh_cleaned)

    contours, hierarchy = cv2.findContours(thresh_cleaned, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    frame_area = frame.shape[0] * frame.shape[1]
    min_contour_area = 0.005 * frame_area
    max_contour_area = 0.9 * frame_area

    valid_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if min_contour_area < area < max_contour_area:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            if 0.6 < aspect_ratio < 1.8:  
                valid_contours.append(cnt)

    debug_frame = frame.copy()
    cv2.drawContours(debug_frame, valid_contours, -1, (255, 0, 0), 2)
    # cv2.imshow("Filtered Contours", debug_frame)

    if not valid_contours:
        print("No valid contours found.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return None

    card_contour = max(valid_contours, key=cv2.contourArea)

    epsilon = 0.04 * cv2.arcLength(card_contour, True)
    approx = cv2.approxPolyDP(card_contour, epsilon, True)

    if len(approx) == 4:
        # print("Card detected with four corners.")
        cv2.drawContours(frame, [approx], -1, (0, 255, 0), 3)
        # cv2.imshow("Detected Card", frame)

        points = np.array([point[0] for point in approx], dtype='float32')

        width, height = 300, 400 
        destination = np.array([
            [0, 0], 
            [width - 1, 0], 
            [width - 1, height - 1], 
            [0, height - 1]
        ], dtype='float32')

        matrix = cv2.getPerspectiveTransform(points, destination)
        warped_card = cv2.warpPerspective(frame, matrix, (width, height))

        # cv2.imshow("Warped Card", warped_card)

        result = detect_rank_and_suit(warped_card)
        # print(f"Detected Card: {result}")
        return result
    # else:
        # print("Card contour approximation failed.")

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

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

    def deal_card(self):
        """Deal a card using machine vision."""
        recognized_card = recognize_card()
        if recognized_card:
            for card in self.cards:
                if str(card['rank']) == recognized_card['rank'] and card['suit'] == recognized_card['suit']:
                    self.cards.remove(card)
                    # print("Card removed from deck")
                    return card
            # print("Card not found in deck.")
        # else:
        #     # print("Failed to recognize card.")
        # return None

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


class Assistant:
    def __init__(self, deck, num_decks):
        self.running_count = 0
        self.num_decks = num_decks
        self.deck = deck

    def percentage_chance_next_card(self):
        """Provide percentage chance of each rank"""
        ace, king, queen, jack, ten, nine, eight, seven, six, five, four, three, two = 0,0,0,0,0,0,0,0,0,0,0,0,0
        for card in self.deck.cards:
            if(card['rank'] == 'A'):
                ace += 1
            elif(card['rank'] == 'K'):
                king += 1
            elif(card['rank'] == 'Q'):
                queen += 1
            elif(card['rank'] == 'J'):
                jack += 1
            elif(card['rank'] == 10):
                ten += 1
            elif(card['rank'] == 9):
                nine += 1
            elif(card['rank'] == 8):
                eight += 1
            elif(card['rank'] == 7):
                seven += 1
            elif(card['rank'] == 6):
                six += 1
            elif(card['rank'] == 5):
                five += 1
            elif(card['rank'] == 4):
                four += 1
            elif(card['rank'] == 3):
                three += 1
            else:
                two += 1
        num_cards = len(self.deck.cards)
        per_ace = (ace/num_cards)*100
        per_king = (king/num_cards)*100
        per_queen = (queen/num_cards)*100
        per_jack = (jack/num_cards)*100
        per_ten = (ten/num_cards)*100
        per_nine = (nine/num_cards)*100
        per_eight = (eight/num_cards)*100
        per_seven = (seven/num_cards)*100
        per_six = (six/num_cards)*100
        per_five = (five/num_cards)*100
        per_four = (four/num_cards)*100
        per_three = (three/num_cards)*100
        per_two = (two/num_cards)*100
        print(f"""Percent chance of each card:
            Ace:   {per_ace:.2f}%  
            King:  {per_king:.2f}%  
            Queen: {per_queen:.2f}%  
            Jack:  {per_jack:.2f}%  
            Ten:   {per_ten:.2f}%  
            Nine:  {per_nine:.2f}%  
            Eight: {per_eight:.2f}%  
            Seven: {per_seven:.2f}%  
            Six:   {per_six:.2f}%  
            Five:  {per_five:.2f}%  
            Four:  {per_four:.2f}%  
            Three: {per_three:.2f}%  
            Two:   {per_two:.2f}%""")        
    
    def update_count(self, card):
        """Update the running count based on the card dealt."""
        if card['rank'] in [2, 3, 4, 5, 6]:
            self.running_count += 1
        elif card['rank'] in [10, 'J', 'Q', 'K', 'A']:
            self.running_count -= 1
    
    def get_true_count(self):
        """Calculate the true count by adjusting for remaining decks."""
        remaining_decks = max(self.num_decks - (52 - len(self.deck.cards)) / 52, 1)  # Prevent division by zero
        return self.running_count / remaining_decks
    
    def suggest_action(self, player_hand, dealer_card, player_value, true_count):
        """Provide a suggestion based on the current game state and true count."""
        if true_count > 3:
            return "Consider doubling or splitting if the hand allows it."
        elif true_count < -1:
            return "Play conservatively, the deck favors the dealer."
        else:
            return "Play standard strategy."






game1 = BlackJackGame(num_players=1)
game1.start_game()
