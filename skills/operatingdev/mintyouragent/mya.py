#!/usr/bin/env python3
"""
MintYourAgent - Token Launch CLI
Single-file Python implementation. No bash, no jq, no solana-cli.

Install: pip install solders requests
Usage:  python mya.py setup
        python mya.py launch --name "Token" --symbol "TKN" --description "..." --image "url"
        python mya.py wallet balance

Version: 2.3.0

Changelog:
- 2.3.0: All flags (issues 57-100), .env support, network selection, proxy support
- 2.2.0: Security hardening (issues 17-56), type hints, retry logic, audit logging
- 2.1.0: Secure local signing, first-launch tips, AI initial-buy
"""

from __future__ import annotations

import argparse
import atexit
import base64
import codecs
import ctypes
import hashlib
import hmac
import json
import logging
import os
import re
import signal
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO, Tuple, TypeVar, Union

# Platform-specific imports
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False  # Windows compatibility (Issue #62)

# ============== CONSTANTS (Issue #46, #48, #52) ==============

class ExitCode(IntEnum):
    """Exit codes for consistent error handling (Issue #38)."""
    SUCCESS = 0
    GENERAL_ERROR = 1
    MISSING_DEPS = 2
    NO_WALLET = 3
    INVALID_INPUT = 4
    NETWORK_ERROR = 5
    API_ERROR = 6
    SECURITY_ERROR = 7
    USER_CANCELLED = 8
    TIMEOUT = 9


class Network(IntEnum):
    """Solana networks (Issue #85)."""
    MAINNET = 0
    DEVNET = 1
    TESTNET = 2


class OutputFormat(IntEnum):
    """Output formats (Issue #94)."""
    TEXT = 0
    JSON = 1
    CSV = 2
    TABLE = 3


class Constants:
    """Configuration constants (Issue #48)."""
    VERSION = "2.3.0"
    
    # File size limits
    MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_NAME_LENGTH = 32
    MAX_SYMBOL_LENGTH = 10
    
    # Network defaults
    DEFAULT_TIMEOUT = 30
    DEFAULT_RETRY_COUNT = 3
    RETRY_BACKOFF = 2
    
    # RPC endpoints (Issue #85)
    RPC_ENDPOINTS = {
        Network.MAINNET: "https://api.mainnet-beta.solana.com",
        Network.DEVNET: "https://api.devnet.solana.com",
        Network.TESTNET: "https://api.testnet.solana.com",
    }
    
    DEFAULT_API_URL = "https://www.mintyouragent.com/api"
    
    # AI initial buy
    AI_FEE_RESERVE = 0.05
    AI_BUY_PERCENTAGE = 0.15
    AI_BUY_MAX = 1.0
    AI_BUY_MIN = 0.01
    
    # Lamports per SOL
    LAMPORTS_PER_SOL = 1_000_000_000
    
    # Default priority fee (Issue #91)
    DEFAULT_PRIORITY_FEE = 0  # microlamports
    
    # User agent (Issue #99)
    USER_AGENT = f"MintYourAgent/{VERSION}"
    
    # Emoji set (Issue #75)
    EMOJI = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'money': '💰',
        'rocket': '🚀',
        'coin': '🪙',
        'link': '🔗',
        'lock': '🔐',
        'folder': '📁',
        'chart': '📊',
        'pencil': '📝',
        'bulb': '💡',
        'address': '📍',
    }


# ============== DEPENDENCY CHECK ==============

try:
    from solders.keypair import Keypair
    from solders.transaction import Transaction as SoldersTransaction
    from solders.hash import Hash
    import requests
except ImportError:
    print(f"{Constants.EMOJI['error']} Missing dependencies. Run: pip install solders requests")
    sys.exit(ExitCode.MISSING_DEPS)


# ============== GLOBAL RUNTIME CONFIG ==============

@dataclass
class RuntimeConfig:
    """Runtime configuration from CLI args (Issue #81, #82, etc)."""
    # Paths
    config_file: Optional[Path] = None
    wallet_file: Optional[Path] = None
    log_file: Optional[Path] = None
    output_file: Optional[Path] = None
    
    # Network
    api_url: str = Constants.DEFAULT_API_URL
    rpc_url: Optional[str] = None
    network: Network = Network.MAINNET
    proxy: Optional[str] = None
    user_agent: str = Constants.USER_AGENT
    
    # Behavior
    timeout: int = Constants.DEFAULT_TIMEOUT
    retry_count: int = Constants.DEFAULT_RETRY_COUNT
    priority_fee: int = Constants.DEFAULT_PRIORITY_FEE
    skip_balance_check: bool = False
    
    # Output
    format: OutputFormat = OutputFormat.TEXT
    quiet: bool = False
    debug: bool = False
    verbose: bool = False
    no_color: bool = False
    no_emoji: bool = False
    timestamps: bool = False
    
    # Request tracing (Issue #73, #74)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


# Global runtime config
_runtime: RuntimeConfig = RuntimeConfig()


def get_runtime() -> RuntimeConfig:
    """Get current runtime config."""
    return _runtime


def set_runtime(config: RuntimeConfig) -> None:
    """Set runtime config."""
    global _runtime
    _runtime = config


# ============== .ENV SUPPORT (Issue #67) ==============

def load_dotenv(path: Optional[Path] = None) -> Dict[str, str]:
    """Load .env file (Issue #67)."""
    env_vars: Dict[str, str] = {}
    
    # Search paths
    search_paths = []
    if path:
        search_paths.append(path)
    search_paths.extend([
        Path.cwd() / ".env",
        Path.home() / ".mintyouragent" / ".env",
    ])
    
    for env_path in search_paths:
        if env_path.exists():
            try:
                # Handle BOM (Issue #61)
                with open(env_path, 'r', encoding='utf-8-sig') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, _, value = line.partition('=')
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            env_vars[key] = value
                            if key not in os.environ:
                                os.environ[key] = value
                break
            except (OSError, UnicodeDecodeError):
                continue
    
    return env_vars


# ============== PATHS ==============

def get_data_dir() -> Path:
    """Get data directory."""
    return Path.home() / ".mintyouragent"


def get_wallet_file() -> Path:
    """Get wallet file path."""
    rt = get_runtime()
    if rt.wallet_file:
        return rt.wallet_file
    return get_data_dir() / "wallet.json"


def get_config_file() -> Path:
    """Get config file path."""
    rt = get_runtime()
    if rt.config_file:
        return rt.config_file
    return get_data_dir() / "config.json"


def get_seed_file() -> Path:
    """Get seed file path."""
    return get_data_dir() / "SEED_PHRASE.txt"


