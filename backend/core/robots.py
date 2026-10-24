# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""robots.txt compliance for the crawler: fetching, parsing and pacing.

robots.txt that is missing or unreachable allows every URL, as is standard
for client errors (RFC 9309, section 2.3.1.3). The file is requested with
the crawler's real User-Agent header, parsed with urllib.robotparser, and
the rules are cached per host for the whole crawl.
"""

import asyncio
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import aiohttp

_ROBOTS_PATH = '/robots.txt'
# An unresponsive host must not stall the start of the scan.
_ROBOTS_TIMEOUT_SECONDS = 10.0
# Product token of this crawler. When a robots.txt group names it, that
# group is the most specific one applying to us (RFC 9309, section 2.2.2)
# and governs, instead of the Mozilla/5.0 compatibility token.
_PRODUCT_TOKEN = 'SEO-Prism'

HostKey = Tuple[str, str, int]


def host_key(url: str) -> HostKey:
    """(scheme, hostname, effective port) identifying the host of a URL."""
    parsed = urlparse(url)
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    return (parsed.scheme, (parsed.hostname or '').lower(), port)


def _robots_url(key: HostKey) -> str:
    scheme, hostname, port = key
    host = f'[{hostname}]' if ':' in hostname else hostname
    default_port = 443 if scheme == 'https' else 80
    if port == default_port:
        return f'{scheme}://{host}/robots.txt'
    return f'{scheme}://{host}:{port}/robots.txt'


class RobotRules:
    """Verdicts of one host's robots.txt for the crawler's user agent.

    When the parser is None (robots.txt missing or unreachable) every URL
    is allowed and no pacing applies.
    """

    def __init__(self, parser: Optional[RobotFileParser], user_agent: str,
                 host: HostKey, agents: Optional[Tuple[str, ...]] = None):
        self.host = host
        self._parser = parser
        self._agents = agents if agents is not None else (user_agent,)

    @staticmethod
    def _governing_agents(text: str, user_agent: str) -> Tuple[str, ...]:
        """Agents to evaluate: the product token when the file names us."""
        for line in text.splitlines():
            line = line.split('#', 1)[0].strip()
            field, sep, value = line.partition(':')
            if not sep or field.strip().lower() != 'user-agent':
                continue
            if _PRODUCT_TOKEN.lower() in value.strip().lower():
                return (_PRODUCT_TOKEN,)
        return (user_agent,)

    @classmethod
    async def load(cls, session: aiohttp.ClientSession, robots_url: str,
                   user_agent: str, host: HostKey) -> 'RobotRules':
        """Fetch and parse one host's robots.txt; failures allow everything."""
        try:
            async with session.get(
                robots_url,
                headers={'User-Agent': user_agent},
                timeout=aiohttp.ClientTimeout(total=_ROBOTS_TIMEOUT_SECONDS),
            ) as response:
                if response.status != 200:
                    return cls(None, user_agent, host)
                text = await response.text()
        except Exception:
            return cls(None, user_agent, host)

        parser = RobotFileParser(robots_url)
        parser.parse(text.splitlines())
        return cls(parser, user_agent, host,
                   cls._governing_agents(text, user_agent))

    def can_fetch(self, url: str) -> bool:
        if self._parser is None:
            return True
        return all(self._parser.can_fetch(agent, url) for agent in self._agents)

    def _rate_interval(self, agent: str) -> float:
        rate = self._parser.request_rate(agent)
        if rate and rate.requests > 0 and rate.seconds > 0:
            return rate.seconds / rate.requests
        return 0.0

    def delay_for(self, url: str) -> Optional[float]:
        """Minimum seconds between requests to `url`'s host, or None.

        Crawl-delay and Request-rate are combined taking the most
        restrictive. None when the URL belongs to another host or this
        host defines no pause.
        """
        if self._parser is None or host_key(url) != self.host:
            return None
        delay = max((self._parser.crawl_delay(agent) or 0.0
                     for agent in self._agents), default=0.0)
        rate = max((self._rate_interval(agent) for agent in self._agents),
                   default=0.0)
        return max(delay, rate) or None


class RobotsCache:
    """Loads robots.txt once per host and caches the rules for the crawl."""

    def __init__(self, session: aiohttp.ClientSession, user_agent: str):
        self._session = session
        self._user_agent = user_agent
        self._rules: Dict[HostKey, RobotRules] = {}
        self._locks: Dict[HostKey, asyncio.Lock] = {}

    async def rules_for(self, url: str) -> RobotRules:
        key = host_key(url)
        cached = self._rules.get(key)
        if cached is not None:
            return cached
        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            if key not in self._rules:
                self._rules[key] = await RobotRules.load(
                    self._session, _robots_url(key), self._user_agent, key)
        return self._rules[key]
