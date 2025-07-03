# src/modules/backend/solver/stateless_solver_strategy.py
"""
Stateless strategy pattern implementation for Wordle solver algorithms.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from src.modules.backend.stateless_word_manager import StatelessWordManager
    from src.modules.backend.word_manager import WordManager


class StatelessSolverStrategy(ABC):
    """Abstract base class for stateless Wordle solver strategies."""

    @abstractmethod
    def get_top_suggestions(
        self,
        constraints: List[Tuple[str, str]],
        count: int = 10,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
        word_set: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Get top N suggestions based on the strategy's algorithm using stateless filtering.

        Args:
            constraints: List of (guess, result) tuples representing game constraints
            count: Number of suggestions to return
            word_manager: Optional WordManager instance for backward compatibility
            stateless_word_manager: Optional StatelessWordManager for pure stateless operations
            prefer_common: Whether to prefer common words in suggestions
            word_set: Optional specific set of words to consider. If None, uses all words.

        Returns:
            List of suggested words, ordered by preference
        """
        raise NotImplementedError("Subclasses must implement get_top_suggestions")

    def _get_filtered_words(
        self,
        constraints: List[Tuple[str, str]],
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        word_set: Optional[Set[str]] = None,
    ) -> Tuple[List[str], List[str]]:
        """
        Get filtered possible and common words using stateless filtering.

        Args:
            constraints: List of (guess, result) tuples
            word_manager: Optional WordManager for backward compatibility
            stateless_word_manager: Optional StatelessWordManager
            word_set: Optional specific set of words to filter

        Returns:
            Tuple of (possible_words, common_words)
        """
        if stateless_word_manager is not None:
            # Use pure stateless manager
            possible_words = stateless_word_manager.apply_multiple_constraints(
                constraints, word_set
            )
            common_words = stateless_word_manager.get_common_words_from_set(
                set(possible_words)
            )
        elif word_manager is not None:
            # Use stateless methods on existing word manager
            possible_words = word_manager.apply_multiple_constraints(
                constraints, word_set
            )
            common_words = [
                word for word in possible_words if word in word_manager.common_words
            ]
        else:
            raise ValueError(
                "Either word_manager or stateless_word_manager must be provided"
            )

        return possible_words, common_words

    def _get_word_frequency(
        self,
        word: str,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
    ) -> int:
        """Get word frequency using available word manager."""
        if stateless_word_manager is not None:
            return stateless_word_manager.get_word_frequency(word)
        elif word_manager is not None:
            return word_manager.get_word_frequency(word)
        else:
            return 0

    def _get_word_entropy(
        self,
        word: str,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
    ) -> float:
        """Get word entropy using available word manager."""
        if stateless_word_manager is not None:
            return stateless_word_manager.get_word_entropy(word)
        elif word_manager is not None:
            return word_manager.get_word_entropy(word)
        else:
            return 0.0


class LegacyStrategyAdapter:
    """Adapter to make legacy strategies work with stateless interface."""

    def __init__(self, legacy_strategy):
        """Initialize with a legacy strategy instance."""
        self.legacy_strategy = legacy_strategy

    def get_top_suggestions(
        self,
        constraints: List[Tuple[str, str]],
        count: int = 10,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
        word_set: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Adapt legacy strategy to work with stateless interface.

        This allows legacy strategies to work with the new stateless interface
        while we incrementally migrate them.
        """
        # Get filtered words using stateless methods
        if stateless_word_manager is not None:
            possible_words = stateless_word_manager.apply_multiple_constraints(
                constraints, word_set
            )
            common_words = stateless_word_manager.get_common_words_from_set(
                set(possible_words)
            )
            wm = None  # Legacy strategies can work without word manager
        elif word_manager is not None:
            possible_words = word_manager.apply_multiple_constraints(
                constraints, word_set
            )
            common_words = [
                word for word in possible_words if word in word_manager.common_words
            ]
            wm = word_manager
        else:
            raise ValueError(
                "Either word_manager or stateless_word_manager must be provided"
            )

        # Detect if legacy_strategy is actually a stateless strategy
        if (
            hasattr(self.legacy_strategy, "__class__")
            and "Stateless" in self.legacy_strategy.__class__.__name__
        ):
            # Call using stateless interface
            return self.legacy_strategy.get_top_suggestions(
                constraints=constraints,
                count=count,
                word_manager=word_manager,
                stateless_word_manager=stateless_word_manager,
                prefer_common=prefer_common,
                word_set=set(possible_words) if possible_words else word_set,
            )
        else:
            # Call using legacy interface
            try:
                return self.legacy_strategy.get_top_suggestions(
                    count=count,
                    word_manager=wm,
                    possible_words=possible_words,
                    common_words=common_words,
                    guesses_so_far=constraints,
                )
            except TypeError:
                # Try with fewer parameters if full call fails
                try:
                    return self.legacy_strategy.get_top_suggestions(
                        count=count, word_manager=wm
                    )
                except TypeError:
                    # Last resort - just use the count parameter
                    return self.legacy_strategy.get_top_suggestions(count)