def get_audit_log_file() -> Path:
    """Get audit log file path."""
    rt = get_runtime()
    if rt.log_file:
        return rt.log_file
    return get_data_dir() / "audit.log"


def get_rpc_url() -> str:
    """Get RPC URL based on network selection (Issue #84, #85)."""
    rt = get_runtime()
    if rt.rpc_url:
        return rt.rpc_url
    env_rpc = os.environ.get("HELIUS_RPC") or os.environ.get("SOLANA_RPC_URL")
    if env_rpc:
        return env_rpc
    return Constants.RPC_ENDPOINTS[rt.network]


def get_api_url() -> str:
    """Get API URL."""
    rt = get_runtime()
    return os.environ.get("MYA_API_URL", rt.api_url)


def get_ssl_verify() -> bool:
    """Get SSL verification setting."""
    return os.environ.get("MYA_SSL_VERIFY", "true").lower() != "false"


def get_api_key() -> str:
    """Get API key."""
    return os.environ.get("MYA_API_KEY", "")


# ============== LOGGING (Issue #32, #39, #69, #97) ==============

_logger: Optional[logging.Logger] = None


def setup_logging() -> logging.Logger:
    """Setup logging with levels (Issue #69)."""
    global _logger
    if _logger:
        return _logger
    
    rt = get_runtime()
    logger = logging.getLogger("mintyouragent")
    logger.handlers.clear()
    
    if rt.debug:
        logger.setLevel(logging.DEBUG)
    elif rt.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)
    
    # Console handler (unless quiet)
    if not rt.quiet:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG if rt.debug else logging.INFO)
        fmt = "%(asctime)s " if rt.timestamps else ""
        fmt += "[%(levelname)s] %(message)s" if rt.debug else "%(message)s"
        console.setFormatter(logging.Formatter(fmt))
        logger.addHandler(console)
    
    # File handler
    try:
        ensure_data_dir()
        log_path = get_audit_log_file()
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(correlation_id)s] %(message)s"
        ))
        logger.addHandler(file_handler)
    except (OSError, IOError):
        pass
    
    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    """Get or create logger."""
    global _logger
    if not _logger:
        _logger = setup_logging()
    return _logger


class CorrelationAdapter(logging.LoggerAdapter):
    """Add correlation ID to log messages (Issue #73)."""
    
    def process(self, msg: str, kwargs: Any) -> Tuple[str, Any]:
        rt = get_runtime()
        kwargs.setdefault('extra', {})
        kwargs['extra']['correlation_id'] = rt.correlation_id
        return msg, kwargs


def log_with_trace(level: int, msg: str, **kwargs: Any) -> None:
    """Log with request tracing (Issue #74)."""
    logger = get_logger()
    adapter = CorrelationAdapter(logger, {})
    adapter.log(level, msg, **kwargs)


# ============== OUTPUT (Issue #40, #41, #50, #51, #75, #78, #94, #95, #96) ==============

class Output:
    """Output formatting with all options."""
    
    COLORS = {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'bold': '\033[1m',
        'reset': '\033[0m',
    }
    
    @classmethod
    def _should_color(cls) -> bool:
        rt = get_runtime()
        return not rt.no_color and rt.format == OutputFormat.TEXT and sys.stdout.isatty()
    
    @classmethod
    def _should_emoji(cls) -> bool:
        rt = get_runtime()
        return not rt.no_emoji and rt.format == OutputFormat.TEXT
    
    @classmethod
    def _prefix_timestamp(cls) -> str:
        rt = get_runtime()
        if rt.timestamps:
            return f"[{datetime.now().strftime('%H:%M:%S')}] "
        return ""
    
    @classmethod
    def _get_emoji(cls, key: str) -> str:
        if cls._should_emoji():
            return Constants.EMOJI.get(key, '')
        return ''
    
    @classmethod
    def color(cls, text: str, code: str) -> str:
        """Apply ANSI color."""
        if not cls._should_color():
            return text
        return f"{cls.COLORS.get(code, '')}{text}{cls.COLORS['reset']}"
    
    @classmethod
    def _is_quiet(cls) -> bool:
        return get_runtime().quiet
    
    @classmethod
    def success(cls, msg: str) -> None:
        if cls._is_quiet():
            return
        emoji = cls._get_emoji('success')
        prefix = cls._prefix_timestamp()
        print(cls.color(f"{prefix}{emoji} {msg}" if emoji else f"{prefix}{msg}", 'green'))
    
    @classmethod
    def error(cls, msg: str) -> None:
        # Errors always print, even in quiet mode
        emoji = cls._get_emoji('error')
        prefix = cls._prefix_timestamp()
        print(cls.color(f"{prefix}{emoji} {msg}" if emoji else f"{prefix}ERROR: {msg}", 'red'), file=sys.stderr)
    
    @classmethod
    def warning(cls, msg: str) -> None:
        if cls._is_quiet():
            return
        emoji = cls._get_emoji('warning')
        prefix = cls._prefix_timestamp()
        print(cls.color(f"{prefix}{emoji}  {msg}" if emoji else f"{prefix}WARNING: {msg}", 'yellow'))
    
    @classmethod
    def info(cls, msg: str) -> None:
        if cls._is_quiet():
            return
        emoji = cls._get_emoji('info')
        prefix = cls._prefix_timestamp()
        print(f"{prefix}{emoji}  {msg}" if emoji else f"{prefix}{msg}")
    
    @classmethod
    def debug(cls, msg: str) -> None:
        rt = get_runtime()
        if rt.debug and not cls._is_quiet():
            prefix = cls._prefix_timestamp()
            print(cls.color(f"{prefix}[DEBUG] {msg}", 'cyan'))
    
    @classmethod
    def json_output(cls, data: Dict[str, Any]) -> None:
        """Output as JSON (Issue #51, #64)."""
        rt = get_runtime()
        output = json.dumps(data, indent=2, sort_keys=True, default=str)
        if rt.output_file:
            with open(rt.output_file, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output)
    
    @classmethod
    def csv_output(cls, headers: List[str], rows: List[List[Any]]) -> None:
        """Output as CSV (Issue #94)."""
        rt = get_runtime()
        import csv
        import io
        
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(headers)
        writer.writerows(rows)
        
        output = buffer.getvalue()
        if rt.output_file:
            with open(rt.output_file, 'w', encoding='utf-8', newline='') as f:
                f.write(output)
        else:
            print(output)
    
    @classmethod
    def table_output(cls, headers: List[str], rows: List[List[Any]]) -> None:
        """Output as table (Issue #94)."""
        if not rows:
            return
        
        # Calculate column widths
        widths = [len(str(h)) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))
        
        # Print header
        header_line = " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
        print(header_line)
        print("-" * len(header_line))
        
        # Print rows
        for row in rows:
            print(" | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)))
    
    @classmethod
    def formatted_output(cls, data: Dict[str, Any], headers: Optional[List[str]] = None) -> None:
        """Output in configured format (Issue #94)."""
        rt = get_runtime()
        
        if rt.format == OutputFormat.JSON:
            cls.json_output(data)
        elif rt.format == OutputFormat.CSV and headers:
            rows = [[data.get(h, '') for h in headers]]
            cls.csv_output(headers, rows)
        elif rt.format == OutputFormat.TABLE and headers:
            rows = [[data.get(h, '') for h in headers]]
            cls.table_output(headers, rows)
        else:
            # Default text output
            for key, value in data.items():
                print(f"{key}: {value}")


class Spinner:
    """Threaded spinner."""
    
    FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, msg: str):
        self.msg = msg
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
    
    def _spin(self) -> None:
        i = 0
        rt = get_runtime()
        while not self._stop.is_set():
            if not rt.no_color and not rt.quiet and rt.format == OutputFormat.TEXT:
                frame = self.FRAMES[i % len(self.FRAMES)] if not rt.no_emoji else "..."
                print(f"\r{frame} {self.msg}", end='', flush=True)
            i += 1
            self._stop.wait(0.1)
    
    def __enter__(self) -> Spinner:
        rt = get_runtime()
        if rt.quiet or rt.format != OutputFormat.TEXT:
            return self
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self
    
    def __exit__(self, *args: Any) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=0.5)
        rt = get_runtime()
        if not rt.quiet and rt.format == OutputFormat.TEXT:
            check = Constants.EMOJI['success'] if not rt.no_emoji else "[OK]"
            print(f"\r{check} {self.msg}   ")


