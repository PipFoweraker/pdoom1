# P(Doom) Keyboard Reference

## Design Philosophy: One Function Per Key

P(Doom) follows a "one function per key" design principle for clarity and simplicity. Each key has a primary dedicated function to avoid confusion.

## Core Game Controls

| Key | Function | Context | Notes |
|-----|----------|---------|-------|
| **M** | Menu | In-game | Access pause/main menu from game |
| **ESC** | Emergency Exit | Universal | Always exits/cancels - highest priority |
| **<-** (Left Arrow) | Back/Cancel | Dialogs | Primary navigation back button |
| **Backspace** | Alternate Cancel | Dialogs | Alternative to Left Arrow |

## Action Selection

| Key | Function | Context | Notes |
|-----|----------|---------|-------|
| **1-9** | Actions 1-9 | In-game | Direct action selection by number |

## Development Commands
*Available during alpha/beta for testing*

| Key | Function | Context | Notes |
|-----|----------|---------|-------|
| **H** | Help Guide | Universal | Show help/tutorial information |
| **S** | Skip Tutorial | Tutorial overlay | Quick skip during onboarding |
| **D** | Debug Info | In-game | Development information |
| **[** | Screenshot | Universal | Save screenshot to `/screenshots/` |

## Navigation Hierarchy

1. **ESC** - Universal emergency exit (highest priority)
2. **M** - Menu access from game
3. **<- / Backspace** - Context-specific back/cancel
4. **1-9** - Direct action selection
5. **Dev keys** - Development helpers

## Context-Specific Behavior

### Main Menu
- Arrow keys: Navigate menu items
- Enter: Select item
- ESC: Exit game

### In-Game
- 1-9: Select actions directly
- M: Access pause menu
- ESC: Emergency exit to main menu

### Hiring Dialog
- Click: Select employee type
- <- or Backspace: Cancel hiring
- ESC: Emergency exit

### Tutorial Overlay
- S: Skip tutorial
- ESC: Emergency exit tutorial

## Configuration

All keybindings are configurable in `configs/default.json` under the `keybindings` section. The default configuration implements the "one function per key" principle but can be customized for accessibility needs.

## Alpha/Beta Notes

During alpha and beta testing, all development commands remain accessible and documented. This allows for comprehensive testing and feedback collection. In release versions, some development keys may be hidden or require configuration to enable.
