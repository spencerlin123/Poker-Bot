'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, BidAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import random
import eval7


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        pass

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        pass
        
        card1 = my_cards[0]
        card2 = my_cards[1]

        rank1 = card1[0] # "Ad", "9c", "Th" -> "A", "9", "T"
        suit1 = card1[1] # "d", "c", "h", etc.
        rank2 = card2[0]
        suit2 = card2[1]

        game_clock = game_state.game_clock
        num_rounds = game_state.round_num

        self.strong_hole = False
        if rank1 == rank2 or (rank1 in "AKQJT9876" and rank2 in "AKQJT9876"):
            self.strong_hole = True
        
        monte_carlo_iters = 100 #try to do as many simulations as we can
        strength_w_auction, strength_wo_auction = self.calculate_strength(my_cards, monte_carlo_iters)
        self.strength_w_auction = strength_w_auction
        self.strength_wo_auction = strength_wo_auction

        if num_rounds == NUM_ROUNDS:
            # how much time we are using on our iterations
            print(game_clock)


    def calculate_strength(self, my_cards, iters):
        deck = eval7.Deck()
        my_cards = [eval7.Card(card) for card in my_cards] #makes sure cards are in nice format to be used in simulation
        for card in my_cards:
            deck.cards.remove(card)
        wins_w_auction = 0
        wins_wo_auction = 0

        # Run tons of simulation using MC and built in eval7 library to get good estimate of probability of winning with current hand
        
        # Case for opp getting auction card
        for i in range(iters):
            deck.shuffle()
            opp = 3
            community = 5
            draw = deck.peek(opp + community) # draw 8 cards
            opp_cards = draw[:opp]
            community_cards = draw[opp:]

            our_hand = my_cards + community_cards
            opp_hand = opp_cards + community_cards

            # Evaluate strength of our hand vs opp hand
            our_hand_val = eval7.evaluate(our_hand)
            opp_hand_val = eval7.evaluate(opp_hand)

            if our_hand_val > opp_hand_val:
                wins_wo_auction += 2
            elif our_hand_val  == opp_hand_val:
                wins_wo_auction += 1
            else:
                # We lost the round
                wins_wo_auction += 0

        # Case for us getting auction card
        for i in range(iters):
            deck.shuffle()
            opp = 2
            community = 5
            auction = 1
            draw = deck.peek(opp + community + auction)
            opp_cards = draw[:opp]
            community_cards = draw[opp: opp + community]
            auction_card = draw[opp+community:]

            our_hand = my_cards + community_cards + auction_card
            opp_hand = opp_cards + community_cards
            
            our_hand_val = eval7.evaluate(our_hand)
            opp_hand_val = eval7.evaluate(opp_hand)

            if our_hand_val > opp_hand_val:
                wins_w_auction += 2
            elif our_hand_val  == opp_hand_val:
                wins_w_auction += 1
            else:
                # We lost the round
                wins_w_auction += 0

        strength_w_auction = wins_w_auction / (2*iters)
        strength_wo_auction = wins_wo_auction / (2*iters)

        return strength_w_auction, strength_wo_auction
    
    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        pass

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        # May be useful, but you may choose to not use.
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        my_bid = round_state.bids[active]  # How much you bid previously (available only after auction)
        opp_bid = round_state.bids[1-active]  # How much opponent bid previously (available only after auction)
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        
        pot = my_contribution + opp_contribution #number of chips in pot
        
        # Use MC simulation to find strength difference between w/ auction and w/o auction
        strength_diff = self.strength_w_auction - self.strength_wo_auction
        if BidAction in legal_actions:
            max_bid_percentage = 0.4
            min_bid_percentage = 0.15
            bid_percentage = 0.75*strength_diff + 1/100*random.randint(-500,500)
            bid_percentage = max(min_bid_percentage, bid_percentage)
            bid_percentage = min(max_bid_percentage, bid_percentage)
            bid = bid_percentage * pot
            return BidAction(bid)
        
        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
        
        if not self.strong_hole:
            return FoldAction()
        
        # Case where you don't know if you will get the auction card or not
        # Average strength w/ auction and strength w/o acution to calculate strength during pre-flop

        if street < 3: # Pre-flop
            strength = (self.strength_w_auction - self.strength_wo_auction)/2
            raise_amount = int(my_pip + continue_cost + 0.3*pot)
            raise_cost = int(continue_cost + 0.3*pot)    
        else: # Flop/Post-Flop
            if len(my_cards) == 3: 
                strength = self.strength_w_auction
            else:
                strength = self.strength_wo_auction
            raise_amount = int(my_pip + continue_cost + 0.3*pot)
            raise_cost = int(continue_cost + 0.3*pot)
        
        if RaiseAction in legal_actions and raise_cost <= my_stack:
            raise_amount = max(min_raise, raise_amount)
            raise_amount = min(max_raise, raise_amount)
            commit_action = RaiseAction(raise_amount)
        elif CallAction in legal_actions and continue_cost <= my_stack:
            commit_action = CallAction()
        else:
            commit_action = FoldAction()
        
        # Case where opponent has put money in the pot that we yet to match
        if continue_cost > 0:
            pot_odds = (continue_cost)/(continue_cost + pot)
            intimidation = 0

            if continue_cost/pot > 0.25: # signifies that opponent betting more aggresively
                intimidation = -0.3
            strength += intimidation

            if strength >= pot_odds: # if probability of winning is greater than pot odds
                if random.random() < strength and strength > 0.7:
                    my_action = commit_action
                else:
                    my_action = CallAction()
            if strength < pot_odds:
                if strength < 0.10 and random.random() < 0.50:
                    # Bluffing!
                    if RaiseAction in legal_actions:
                        my_action = commit_action
                else:
                    my_action = FoldAction()

        # Case where we have put more money in the pot than our opponent
        else:
             # when we are stronger we are most likely to raise but not all the time to stay unpredictable
            if strength > 0.6 and random.random() < strength:
                my_action = commit_action
            # no point in folding because opponent hasn't bet anything out so we check
            else:
                my_action = CheckAction()
        
        return my_action






        if RaiseAction in legal_actions:
           min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
           min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
           max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
           print(min_raise, max_raise, my_stack, opp_stack, my_pip, opp_pip)
        
        if RaiseAction in legal_actions and len(my_cards) == 3:
            return RaiseAction(max_raise)
        if self.strong_hole == True and RaiseAction in legal_actions:
            raise_amount = min_raise + (max_raise - min_raise) * 0.1
            return RaiseAction(raise_amount)
        if CheckAction in legal_actions:
            return CheckAction()
        elif BidAction in legal_actions:
            return BidAction(int(0.5*my_stack)) # random bid between 0 and our stack
        elif self.strong_hole == False and FoldAction in legal_actions:
            return FoldAction()
        return CallAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