# ============== SECURITY HELPERS ==============

def ensure_data_dir() -> None:
    """Ensure data directory exists with secure permissions."""
    data_dir = get_data_dir()
    if not data_dir.exists():
        data_dir.mkdir(mode=0o700, parents=True)
    else:
        current_mode = data_dir.stat().st_mode
        if current_mode & 0o077:
            os.chmod(data_dir, 0o700)


def verify_file_permissions(filepath: Path) -> bool:
    """Verify file has secure permissions (600)."""
    if not filepath.exists():
        return True
    current_mode = filepath.stat().st_mode
    if current_mode & 0o077:
        os.chmod(filepath, 0o600)
        return False
    return True


def secure_delete(filepath: Path) -> None:
    """Securely delete a file (Issue #19)."""
    if not filepath.exists():
        return
    try:
        size = filepath.stat().st_size
        with open(filepath, 'wb') as f:
            f.write(os.urandom(size))
            f.flush()
            os.fsync(f.fileno())
        filepath.unlink()
    except (OSError, IOError):
        try:
            filepath.unlink()
        except:
            pass


def clear_sensitive_memory(data: bytearray) -> None:
    """Clear sensitive data from memory (Issue #18)."""
    try:
        ctypes.memset(ctypes.addressof((ctypes.c_char * len(data)).from_buffer(data)), 0, len(data))
    except (TypeError, ValueError):
        pass


