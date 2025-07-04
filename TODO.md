# TODO - Planned Changes and Future Improvements

This document tracks planned changes, improvements, and new features for the Wordle Solver project.

## 🧹 Code Cleanup and Refactoring

### Remove Memory Profiling Infrastructure
- [x] Remove memory profiling from all code modules
- [x] Remove memory profile functions and decorators
- [x] Remove `psutil` dependency from requirements
- [x] Clean up any memory monitoring imports and calls
- [x] Update documentation to remove memory profiling references

### Implement Observer Pattern
- [x] Implement observer pattern for game state management
- [x] Create event system for game state changes
- [x] Decouple game engine from direct state management
- [x] Add event listeners for UI updates and statistics tracking
- [ ] Update architecture documentation to reflect observer pattern usage

## 🎨 User Interface Improvements

### Visual Keyboard Display
- [ ] Add visual keyboard representation in CLI
- [ ] Show previously used letters and their current coloration
- [ ] Implement keyboard state tracking
- [ ] Add keyboard display to game mode interface
- [ ] Include keyboard in solver mode for better UX

## 🔧 Backend Architecture

### JSON-RPC Web Service Preparation
- [ ] Decouple backend from CLI frontend completely
- [ ] Design JSON-RPC API specification
- [ ] Implement service layer for web API
- [ ] Add API versioning support
- [ ] Create client interface abstractions
- [ ] Add authentication and session management
- [ ] Implement rate limiting and request validation

## 🌍 Internationalization

### Additional Language Dictionaries
- [ ] Add Spanish word dictionary support
- [ ] Add French word dictionary support
- [ ] Add German word dictionary support
- [ ] Implement language selection configuration
- [ ] Add language-specific letter frequency analysis
- [ ] Update documentation for multi-language support

## 🏗️ Environment Management

### Development and Production Environments
- [ ] Implement comprehensive dev/prod environment separation
- [ ] Add environment-specific configuration management
- [ ] Set up different logging levels per environment
- [ ] Implement environment-specific database configurations
- [ ] Add development-only debugging features
- [ ] Create production deployment scripts and documentation

## 🤖 AI Integration

### MCP Server Implementation
- [ ] Implement Wordle-Solver MCP (Model Context Protocol) server
- [ ] Design MCP interface for LLM integration
- [ ] Add structured data exchange protocols
- [ ] Implement tool descriptions for LLM consumption
- [ ] Add safety and validation layers for AI interactions
- [ ] Create documentation for LLM developers

## 🎯 Game Rule Parameterization

### Configurable Game Rules
- [ ] Parameterize word length (support 4-8 letter words)
- [ ] Parameterize number of allowed guesses
- [ ] Add configuration validation for rule combinations
- [ ] Update word dictionaries for different word lengths
- [ ] Modify strategies to handle variable word lengths
- [ ] Update UI to accommodate different game configurations

## 🎮 Advanced Game Modes

### Chaos Mode
- [ ] Implement chaos mode where hidden word can change mid-game
- [ ] Add rules for when word changes are allowed
- [ ] Design fair gameplay mechanics for chaos mode
- [ ] Update solver strategies to handle changing targets
- [ ] Add chaos mode configuration options

### Cheat Mode
- [ ] Implement cheat mode with character revelation
- [ ] Add cost mechanism (reveal character costs one attempt)
- [ ] Design cheat usage strategy and limitations
- [ ] Add UI controls for cheat activation
- [ ] Track cheat usage in game statistics

## 📊 Advanced Analytics

### Real-World Evidence Solver Mode
- [ ] Implement comprehensive strategy analysis framework
- [ ] Run every strategy against every word in dictionary
- [ ] Collect performance statistics for all strategy/word combinations
- [ ] Build evidence-based recommendation system
- [ ] Create performance heatmaps and visualizations
- [ ] Implement adaptive strategy selection based on real-world evidence
- [ ] Add statistical significance testing for strategy comparisons

## 🔮 Future Enhancements

### Additional Features Under Consideration
- [ ] Multiplayer mode support
- [ ] Tournament and competition framework
- [ ] Machine learning strategy optimization
- [ ] Custom word list support
- [ ] Accessibility improvements (screen reader support)
- [ ] Mobile app development
- [ ] Integration with external Wordle variants
- [ ] Advanced statistics dashboard
- [ ] Social features (sharing results, leaderboards)
- [ ] Plugin system for custom strategies

## 📚 Documentation Improvements

