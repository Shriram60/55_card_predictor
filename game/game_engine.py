import pygame
from game.deck import Deck

class GameEngine:
    REVEAL_MS = 1500  # how long both cards stay side by side after a guess

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.deck = Deck()

        self.current_card = self.deck.draw()
        self.next_card = None
        self.previous_card = None  # set while the old/new reveal is showing
        self.reveal_until = 0
        self.score = 0
        self.streak = 0
        self.status_msg = "Will the next card be HIGHER or LOWER?"
        self.status_color = (220, 220, 220)

        btn_w, btn_h = 140, 48
        self.btn_higher = pygame.Rect(width // 2 - btn_w - 20, height - 90, btn_w, btn_h)
        self.btn_lower = pygame.Rect(width // 2 + 20, height - 90, btn_w, btn_h)

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_medium = pygame.font.SysFont(None, 30)
        self.font_small = pygame.font.SysFont(None, 24)

    @property
    def multiplier(self):
        """Multiplier the next correct guess earns: 2x after 3 straight wins, 3x after 5."""
        if self.streak >= 5:
            return 3
        if self.streak >= 3:
            return 2
        return 1

    def evaluate_guess(self, guess):
        """Draws next card and evaluates prediction."""
        self.next_card = self.deck.draw()

        #BUG SYMPTON:
        #Face and high cards are incorrectly judged lower than small cards.
        
        if guess == "HIGHER":
            correct = self.next_card.numeric_rank > self.current_card.numeric_rank
        else:
            correct = self.next_card.numeric_rank < self.current_card.numeric_rank

        if self.next_card.numeric_rank == self.current_card.numeric_rank:
            # Push: score and streak stay unchanged
            self.status_msg = "PUSH / TIE! Rank matched"
            self.status_color = (255, 235, 0)
        elif correct:
            # Pay the multiplier the player saw before guessing, then extend the streak
            points = self.multiplier
            self.streak += 1
            self.score += points
            self.status_msg = f"CORRECT! {self.next_card.rank_str} vs {self.current_card.rank_str}  +{points}"
            self.status_color = (80, 220, 80)
        else:
            lost_streak = self.streak >= 3
            self.streak = 0
            self.score = max(0, self.score - 1)
            self.status_msg = f"WRONG! {self.next_card.rank_str} vs {self.current_card.rank_str}"
            if lost_streak:
                self.status_msg += "  Streak lost!"
            self.status_color = (235, 75, 75)

        self.previous_card = self.current_card
        self.reveal_until = pygame.time.get_ticks() + self.REVEAL_MS
        self.current_card = self.next_card

    @property
    def revealing(self):
        return self.previous_card is not None

    def handle_event(self, event):
        if self.revealing:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_higher.collidepoint(event.pos):
                self.evaluate_guess("HIGHER")
            elif self.btn_lower.collidepoint(event.pos):
                self.evaluate_guess("LOWER")

    def update(self):
        if self.revealing and pygame.time.get_ticks() >= self.reveal_until:
            self.previous_card = None

    def render(self, screen):
        screen.fill((25, 80, 45))

        title_surf = self.font_title.render("High-Low Card Predictor", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 25))

        score_surf = self.font_medium.render(f"Score: {self.score}", True, (255, 220, 80))
        screen.blit(score_surf, (30, 30))

        streak_text = f"Streak: {self.streak}"
        if self.multiplier > 1:
            streak_text += f"  x{self.multiplier}"
        streak_color = (255, 140, 60) if self.multiplier > 1 else (210, 210, 210)
        streak_surf = self.font_small.render(streak_text, True, streak_color)
        screen.blit(streak_surf, (30, 62))

        rem_surf = self.font_small.render(f"Deck: {self.deck.remaining} left", True, (210, 210, 210))
        screen.blit(rem_surf, (self.width - rem_surf.get_width() - 30, 35))

        card_w, card_h = 130, 180
        if self.revealing:
            old_x = self.width // 2 - card_w - 25
            new_x = self.width // 2 + 25
            self.previous_card.render(screen, old_x, 100, card_w, card_h)
            # Outline the new card in the result colour
            outline = pygame.Rect(new_x - 5, 95, card_w + 10, card_h + 10)
            pygame.draw.rect(screen, self.status_color, outline, width=4, border_radius=13)
            self.current_card.render(screen, new_x, 100, card_w, card_h)

            for label, x in (("PREVIOUS", old_x), ("NEW", new_x)):
                label_surf = self.font_small.render(label, True, (210, 210, 210))
                screen.blit(label_surf, (x + card_w // 2 - label_surf.get_width() // 2, 76))

            vs_surf = self.font_medium.render("vs", True, (245, 245, 245))
            screen.blit(vs_surf, (self.width // 2 - vs_surf.get_width() // 2, 100 + card_h // 2 - vs_surf.get_height() // 2))
        else:
            self.current_card.render(screen, self.width // 2 - card_w // 2, 100, card_w, card_h)

        status_surf = self.font_small.render(self.status_msg, True, self.status_color)
        screen.blit(status_surf, (self.width // 2 - status_surf.get_width() // 2, 310))

        higher_color = (70, 90, 75) if self.revealing else (40, 140, 60)
        lower_color = (95, 70, 70) if self.revealing else (170, 50, 50)

        pygame.draw.rect(screen, higher_color, self.btn_higher, border_radius=8)
        pygame.draw.rect(screen, (220, 220, 220), self.btn_higher, width=2, border_radius=8)
        high_surf = self.font_medium.render("HIGHER", True, (255, 255, 255))
        screen.blit(
            high_surf,
            (self.btn_higher.centerx - high_surf.get_width() // 2, self.btn_higher.centery - high_surf.get_height() // 2),
        )

        pygame.draw.rect(screen, lower_color, self.btn_lower, border_radius=8)
        pygame.draw.rect(screen, (220, 220, 220), self.btn_lower, width=2, border_radius=8)
        low_surf = self.font_medium.render("LOWER", True, (255, 255, 255))
        screen.blit(
            low_surf,
            (self.btn_lower.centerx - low_surf.get_width() // 2, self.btn_lower.centery - low_surf.get_height() // 2),
        )