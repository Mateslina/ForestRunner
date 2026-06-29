"""
Base screen interface.

All screens (start, playing, shop, game over, etc.) inherit from this class and
implement the same lifecycle methods: event handling, update, and draw.
"""


class BaseScreen:
    """Abstract base class for all game screens."""

    def __init__(self, game):
        """Store reference to the main Game instance."""
        self.game = game

    def handle_events(self, event) -> None:
        """Handle a single pygame event (keyboard, mouse, quit, ...)."""

    def update(self, dt: float) -> None:
        """Advance game logic by dt seconds."""

    def draw(self) -> None:
        """Render the screen to the game window."""
