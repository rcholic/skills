# Plan2Meal ClawdHub Skill

Manage recipes and grocery lists from your Plan2Meal app via chat.

Default backend: `https://gallant-bass-875.convex.cloud`.
Auth and recipe/grocery API traffic goes to this backend unless you override `CONVEX_URL`.

## Quick Start

```bash
# Install via ClawdHub
clawdhub install plan2meal

# Configure environment
cp .env.example .env
# Edit .env with your backend URL and OAuth credentials (required)
```

## Commands

### Recipes
- `plan2meal add <url>` - Add recipe from URL
- `plan2meal list` - List your recipes
- `plan2meal search <term>` - Search recipes
- `plan2meal show <id>` - View recipe details
- `plan2meal delete <id>` - Delete recipe

### Grocery Lists
- `plan2meal lists` - List all grocery lists
- `plan2meal list-show <id>` - View list with items
- `plan2meal list-create <name>` - Create new list
- `plan2meal list-add <listId> <recipeId>` - Add recipe to list

### Help
- `plan2meal help` - Show all commands

## Setup

See [SKILL.md](SKILL.md) for detailed setup instructions.