### Documentation Enhancements
- [ ] Add video tutorials for complex features
- [ ] Create strategy comparison guides
- [ ] Add troubleshooting section
- [ ] Implement interactive documentation examples
- [ ] Add performance benchmarking documentation
- [ ] Create developer onboarding guide

## 🧪 Testing and Quality Assurance

### Testing Infrastructure
- [ ] Increase test coverage to 95%+
- [ ] Add performance benchmarking tests
- [ ] Implement end-to-end testing framework
- [ ] Add load testing for web service components
- [ ] Create automated regression testing
- [ ] Add property-based testing for strategies

---

## Revised Roadmap and Implementation Strategy

### Phase 1: Critical Foundation (Next 4-6 Weeks)
- ✅ Remove memory profiling infrastructure (appears to be already completed)
- 🔥 Implement observer pattern for game state management
  - This creates the foundation for all future features
  - Enables loose coupling between components
  - Start with core event system and subscriber interfaces
- 📊 Enhance testing infrastructure incrementally
  - Focus on unit tests for new observer pattern components
  - Establish continuous integration workflow improvements

### Phase 2: Architecture Preparation (Weeks 7-12)
- 🔧 Begin backend decoupling
  - Create service layer interfaces
  - Separate business logic from presentation
  - Implement dependency injection pattern
- ⚙️ Enhance configuration management
  - Centralize configuration handling
  - Create abstractions for environment-specific settings
  - Prepare for game rule parameterization

### Phase 3: User Experience (Weeks 13-16)
- 🎨 Implement visual keyboard display
  - Leverage observer pattern for state management
  - Add UI components for keyboard visualization
  - Focus on user experience improvements

### Medium Priority (Next Quarter)
- Complete JSON-RPC web service preparation
- Implement game rule parameterization
- Begin internationalization with one additional language

### Long-term Goals (6+ Months)
- MCP server implementation
- Advanced game modes (chaos, cheat)
- Real-world evidence solver mode

### Risk-Benefit Analysis
- **Observer Pattern First**: Creates architectural foundation that simplifies all future work
- **Incremental Approach**: Each phase delivers tangible value while building toward larger goals
- **Test-Driven Development**: Ensures quality while implementing new architectural patterns
- **Backward Compatibility**: Maintain existing functionality during refactoring

## Implementation Details

### Observer Pattern Implementation Plan

```python
# Core event system
class GameEvent:
    """Base class for all game events"""
    pass

class LetterGuessedEvent(GameEvent):
    """Event fired when a letter is guessed"""
    def __init__(self, letter: str, result: str):
        self.letter = letter  # The guessed letter
        self.result = result  # 'correct', 'present', or 'absent'

class GameStateObserver:
    """Interface for all observers that want to be notified of game events"""
    def notify(self, event: GameEvent) -> None:
        """Called when a relevant event occurs"""
        pass

class GameEventBus:
    """Central event dispatcher for the game"""
    def __init__(self):
        self._observers = []

    def subscribe(self, observer: GameStateObserver) -> None:
        """Add an observer to be notified of events"""
        self._observers.append(observer)

    def publish(self, event: GameEvent) -> None:
        """Notify all observers of an event"""
        for observer in self._observers:
            observer.notify(event)
```

### Configuration Management Enhancement

```python
from typing import Dict, Any, Optional
import yaml
import os

class ConfigManager:
    """Centralized configuration management with environment support"""
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._config = {}
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """Load configuration from files and environment variables"""
        # Base configuration
        with open('config.yaml', 'r') as f:
            self._config = yaml.safe_load(f)

        # Environment-specific configuration
        env = os.getenv('WORDLE_ENV', 'development')
        env_config_path = f'config.{env}.yaml'
        if os.path.exists(env_config_path):
            with open(env_config_path, 'r') as f:
                env_config = yaml.safe_load(f)
                # Deep merge configurations
                self._deep_update(self._config, env_config)

    def _deep_update(self, d: Dict[str, Any], u: Dict[str, Any]) -> None:
        """Recursively update a dict with another dict"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key path (dot notation)"""
        parts = key.split('.')
        config = self._config
        for part in parts:
            if part not in config:
                return default
            config = config[part]
        return config
```

---

## Contributing

If you're interested in working on any of these items:

1. Check the [Contributing Guide](https://raeq.github.io/wordle_solver2/contributing.html)
2. Open an issue to discuss the feature
3. Create a feature branch and submit a PR
4. Update this TODO list when items are completed

---

**Last Updated**: July 1, 2025 (Roadmap revised)  
**Repository**: https://github.com/raeq/wordle_solver2  
**Documentation**: https://raeq.github.io/wordle_solver2/
