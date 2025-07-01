# TODO - Planned Changes and Future Improvements

This document tracks planned changes, improvements, and new features for the Wordle Solver project.

## 🧹 Code Cleanup and Refactoring

### Remove Memory Profiling Infrastructure
- [ ] Remove memory profiling from all code modules
- [ ] Remove memory profile functions and decorators
- [ ] Remove `psutil` dependency from requirements
- [ ] Clean up any memory monitoring imports and calls
- [ ] Update documentation to remove memory profiling references

### Implement Observer Pattern
- [ ] Implement observer pattern for game state management
- [ ] Create event system for game state changes
- [ ] Decouple game engine from direct state management
- [ ] Add event listeners for UI updates and statistics tracking
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

## Priority Levels

### High Priority (Next Release)
- Remove memory profiling infrastructure
- Implement observer pattern
- Visual keyboard display

### Medium Priority (Future Releases)
- JSON-RPC web service preparation
- Game rule parameterization
- Additional language dictionaries

### Low Priority (Long-term Goals)
- MCP server implementation
- Advanced game modes (chaos, cheat)
- Real-world evidence solver mode

---

## Contributing

If you're interested in working on any of these items:

1. Check the [Contributing Guide](https://raeq.github.io/wordle_solver2/contributing.html)
2. Open an issue to discuss the feature
3. Create a feature branch and submit a PR
4. Update this TODO list when items are completed

---

**Last Updated**: July 1, 2025  
**Repository**: https://github.com/raeq/wordle_solver2  
**Documentation**: https://raeq.github.io/wordle_solver2/
