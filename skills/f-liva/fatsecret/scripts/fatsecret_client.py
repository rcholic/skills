#!/usr/bin/env python3
"""
FatSecret API Client for OpenClaw - READ-ONLY

Uses OAuth2 client credentials flow for read-only access:
- Food search
- Barcode lookup  
- Recipe search
- Food details

NOTE: This client CANNOT write to user diary.
For diary logging, use fatsecret_diary_simple.py (OAuth1 3-legged).
"""

import json
import os
import sys
import time
from typing import Any, Optional

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)

# Configuration - use FATSECRET_CONFIG_DIR env var for persistent storage in containers
_CONFIG_DIR = os.environ.get("FATSECRET_CONFIG_DIR", os.path.expanduser("~/.config/fatsecret"))
CONFIG_PATH = os.environ.get("FATSECRET_CONFIG", os.path.join(_CONFIG_DIR, "config.json"))
TOKEN_PATH = os.environ.get("FATSECRET_TOKEN", os.path.join(_CONFIG_DIR, "token.json"))

# Proxy is optional - loaded from env var or config file
def _get_default_proxy():
    """Get proxy from environment or config file."""
    proxy = os.environ.get("FATSECRET_PROXY")
    if not proxy and os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                config = json.load(f)
                proxy = config.get("proxy")
        except:
            pass
    return proxy

PROXY_URL = _get_default_proxy()