def acquire_file_lock(filepath: Path) -> Optional[int]:
    """Acquire exclusive file lock (Issue #20)."""
    if not HAS_FCNTL:
        return None  # Windows - skip locking
    try:
        fd = os.open(str(filepath), os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except (OSError, IOError):
        return None


def release_file_lock(fd: Optional[int]) -> None:
    """Release file lock."""
    if fd is None or not HAS_FCNTL:
        return
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    except (OSError, IOError):
        pass


def sanitize_input(text: str) -> str:
    """Sanitize user input (Issue #57)."""
    if not text:
        return ""
    # Remove control characters except newlines
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Limit length
    return text[:10000]


def validate_path_safety(filepath: str) -> Path:
    """Validate path is safe - no traversal or symlinks (Issue #58, #59)."""
    path = Path(filepath)
    
    # Resolve to absolute path
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid path: {e}")
    
    # Check for path traversal
    if ".." in path.parts:
        raise ValueError("Path traversal not allowed")
    
    # Check for symlinks (Issue #59)
    if path.exists() and path.is_symlink():
        raise ValueError("Symlinks not allowed for security")
    
    return resolved


# ============== BASE58 ==============

B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58_encode(data: bytes) -> str:
    """Encode bytes to base58."""
    num = int.from_bytes(data, 'big')
    result = ''
    while num > 0:
        num, rem = divmod(num, 58)
        result = B58_ALPHABET[rem] + result
    for byte in data:
        if byte == 0:
            result = '1' + result
        else:
            break
    return result or '1'


def b58_decode(s: str) -> bytes:
    """Decode base58 string with error handling (Issue #26)."""
    try:
        num = 0
        for c in s:
            if c not in B58_ALPHABET:
                raise ValueError(f"Invalid base58 character: {c}")
            num = num * 58 + B58_ALPHABET.index(c)
        if num == 0:
            result = b''
        else:
            result = num.to_bytes((num.bit_length() + 7) // 8, 'big')
        pad = len(s) - len(s.lstrip('1'))
        return b'\x00' * pad + result
    except (ValueError, OverflowError) as e:
        raise ValueError(f"Invalid base58 string") from e


# ============== WALLET OPERATIONS ==============

def compute_wallet_checksum(data: bytes) -> str:
    """Compute checksum for wallet integrity (Issue #30)."""
    return hashlib.sha256(data).hexdigest()[:8]


def load_wallet() -> Keypair:
    """Load wallet from file."""
    ensure_data_dir()
    wallet_file = get_wallet_file()
    
    if not wallet_file.exists():
        # Check legacy location
        legacy_file = Path(__file__).parent.resolve() / "wallet.json"
        if legacy_file.exists():
            Output.warning("Migrating wallet from skill directory")
            import shutil
            shutil.move(str(legacy_file), str(wallet_file))
            os.chmod(wallet_file, 0o600)
        else:
            Output.error("No wallet found. Run: python mya.py setup")
            sys.exit(ExitCode.NO_WALLET)
    
    was_secure = verify_file_permissions(wallet_file)
    if not was_secure:
        Output.warning("Fixed insecure wallet permissions")
    
    try:
        # Handle encoding (Issue #60, #61)
        with open(wallet_file, 'r', encoding='utf-8-sig') as f:
            wallet_data = json.load(f)
        
        if isinstance(wallet_data, dict):
            keypair_bytes = bytes(wallet_data["bytes"])
            stored_checksum = wallet_data.get("checksum", "")
            if stored_checksum:
                actual_checksum = compute_wallet_checksum(keypair_bytes)
                if stored_checksum != actual_checksum:
                    Output.error("Wallet integrity check failed")
                    log_with_trace(logging.ERROR, "Wallet checksum mismatch")
                    sys.exit(ExitCode.SECURITY_ERROR)
        else:
            keypair_bytes = bytes(wallet_data)
        
        return Keypair.from_bytes(keypair_bytes)
    
    except json.JSONDecodeError:
        # Issue #21, #70 - don't expose paths or stack traces
        Output.error("Corrupted wallet file")
        log_with_trace(logging.ERROR, "Wallet JSON decode error")
        sys.exit(ExitCode.GENERAL_ERROR)
    except Exception as e:
        Output.error("Failed to load wallet")
        if get_runtime().debug:
            Output.debug(f"Exception: {type(e).__name__}: {e}")
        log_with_trace(logging.ERROR, f"Wallet load failed: {e}")
        sys.exit(ExitCode.GENERAL_ERROR)


def save_wallet(keypair: Keypair) -> None:
    """Save wallet to file with checksum."""
    ensure_data_dir()
    wallet_file = get_wallet_file()
    
    keypair_bytes = bytes(keypair)
    checksum = compute_wallet_checksum(keypair_bytes)
    
    wallet_data = {
        "bytes": list(keypair_bytes),
        "checksum": checksum,
        "created": datetime.utcnow().isoformat() + "Z",
        "version": Constants.VERSION,
    }
    
    lock_file = wallet_file.with_suffix('.lock')
    lock_fd = acquire_file_lock(lock_file)
    
    try:
        temp_file = wallet_file.with_suffix('.tmp')
        # Explicit encoding (Issue #60)
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(wallet_data, f, indent=2)
        os.chmod(temp_file, 0o600)
        temp_file.rename(wallet_file)
        log_with_trace(logging.INFO, f"Wallet saved: {str(keypair.pubkey())[:8]}...")
    finally:
        release_file_lock(lock_fd)
        if lock_file.exists():
            try:
                lock_file.unlink()
            except:
                pass


# ============== CONFIG ==============

@dataclass
class AppConfig:
    """Application configuration."""
    autonomous: bool = False
    log_file: Optional[str] = None
    json_output: bool = False
    network: str = "mainnet"
    
    @classmethod
    def load(cls, path: Path) -> AppConfig:
        """Load config with validation (Issue #29, #65)."""
        if not path.exists():
            return cls()
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            
            # Schema validation (Issue #65)
            validated = cls(
                autonomous=bool(data.get("autonomous", False)),
                log_file=data.get("log_file") if isinstance(data.get("log_file"), str) else None,
                json_output=bool(data.get("json_output", False)),
                network=str(data.get("network", "mainnet")) if data.get("network") in ["mainnet", "devnet", "testnet"] else "mainnet",
            )
            return validated
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            log_with_trace(logging.WARNING, f"Config load error: {e}")
            return cls()
    
    def save(self, path: Path) -> None:
        """Save config atomically."""
        ensure_data_dir()
        temp_file = path.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump({
                "autonomous": self.autonomous,
                "log_file": self.log_file,
                "json_output": self.json_output,
                "network": self.network,
            }, f, indent=2)
        temp_file.rename(path)


# ============== API HELPERS ==============

def sign_request(payload: dict, timestamp: int) -> str:
    """Generate HMAC signature for API request."""
    api_key = get_api_key()
    if not api_key:
        return ""
    message = f"{timestamp}:{json.dumps(payload, sort_keys=True)}"
    return hmac.new(api_key.encode(), message.encode(), hashlib.sha256).hexdigest()


def get_request_headers() -> Dict[str, str]:
    """Get common request headers (Issue #99)."""
    rt = get_runtime()
    return {
        "Content-Type": "application/json",
        "User-Agent": rt.user_agent,
        "X-Correlation-ID": rt.correlation_id,
    }


def api_request_with_retry(
    method: str,
    url: str,
    **kwargs: Any
) -> requests.Response:
    """Make API request with retry logic (Issue #36, #86, #87, #98)."""
    rt = get_runtime()
    last_error: Optional[Exception] = None
    
    kwargs.setdefault('timeout', rt.timeout)
    kwargs.setdefault('verify', get_ssl_verify())
    kwargs.setdefault('headers', {}).update(get_request_headers())
    
    # Proxy support (Issue #98)
    if rt.proxy:
        kwargs['proxies'] = {'http': rt.proxy, 'https': rt.proxy}
    
    for attempt in range(rt.retry_count):
        try:
            log_with_trace(logging.DEBUG, f"API request: {method} {url} (attempt {attempt + 1})")
            
            if method.upper() == 'GET':
                resp = requests.get(url, **kwargs)
            else:
                resp = requests.post(url, **kwargs)
            
            resp.raise_for_status()
            log_with_trace(logging.DEBUG, f"API response: {resp.status_code}")
            return resp
            
        except requests.exceptions.SSLError:
            raise
        except requests.exceptions.Timeout as e:
            last_error = e
            log_with_trace(logging.WARNING, f"Request timeout (attempt {attempt + 1})")
        except requests.exceptions.ConnectionError as e:
            last_error = e
            log_with_trace(logging.WARNING, f"Connection error (attempt {attempt + 1})")
        except requests.exceptions.HTTPError as e:
            if e.response is not None and 400 <= e.response.status_code < 500:
                raise
            last_error = e
            log_with_trace(logging.WARNING, f"HTTP error (attempt {attempt + 1})")
        
        if attempt < rt.retry_count - 1:
            sleep_time = Constants.RETRY_BACKOFF ** attempt
            time.sleep(sleep_time)
    
    raise last_error or requests.exceptions.RequestException("Request failed")


@dataclass
class APIResponse:
    """Structured API response (Issue #35, #51)."""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    code: Optional[str] = None
    hint: Optional[str] = None


def parse_api_response(resp: requests.Response) -> APIResponse:
    """Parse API response (Issue #35)."""
    try:
        data = resp.json()
        return APIResponse(
            success=data.get("success", resp.ok),
            data=data,
            error=data.get("error"),
            code=data.get("code"),
            hint=data.get("hint"),
        )
    except json.JSONDecodeError:
        return APIResponse(success=False, error="Invalid API response", code="INVALID_RESPONSE")


def verify_transaction(tx_bytes: bytes, expected_signer: str) -> bool:
    """Verify transaction before signing."""
    try:
        tx = SoldersTransaction.from_bytes(tx_bytes)
        message = tx.message
        
        if not message.recent_blockhash or message.recent_blockhash == Hash.default():
            Output.error("Transaction missing blockhash")
            return False
        
        account_keys = message.account_keys
        if not any(str(acc) == expected_signer for acc in account_keys):
            Output.error("Transaction missing expected signer")
            return False
        
        return True
    except Exception as e:
        Output.error("Transaction verification failed")
        log_with_trace(logging.ERROR, f"TX verification: {e}")
        return False


# ============== IMAGE HANDLING (Issue #47) ==============

def load_image_file(filepath: str) -> Tuple[str, str]:
    """Load and encode image file (Issue #47, #58, #59)."""
    # Validate path safety
    safe_path = validate_path_safety(filepath)
    
    if not safe_path.exists():
        raise FileNotFoundError("Image file not found")
    
    file_size = safe_path.stat().st_size
    if file_size > Constants.MAX_IMAGE_SIZE_BYTES:
        raise ValueError(f"Image too large (max {Constants.MAX_IMAGE_SIZE_BYTES // 1024 // 1024}MB)")
    
    with open(safe_path, 'rb') as f:
        img_data = f.read()
    
    ext = safe_path.suffix.lower().lstrip('.')
    mime_map = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'gif': 'image/gif', 'webp': 'image/webp'}
    mime = mime_map.get(ext, 'image/png')
    
    data_url = f"data:{mime};base64,{base64.b64encode(img_data).decode()}"
    return data_url, mime


def validate_https_url(url: str, name: str = "URL") -> None:
    """Validate URL is HTTPS (Issue #12, #16)."""
    url = sanitize_input(url)
    if not url.startswith('https://'):
        raise ValueError(f"{name} must use HTTPS")


# ============== SIGNAL HANDLERS (Issue #37) ==============

def setup_signal_handlers() -> None:
    """Setup graceful signal handling."""
    def handler(signum: int, frame: Any) -> None:
        print("\n")
        Output.warning("Interrupted by user")
        sys.exit(ExitCode.USER_CANCELLED)
    
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


# ============== COMMANDS ==============

def show_first_launch_tips() -> None:
    """Show helpful commands before first launch."""
    print("=" * 50)
    print(f"{Constants.EMOJI['info']}  BEFORE YOUR FIRST LAUNCH")
    print("=" * 50)
    print("")
    print("Useful commands:")
    print("")
    print("  python mya.py wallet balance")
    print("     Check you have enough SOL")
    print("")
    print("  python mya.py wallet check")
    print("     See your daily launch limit")
    print("")
    print("  python mya.py launch --dry-run --name ...")
    print("     Test without spending SOL")
    print("")
    print("=" * 50)


def get_initial_buy_decision(args: argparse.Namespace, balance_sol: float) -> float:
    """Determine initial buy amount based on balance."""
    if hasattr(args, 'initial_buy') and args.initial_buy and args.initial_buy > 0:
        return args.initial_buy
    
    if hasattr(args, 'ai_initial_buy') and args.ai_initial_buy:
        print(f"{Constants.EMOJI['bulb']} AI calculating initial buy...")
        print(f"   Wallet balance: {balance_sol:.4f} SOL")
        
        available = balance_sol - Constants.AI_FEE_RESERVE
        print(f"   Reserved: {Constants.AI_FEE_RESERVE} SOL")
        print(f"   Available: {available:.4f} SOL")
        
        if available < Constants.AI_BUY_MIN:
            print(f"{Constants.EMOJI['bulb']} AI decision: No initial buy (low balance)")
            return 0
        
        recommended = min(available * Constants.AI_BUY_PERCENTAGE, Constants.AI_BUY_MAX)
        recommended = max(recommended, Constants.AI_BUY_MIN)
        recommended = round(recommended, 3)
        
        print(f"   Calculation: {Constants.AI_BUY_PERCENTAGE*100:.0f}% of {available:.4f}")
        print(f"{Constants.EMOJI['bulb']} AI decision: {recommended} SOL")
        return recommended
    
    return 0


def cmd_setup(args: argparse.Namespace) -> None:
    """Generate a new wallet."""
    ensure_data_dir()
    wallet_file = get_wallet_file()
    
    if wallet_file.exists() and not args.force:
        Output.warning(f"Wallet already exists: {wallet_file}")
        print("Use --force to regenerate")
        return
    
    keypair = Keypair()
    save_wallet(keypair)
    
    address = str(keypair.pubkey())
    seed_file = get_seed_file()
    
    with open(seed_file, 'w', encoding='utf-8') as f:
        f.write(f"Wallet Address: {address}\n\n")
        f.write("Private Key (Base58):\n")
        f.write(b58_encode(bytes(keypair)) + "\n\n")
        f.write("DO NOT SHARE THIS FILE!\n")
        f.write(f"\nGenerated: {datetime.now().isoformat()}\n")
    os.chmod(seed_file, 0o600)
    
    # Clean up legacy
    legacy_seed = Path(__file__).parent.resolve() / "SEED_PHRASE.txt"
    if legacy_seed.exists():
        secure_delete(legacy_seed)
    
    log_with_trace(logging.INFO, f"Wallet created: {address}")
    
    rt = get_runtime()
    if rt.format == OutputFormat.JSON:
        Output.json_output({"success": True, "address": address, "data_dir": str(get_data_dir())})
    else:
        Output.success("Wallet created!")
        print(f"{Constants.EMOJI['address']} Address: {address}")
        print(f"{Constants.EMOJI['folder']} Data: {get_data_dir()}")
        print(f"{Constants.EMOJI['lock']} Seed: {seed_file}")
        print("")
        Output.warning("Back up SEED_PHRASE.txt!")


def cmd_wallet(args: argparse.Namespace) -> None:
    """Wallet management commands."""
    rt = get_runtime()
    
    if args.wallet_cmd == "import":
        if args.key:
            Output.warning("Passing keys via CLI is insecure (visible in ps aux)")
            key = args.key
        elif not sys.stdin.isatty():
            key = sys.stdin.read().strip()
        else:
            Output.error("Provide key with --key or pipe from file")
            return
        
        try:
            key_bytes = b58_decode(sanitize_input(key))
            keypair = Keypair.from_bytes(key_bytes)
            save_wallet(keypair)
            
            if isinstance(key, str):
                key_ba = bytearray(key.encode())
                clear_sensitive_memory(key_ba)
            
            Output.success(f"Wallet imported: {keypair.pubkey()}")
            log_with_trace(logging.INFO, f"Wallet imported: {str(keypair.pubkey())[:8]}...")
        except ValueError as e:
            Output.error("Invalid key format")
        except Exception as e:
            Output.error("Import failed")
            if rt.debug:
                Output.debug(str(e))
        return
    
    keypair = load_wallet()
    address = str(keypair.pubkey())
    
    if args.wallet_cmd == "address":
        if rt.format == OutputFormat.JSON:
            Output.json_output({"address": address})
        else:
            print(address)
    
    elif args.wallet_cmd == "balance":
        if not rt.skip_balance_check:
            try:
                with Spinner("Fetching balance..."):
                    resp = api_request_with_retry('POST', get_rpc_url(), json={
                        "jsonrpc": "2.0", "id": 1,
                        "method": "getBalance", "params": [address]
                    })
                data = resp.json()
                if "result" in data:
                    lamports = data["result"]["value"]
                    sol = lamports / Constants.LAMPORTS_PER_SOL
                    
                    if rt.format == OutputFormat.JSON:
                        Output.json_output({"address": address, "balance_sol": sol, "balance_lamports": lamports})
                    else:
                        print(f"{Constants.EMOJI['address']} Address: {address}")
                        print(f"{Constants.EMOJI['money']} Balance: {sol:.6f} SOL")
                else:
                    Output.error("Could not fetch balance")
            except requests.exceptions.SSLError:
                Output.error("SSL verification failed")
            except Exception as e:
                Output.error("Network error")
                if rt.debug:
                    Output.debug(str(e))
                print(f"{Constants.EMOJI['link']} View: https://solscan.io/account/{address}")
        else:
            print(f"{Constants.EMOJI['address']} Address: {address}")
            print("(balance check skipped)")
    
    elif args.wallet_cmd == "export":
        Output.warning("PRIVATE KEY - DO NOT SHARE!")
        print("")
        b58_key = b58_encode(bytes(keypair))
        
        if rt.format == OutputFormat.JSON:
            Output.json_output({"private_key": b58_key, "address": address})
        else:
            print("Base58 Private Key:")
            print(b58_key)
        
        log_with_trace(logging.WARNING, "Private key exported")
    
    elif args.wallet_cmd == "fund":
        if rt.format == OutputFormat.JSON:
            Output.json_output({"address": address, "explorer": f"https://solscan.io/account/{address}"})
        else:
            print(f"{Constants.EMOJI['address']} Send SOL to: {address}")
            print("")
            print("Need ~0.02 SOL per launch")
            print(f"{Constants.EMOJI['link']} View: https://solscan.io/account/{address}")
    
    elif args.wallet_cmd == "check":
        with Spinner("Checking status..."):
            try:
                resp = api_request_with_retry('GET', f"{get_api_url()}/launch", params={"agent": address})
                result = parse_api_response(resp)
                
                if result.success and "launchesRemaining" in result.data:
                    if rt.format == OutputFormat.JSON:
                        Output.json_output(result.data)
                    else:
                        print(f"Tier: {result.data.get('tier', 'free')}")
                        print(f"{Constants.EMOJI['rocket']} Launches: {result.data.get('launchesToday', 0)}/{result.data.get('launchLimit', 1)}")
                        print(f"{Constants.EMOJI['chart']} Remaining: {result.data.get('launchesRemaining', 0)}")
                else:
                    Output.error(result.error or "Could not fetch stats")
            except Exception as e:
                Output.error("Error fetching stats")
                if rt.debug:
                    Output.debug(str(e))
    
    else:
        print("Usage: python mya.py wallet <command>")
        print("")
        print("Commands:")
        print("  address   Show address")
        print("  balance   Show balance")
        print("  export    Export private key")
        print("  fund      Funding instructions")
        print("  check     Check launch limit")
        print("  import    Import wallet")


def cmd_launch(args: argparse.Namespace) -> None:
    """Launch a token."""
    rt = get_runtime()
    
    if hasattr(args, 'tips') and args.tips:
        show_first_launch_tips()
        return
    
    # Validate required fields
    errors = []
    if not args.name:
        errors.append("--name required")
    if not args.symbol:
        errors.append("--symbol required")
    if not args.description:
        errors.append("--description required")
    if not args.image and not args.image_file:
        errors.append("--image or --image-file required")
    
    if errors:
        Output.error("Missing fields:")
        for e in errors:
            print(f"   {e}")
        sys.exit(ExitCode.INVALID_INPUT)
    
    # Sanitize inputs (Issue #57)
    name = sanitize_input(args.name)
    symbol = sanitize_input(args.symbol)
    description = sanitize_input(args.description)
    
    # Validate
    if len(symbol) > Constants.MAX_SYMBOL_LENGTH:
        Output.error(f"Symbol max {Constants.MAX_SYMBOL_LENGTH} chars")
        sys.exit(ExitCode.INVALID_INPUT)
    if not symbol.isascii() or not symbol.replace('_', '').isalnum():
        Output.error("Symbol: ASCII letters/numbers only")
        sys.exit(ExitCode.INVALID_INPUT)
    if len(name) > Constants.MAX_NAME_LENGTH:
        Output.error(f"Name max {Constants.MAX_NAME_LENGTH} chars")
        sys.exit(ExitCode.INVALID_INPUT)
    if len(description) > Constants.MAX_DESCRIPTION_LENGTH:
        Output.error(f"Description max {Constants.MAX_DESCRIPTION_LENGTH} chars")
        sys.exit(ExitCode.INVALID_INPUT)
    
    # Handle image
    try:
        if args.image_file:
            image, _ = load_image_file(args.image_file)
        else:
            validate_https_url(args.image, "Image URL")
            image = args.image
    except (FileNotFoundError, ValueError) as e:
        Output.error(str(e))
        sys.exit(ExitCode.INVALID_INPUT)
    
    # Handle banner
    banner = None
    if args.banner_file:
        try:
            banner, _ = load_image_file(args.banner_file)
        except (FileNotFoundError, ValueError) as e:
            Output.error(f"Banner: {e}")
            sys.exit(ExitCode.INVALID_INPUT)
    elif args.banner:
        try:
            validate_https_url(args.banner, "Banner URL")
            banner = args.banner
        except ValueError as e:
            Output.error(str(e))
            sys.exit(ExitCode.INVALID_INPUT)
    
    # Validate socials
    for url_name, url in [('Twitter', args.twitter), ('Telegram', args.telegram), ('Website', args.website)]:
        if url:
            try:
                validate_https_url(url, url_name)
            except ValueError as e:
                Output.error(str(e))
                sys.exit(ExitCode.INVALID_INPUT)
    
    keypair = load_wallet()
    creator_address = str(keypair.pubkey())
    
    # Dry run
    if args.dry_run:
        data = {
            "mode": "dry_run",
            "name": name,
            "symbol": symbol.upper(),
            "description": description[:50] + "...",
            "creator": creator_address,
        }
        if rt.format == OutputFormat.JSON:
            Output.json_output(data)
        else:
            print("DRY RUN:")
            for k, v in data.items():
                print(f"   {k}: {v}")
        return
    
    # Confirmation (Issue #33)
    if not args.yes and sys.stdin.isatty():
        Output.warning("This spends real SOL")
        confirm = input("Proceed? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            sys.exit(ExitCode.USER_CANCELLED)
    
    print(f"{Constants.EMOJI['rocket']} Launching {symbol.upper()}...")
    log_with_trace(logging.INFO, f"Launch: {symbol} by {creator_address[:8]}")
    
    try:
        # Check balance
        balance_sol = 0
        if not rt.skip_balance_check:
            with Spinner("Checking balance..."):
                try:
                    resp = api_request_with_retry('POST', get_rpc_url(), json={
                        "jsonrpc": "2.0", "id": 1,
                        "method": "getBalance", "params": [creator_address]
                    })
                    data = resp.json()
                    if "result" in data:
                        balance_sol = data["result"]["value"] / Constants.LAMPORTS_PER_SOL
                        print(f"   Balance: {balance_sol:.4f} SOL")
                except Exception as e:
                    Output.warning("Could not check balance")
        
        initial_buy = get_initial_buy_decision(args, balance_sol)
        if initial_buy > 0:
            print(f"   Initial buy: {initial_buy} SOL")
        
        # Prepare
        with Spinner("Preparing..."):
            prepare_payload = {
                "name": name,
                "symbol": symbol.upper(),
                "description": description,
                "image": image,
                "creatorAddress": creator_address,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            if banner:
                prepare_payload["banner"] = banner
            if args.twitter:
                prepare_payload["twitter"] = sanitize_input(args.twitter)
            if args.telegram:
                prepare_payload["telegram"] = sanitize_input(args.telegram)
            if args.website:
                prepare_payload["website"] = sanitize_input(args.website)
            if initial_buy > 0:
                prepare_payload["initialBuyAmount"] = initial_buy
            if args.slippage:
                prepare_payload["slippageBps"] = args.slippage
            if rt.priority_fee > 0:
                prepare_payload["priorityFee"] = rt.priority_fee
            
            headers = get_request_headers()
            timestamp = int(time.time())
            api_key = get_api_key()
            if api_key:
                headers["X-Timestamp"] = str(timestamp)
                headers["X-Signature"] = sign_request(prepare_payload, timestamp)
            
            resp = api_request_with_retry('POST', f"{get_api_url()}/launch/prepare",
                json=prepare_payload, headers=headers, timeout=60)
            prepare_result = parse_api_response(resp)
        
        if not prepare_result.success:
            Output.error("Prepare failed:")
            print(f"   {prepare_result.error}")
            if prepare_result.code:
                print(f"   Code: {prepare_result.code}")
            sys.exit(ExitCode.API_ERROR)
        
        # Sign
        with Spinner("Signing..."):
            tx_bytes = base64.b64decode(prepare_result.data["transaction"])
            mint_address = prepare_result.data["mintAddress"]
            
            if not verify_transaction(tx_bytes, creator_address):
                Output.error("Transaction verification failed")
                sys.exit(ExitCode.SECURITY_ERROR)
            
            tx = SoldersTransaction.from_bytes(tx_bytes)
            tx.sign([keypair], tx.message.recent_blockhash)
            signed_tx_b64 = base64.b64encode(bytes(tx)).decode()
        
        # Submit
        with Spinner("Submitting..."):
            submit_payload = {
                "signedTransaction": signed_tx_b64,
                "mintAddress": mint_address,
                "creatorAddress": creator_address,
                "metadata": {
                    "name": name,
                    "symbol": symbol.upper(),
                    "description": description,
                    "imageUrl": prepare_result.data.get("imageUrl"),
                    "twitter": args.twitter,
                    "telegram": args.telegram,
                    "website": args.website,
                }
            }
            
            resp = api_request_with_retry('POST', f"{get_api_url()}/launch/submit",
                json=submit_payload, headers=headers, timeout=120)
            result = parse_api_response(resp)
        
        if result.success:
            log_with_trace(logging.INFO, f"Launch success: {mint_address}")
            
            if rt.format == OutputFormat.JSON:
                Output.json_output({
                    "success": True,
                    "mint": result.data.get('mint'),
                    "signature": result.data.get('signature'),
                    "pump_url": result.data.get('pumpUrl'),
                    "dexscreener": result.data.get('dexscreener'),
                })
            else:
                Output.success("Token launched!")
                print(f"{Constants.EMOJI['coin']} Mint: {result.data.get('mint')}")
                print(f"{Constants.EMOJI['link']} pump.fun: {result.data.get('pumpUrl')}")
                if result.data.get('dexscreener'):
                    print(f"{Constants.EMOJI['chart']} DEX: {result.data.get('dexscreener')}")
        else:
            Output.error("Launch failed:")
            print(f"   {result.error}")
            log_with_trace(logging.ERROR, f"Launch failed: {result.error}")
            sys.exit(ExitCode.API_ERROR)
    
    except requests.exceptions.SSLError:
        Output.error("SSL verification failed")
        sys.exit(ExitCode.NETWORK_ERROR)
    except requests.exceptions.Timeout:
        Output.error("Request timed out")
        sys.exit(ExitCode.TIMEOUT)
    except requests.exceptions.ConnectionError:
        Output.error("Network error")
        sys.exit(ExitCode.NETWORK_ERROR)
    except KeyboardInterrupt:
        Output.warning("Interrupted")
        sys.exit(ExitCode.USER_CANCELLED)
    except Exception as e:
        Output.error("Error")
        if rt.debug:
            Output.debug(f"{type(e).__name__}: {e}")
        log_with_trace(logging.ERROR, f"Launch exception: {e}")
        sys.exit(ExitCode.GENERAL_ERROR)


def cmd_config(args: argparse.Namespace) -> None:
    """Manage configuration."""
    config = AppConfig.load(get_config_file())
    rt = get_runtime()
    
    if args.config_cmd == "show":
        data = {
            "autonomous": config.autonomous,
            "log_file": config.log_file,
            "network": config.network,
        }
        if rt.format == OutputFormat.JSON:
            Output.json_output(data)
        else:
            print(json.dumps(data, indent=2))
    
    elif args.config_cmd == "autonomous":
        if args.value is None:
            print(f"autonomous: {config.autonomous}")
        else:
            config.autonomous = args.value.lower() in ('true', '1', 'yes', 'on')
            config.save(get_config_file())
            Output.success(f"autonomous = {config.autonomous}")
    
    else:
        print("Usage: python mya.py config <command>")
        print("")
        print("Commands:")
        print("  show                    Show config")
        print("  autonomous [true|false] Get/set autonomous mode")


def cmd_uninstall(args: argparse.Namespace) -> None:
    """Remove files."""
    wallet_file = get_wallet_file()
    config_file = get_config_file()
    seed_file = get_seed_file()
    data_dir = get_data_dir()
    
    print("This will remove:")
    print(f"   {wallet_file}")
    print(f"   {config_file}")
    print(f"   {seed_file}")
    print("")
    
    if not args.yes:
        confirm = input("Proceed? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
    
    for f in [wallet_file, seed_file]:
        if f.exists():
            secure_delete(f)
            print(f"Removed: {f}")
    
    if config_file.exists():
        config_file.unlink()
        print(f"Removed: {config_file}")
    
    if data_dir.exists() and not any(data_dir.iterdir()):
        data_dir.rmdir()
        print(f"Removed: {data_dir}")
    
    Output.success("Cleanup complete")


def main() -> None:
    """Main entry point."""
    # Load .env first (Issue #67)
    load_dotenv()
    
    setup_signal_handlers()
    
    parser = argparse.ArgumentParser(
        description="MintYourAgent - Launch tokens on pump.fun",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Version: {Constants.VERSION}

Environment Variables:
  MYA_API_URL, MYA_API_KEY, MYA_SSL_VERIFY
  HELIUS_RPC, SOLANA_RPC_URL
        """
    )
    
    # Global options
    parser.add_argument("--version", action="version", version=f"MintYourAgent {Constants.VERSION}")
    parser.add_argument("--no-color", action="store_true", help="Disable colors")
    parser.add_argument("--no-emoji", action="store_true", help="Disable emoji (Issue #95)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--format", choices=["text", "json", "csv", "table"], default="text", help="Output format (Issue #94)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode (Issue #78)")
    parser.add_argument("--debug", action="store_true", help="Debug mode (Issue #80)")
    parser.add_argument("--timestamps", action="store_true", help="Show timestamps (Issue #96)")
    
    # Path options (Issue #81, #82, #97)
    parser.add_argument("--config-file", type=Path, help="Config file path")
    parser.add_argument("--wallet-file", type=Path, help="Wallet file path")
    parser.add_argument("--log-file", type=Path, help="Log file path")
    parser.add_argument("--output-file", "-o", type=Path, help="Output file (Issue #93)")
    
    # Network options (Issue #83, #84, #85)
    parser.add_argument("--api-url", help="API URL")
    parser.add_argument("--rpc-url", help="RPC URL")
    parser.add_argument("--network", choices=["mainnet", "devnet", "testnet"], default="mainnet", help="Network")
    parser.add_argument("--proxy", help="HTTP proxy (Issue #98)")
    parser.add_argument("--user-agent", help="User agent (Issue #99)")
    
    # Behavior options (Issue #86, #87, #91, #92)
    parser.add_argument("--timeout", type=int, default=Constants.DEFAULT_TIMEOUT, help="Request timeout")
    parser.add_argument("--retry-count", type=int, default=Constants.DEFAULT_RETRY_COUNT, help="Retry count")
    parser.add_argument("--priority-fee", type=int, default=0, help="Priority fee (microlamports)")
    parser.add_argument("--skip-balance-check", action="store_true", help="Skip balance check")
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Setup
    setup_p = subparsers.add_parser("setup", help="Create wallet")
    setup_p.add_argument("--force", action="store_true", help="Overwrite")
    
    # Wallet
    wallet_p = subparsers.add_parser("wallet", help="Wallet commands")
    wallet_p.add_argument("wallet_cmd", nargs="?", default="help",
                         choices=["address", "balance", "export", "fund", "check", "import", "help"])
    wallet_p.add_argument("--key", help="Private key (prefer stdin)")
    
    # Launch
    launch_p = subparsers.add_parser("launch", help="Launch token")
    launch_p.add_argument("--name", help="Token name")
    launch_p.add_argument("--symbol", help="Token symbol")
    launch_p.add_argument("--description", help="Description")
    launch_p.add_argument("--image", help="Image URL")
    launch_p.add_argument("--image-file", help="Image file")
    launch_p.add_argument("--banner", help="Banner URL")
    launch_p.add_argument("--banner-file", help="Banner file")
    launch_p.add_argument("--twitter", help="Twitter URL")
    launch_p.add_argument("--telegram", help="Telegram URL")
    launch_p.add_argument("--website", help="Website URL")
    launch_p.add_argument("--initial-buy", type=float, default=0, help="Initial buy (SOL)")
    launch_p.add_argument("--ai-initial-buy", action="store_true", help="AI decides buy amount")
    launch_p.add_argument("--slippage", type=int, default=100, help="Slippage (bps)")
    launch_p.add_argument("--dry-run", action="store_true", help="Test only")
    launch_p.add_argument("--tips", action="store_true", help="Show tips")
    launch_p.add_argument("-y", "--yes", action="store_true", help="Skip prompts")
    
    # Config
    config_p = subparsers.add_parser("config", help="Config commands")
    config_p.add_argument("config_cmd", nargs="?", default="show", choices=["show", "autonomous"])
    config_p.add_argument("value", nargs="?", help="Value")
    
    # Uninstall
    uninstall_p = subparsers.add_parser("uninstall", help="Remove files")
    uninstall_p.add_argument("-y", "--yes", action="store_true", help="Skip prompt")
    
    args = parser.parse_args()
    
    # Build runtime config
    format_map = {"text": OutputFormat.TEXT, "json": OutputFormat.JSON, "csv": OutputFormat.CSV, "table": OutputFormat.TABLE}
    network_map = {"mainnet": Network.MAINNET, "devnet": Network.DEVNET, "testnet": Network.TESTNET}
    
    runtime = RuntimeConfig(
        config_file=args.config_file,
        wallet_file=args.wallet_file,
        log_file=args.log_file,
        output_file=getattr(args, 'output_file', None),
        api_url=args.api_url or Constants.DEFAULT_API_URL,
        rpc_url=args.rpc_url,
        network=network_map.get(args.network, Network.MAINNET),
        proxy=args.proxy,
        user_agent=args.user_agent or Constants.USER_AGENT,
        timeout=args.timeout,
        retry_count=args.retry_count,
        priority_fee=args.priority_fee,
        skip_balance_check=args.skip_balance_check,
        format=format_map.get(args.format, OutputFormat.TEXT) if not args.json else OutputFormat.JSON,
        quiet=args.quiet,
        debug=args.debug,
        verbose=args.verbose,
        no_color=args.no_color,
        no_emoji=args.no_emoji,
        timestamps=args.timestamps,
    )
    set_runtime(runtime)
    
    # Setup logging
    setup_logging()
    
    # Route commands
    if args.command == "setup":
        cmd_setup(args)
    elif args.command == "wallet":
        cmd_wallet(args)
    elif args.command == "launch":
        cmd_launch(args)
    elif args.command == "config":
        cmd_config(args)
    elif args.command == "uninstall":
        cmd_uninstall(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