class FatSecretClient:
    """FatSecret API client with OAuth2 authentication."""
    
    TOKEN_URL = "https://oauth.fatsecret.com/connect/token"
    API_URL = "https://platform.fatsecret.com/rest/server.api"
    
    def __init__(self, client_id: str = None, client_secret: str = None, proxy: str = None):
        """Initialize client with API credentials."""
        if client_id and client_secret:
            self.client_id = client_id
            self.client_secret = client_secret
        else:
            self._load_config()
        self.access_token = None
        self.token_expires = 0
        self.proxy = proxy or PROXY_URL
        self.proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
    
    def _load_config(self):
        """Load credentials from config file."""
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError(
                f"Config not found at {CONFIG_PATH}. "
                "Create config with client_id and client_secret (or consumer_key and consumer_secret)."
            )
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        # Support both naming conventions
        self.client_id = config.get("client_id") or config.get("consumer_key")
        self.client_secret = config.get("client_secret") or config.get("consumer_secret")
    
    def _get_token(self) -> str:
        """Get or refresh OAuth2 access token."""
        # Check if we have a valid cached token
        if self.access_token and time.time() < self.token_expires - 60:
            return self.access_token
        
        # Try to load cached token from file
        if os.path.exists(TOKEN_PATH):
            try:
                with open(TOKEN_PATH) as f:
                    token_data = json.load(f)
                if time.time() < token_data.get("expires_at", 0) - 60:
                    self.access_token = token_data["access_token"]
                    self.token_expires = token_data["expires_at"]
                    return self.access_token
            except:
                pass
        
        # Request new token
        response = requests.post(
            self.TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "basic"
            },
            proxies=self.proxies
        )
        response.raise_for_status()
        data = response.json()
        
        self.access_token = data["access_token"]
        self.token_expires = time.time() + data.get("expires_in", 86400)
        
        # Cache token to file
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, 'w') as f:
            json.dump({
                "access_token": self.access_token,
                "expires_at": self.token_expires
            }, f)
        
        return self.access_token
    
    def _make_request(self, method: str, params: dict = None) -> dict:
        """Make authenticated request to FatSecret API."""
        params = params or {}
        token = self._get_token()
        
        # Add method and format
        params["method"] = method
        params["format"] = "json"
        
        response = requests.post(
            self.API_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data=params,
            proxies=self.proxies
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Check for API errors
        if "error" in data:
            error = data["error"]
            raise Exception(f"FatSecret API Error {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}")
        
        return data
    
    # ==================== FOOD METHODS ====================
    
    def search_foods(self, query: str, page: int = 0, max_results: int = 20) -> dict:
        """Search for foods by keyword.
        
        Args:
            query: Search term (e.g., "chicken breast")
            page: Page number (0-indexed)
            max_results: Results per page (max 50)
        
        Returns:
            Dict with 'foods' containing search results
        """
        return self._make_request("foods.search", {
            "search_expression": query,
            "page_number": str(page),
            "max_results": str(min(max_results, 50))
        })
    
    def get_food(self, food_id: int) -> dict:
        """Get detailed nutrition info for a food.
        
        Args:
            food_id: FatSecret food ID
        
        Returns:
            Dict with complete food data including servings
        """
        return self._make_request("food.get.v4", {"food_id": str(food_id)})
    
    def find_by_barcode(self, barcode: str) -> dict:
        """Look up food by barcode (UPC/EAN).
        
        Args:
            barcode: Product barcode
        
        Returns:
            Food details if found
        """
        result = self._make_request("food.find_id_for_barcode", {"barcode": barcode})
        food_id = result.get("food_id", {}).get("value")
        if food_id:
            return self.get_food(int(food_id))
        raise Exception(f"Barcode {barcode} not found")
    
    def autocomplete(self, expression: str, max_results: int = 10) -> dict:
        """Get autocomplete suggestions.
        
        Args:
            expression: Partial search term
            max_results: Max suggestions
        
        Returns:
            Dict with suggestions
        """
        return self._make_request("foods.autocomplete", {
            "expression": expression,
            "max_results": str(max_results)
        })
    
    # ==================== RECIPE METHODS ====================
    
    def search_recipes(self, query: str, page: int = 0, max_results: int = 20) -> dict:
        """Search for recipes.
        
        Args:
            query: Search term
            page: Page number
            max_results: Results per page
        
        Returns:
            Dict with recipe search results
        """
        return self._make_request("recipes.search.v3", {
            "search_expression": query,
            "page_number": str(page),
            "max_results": str(max_results)
        })
    
    def get_recipe(self, recipe_id: int) -> dict:
        """Get detailed recipe info.
        
        Args:
            recipe_id: FatSecret recipe ID
        
        Returns:
            Dict with recipe details, ingredients, directions, nutrition
        """
        return self._make_request("recipe.get.v2", {"recipe_id": str(recipe_id)})


def format_food_result(food: dict) -> str:
    """Format food data for display."""
    f = food.get("food", food)
    lines = [
        f"**{f.get('food_name', 'Unknown')}**",
        f"Brand: {f.get('brand_name', 'Generic')}",
        f"Type: {f.get('food_type', 'Unknown')}",
    ]
    
    servings = f.get("servings", {}).get("serving", [])
    if not isinstance(servings, list):
        servings = [servings]
    
    if servings:
        lines.append("\nServings:")
        for s in servings[:3]:  # Show max 3 servings
            lines.append(
                f"  • {s.get('serving_description', 'N/A')}: "
                f"{s.get('calories', '?')} kcal, "
                f"P {s.get('protein', '?')}g, "
                f"C {s.get('carbohydrate', '?')}g, "
                f"F {s.get('fat', '?')}g"
            )
    
    return "\n".join(lines)


def format_search_results(results: dict) -> str:
    """Format search results for display."""
    foods = results.get("foods", {})
    food_list = foods.get("food", [])
    if not isinstance(food_list, list):
        food_list = [food_list]
    
    total = foods.get("total_results", len(food_list))
    lines = [f"Found {total} results:\n"]
    
    for f in food_list[:10]:  # Show max 10
        desc = f.get('food_description', '')[:60]
        brand = f" ({f.get('brand_name')})" if f.get('brand_name') else ''
        lines.append(
            f"• [{f.get('food_id')}] {f.get('food_name', 'Unknown')}{brand}"
            f"\n  {desc}..."
        )
    
    return "\n".join(lines)


# ==================== CLI ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FatSecret API CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Search command
    search_p = subparsers.add_parser("search", help="Search foods")
    search_p.add_argument("query", help="Search term")
    search_p.add_argument("--page", type=int, default=0)
    search_p.add_argument("--max", type=int, default=10)
    search_p.add_argument("--json", action="store_true", help="Output raw JSON")
    
    # Get food command
    get_p = subparsers.add_parser("get", help="Get food details")
    get_p.add_argument("food_id", type=int, help="Food ID")
    get_p.add_argument("--json", action="store_true")
    
    # Barcode command
    barcode_p = subparsers.add_parser("barcode", help="Lookup by barcode")
    barcode_p.add_argument("barcode", help="UPC/EAN barcode")
    barcode_p.add_argument("--json", action="store_true")
    
    # Recipe search
    recipe_p = subparsers.add_parser("recipes", help="Search recipes")
    recipe_p.add_argument("query", help="Search term")
    recipe_p.add_argument("--json", action="store_true")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        client = FatSecretClient()
        
        if args.command == "search":
            result = client.search_foods(args.query, args.page, args.max)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(format_search_results(result))
        
        elif args.command == "get":
            result = client.get_food(args.food_id)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(format_food_result(result))
        
        elif args.command == "barcode":
            result = client.find_by_barcode(args.barcode)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(format_food_result(result))
        
        elif args.command == "recipes":
            result = client.search_recipes(args.query)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                recipes = result.get("recipes", {}).get("recipe", [])
                if not isinstance(recipes, list):
                    recipes = [recipes]
                for r in recipes[:10]:
                    print(f"• [{r.get('recipe_id')}] {r.get('recipe_name')} - {r.get('recipe_description', '')[:50]}...")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
