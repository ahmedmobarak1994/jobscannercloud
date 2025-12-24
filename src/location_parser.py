"""
Location parsing and geo-filtering

Parses job location strings and determines:
- Is it remote?
- What scope? (global/region/country/restricted)
- Which countries/regions?
- Should it be allowed based on geo policy?
"""
import re
from dataclasses import dataclass
from typing import Set, Optional, Tuple
from enum import Enum


class LocationScope(Enum):
    """Remote scope classification"""
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE_UNKNOWN = "remote_unknown"
    REMOTE_GLOBAL = "remote_global"
    REMOTE_REGION = "remote_region"
    REMOTE_COUNTRY = "remote_country"
    REMOTE_RESTRICTED = "remote_restricted"


@dataclass
class LocationInfo:
    """Parsed location information"""
    is_remote: bool
    scope: LocationScope
    countries: Set[str]
    regions: Set[str]
    has_us_state: bool
    has_city_restriction: bool
    raw_norm: str

    def __str__(self):
        return f"LocationInfo(remote={self.is_remote}, scope={self.scope.value}, countries={self.countries}, regions={self.regions})"


class LocationParser:
    """Parse job location strings"""

    # US states (2-letter codes in context)
    US_STATES = {
        'wa', 'washington', 'ca', 'california', 'ny', 'new york', 'tx', 'texas',
        'fl', 'florida', 'il', 'illinois', 'pa', 'pennsylvania', 'oh', 'ohio',
        'ga', 'georgia', 'nc', 'north carolina', 'mi', 'michigan', 'nj', 'new jersey',
        'va', 'virginia', 'ma', 'massachusetts', 'az', 'arizona', 'tn', 'tennessee',
        'in', 'indiana', 'mo', 'missouri', 'md', 'maryland', 'wi', 'wisconsin',
        'co', 'colorado', 'mn', 'minnesota', 'sc', 'south carolina', 'al', 'alabama',
        'la', 'louisiana', 'ky', 'kentucky', 'or', 'oregon', 'ok', 'oklahoma',
        'ct', 'connecticut', 'ut', 'utah', 'ia', 'iowa', 'nv', 'nevada',
        'ar', 'arkansas', 'ms', 'mississippi', 'ks', 'kansas', 'nm', 'new mexico',
    }

    # US cities (major tech hubs)
    US_CITIES = {
        'seattle', 'san francisco', 'nyc', 'new york city', 'chicago', 'boston',
        'austin', 'atlanta', 'denver', 'portland', 'los angeles', 'san diego',
        'dallas', 'houston', 'miami', 'phoenix', 'philadelphia', 'pittsburgh',
        'raleigh', 'salt lake city', 'minneapolis', 'detroit', 'tampa',
    }

    # Canadian cities
    CANADIAN_CITIES = {'toronto', 'vancouver', 'montreal', 'ottawa', 'calgary', 'edmonton'}

    # Australian cities
    AUSTRALIAN_CITIES = {'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide'}

    # Country mappings
    COUNTRY_PATTERNS = {
        'united states': ['united states', 'usa', 'u.s.', 'us ', ' us,', ' us)', 'america'],
        'canada': ['canada', 'canadian'],
        'australia': ['australia', 'australian'],
        'new zealand': ['new zealand', 'nz'],
        'united kingdom': ['united kingdom', 'uk', 'u.k.', 'great britain'],
        'ireland': ['ireland', 'irish'],
        'netherlands': ['netherlands', 'dutch', 'amsterdam'],
        'germany': ['germany', 'german', 'berlin', 'munich'],
        'france': ['france', 'french', 'paris'],
        'spain': ['spain', 'spanish', 'madrid', 'barcelona'],
        'portugal': ['portugal', 'portuguese', 'lisbon'],
        'italy': ['italy', 'italian', 'rome', 'milan'],
        'sweden': ['sweden', 'swedish', 'stockholm'],
        'norway': ['norway', 'norwegian', 'oslo'],
        'denmark': ['denmark', 'danish', 'copenhagen'],
        'finland': ['finland', 'finnish', 'helsinki'],
        'poland': ['poland', 'polish', 'warsaw'],
        'belgium': ['belgium', 'belgian', 'brussels'],
        'austria': ['austria', 'austrian', 'vienna'],
        'switzerland': ['switzerland', 'swiss', 'zurich'],
        'czech republic': ['czech republic', 'czech', 'prague'],
    }

    # Region patterns
    REGION_PATTERNS = {
        'europe': ['europe', 'european'],
        'emea': ['emea'],
        'eu': [' eu ', ' eu,', ' eu)', 'european union'],
        'americas': ['americas'],
        'apac': ['apac', 'asia pacific'],
        'north america': ['north america'],
    }

    # Remote indicators
    REMOTE_POSITIVE = ['remote', 'distributed', 'work from home', 'home based', 'remote-first', 'work from anywhere']
    REMOTE_NEGATIVE = ['hybrid', 'on-site', 'onsite', 'in-office', 'office-based']

    # Restriction patterns
    RESTRICTION_PATTERNS = [
        r'remote\s*\([^)]*only\)',
        r'remote\s*\([^)]*within\)',
        r'remote\s*within',
        r'must be located in',
        r'must be based in',
        r'must reside in',
        r'only candidates located in',
        r'only within',
        r'remote\s*\([^)]*,\s*\w{2}\s*only\)',  # "Remote (Seattle, WA only)"
    ]

    # Worldwide patterns
    WORLDWIDE_PATTERNS = [
        'worldwide',
        'work from anywhere',
        'global remote',
        'remote worldwide',
        'home based - worldwide',
        'home based worldwide',
        'remote (global)',
        'remote global'
    ]

    def parse_location(self, raw: str, content: str = "") -> LocationInfo:
        """
        Parse location string and return structured info

        Args:
            raw: Raw location string from job posting
            content: Optional job description for additional context

        Returns:
            LocationInfo with parsed details
        """
        # Normalize
        text = f"{raw.lower()} {content.lower()}"
        raw_norm = raw.lower().strip()

        # Check if remote
        is_remote = any(p in text for p in self.REMOTE_POSITIVE)
        has_hybrid = any(p in text for p in self.REMOTE_NEGATIVE)

        if has_hybrid and not is_remote:
            return LocationInfo(
                is_remote=False,
                scope=LocationScope.HYBRID,
                countries=set(),
                regions=set(),
                has_us_state=False,
                has_city_restriction=False,
                raw_norm=raw_norm
            )

        if not is_remote:
            return LocationInfo(
                is_remote=False,
                scope=LocationScope.ONSITE,
                countries=set(),
                regions=set(),
                has_us_state=False,
                has_city_restriction=False,
                raw_norm=raw_norm
            )

        # It's remote - determine scope
        countries = self._detect_countries(text)
        regions = self._detect_regions(text)
        has_us_state = self._has_us_state(text)
        has_city_restriction = self._has_city_restriction(text)
        has_restriction = self._has_restriction_pattern(text)
        is_worldwide = any(p in text for p in self.WORLDWIDE_PATTERNS)

        # Determine scope
        if has_restriction or has_us_state or has_city_restriction:
            scope = LocationScope.REMOTE_RESTRICTED
        elif is_worldwide:
            scope = LocationScope.REMOTE_GLOBAL
        elif countries:
            scope = LocationScope.REMOTE_COUNTRY
        elif regions:
            scope = LocationScope.REMOTE_REGION
        else:
            scope = LocationScope.REMOTE_UNKNOWN

        return LocationInfo(
            is_remote=is_remote,
            scope=scope,
            countries=countries,
            regions=regions,
            has_us_state=has_us_state,
            has_city_restriction=has_city_restriction,
            raw_norm=raw_norm
        )

    def _detect_countries(self, text: str) -> Set[str]:
        """Detect mentioned countries"""
        countries = set()

        for country, patterns in self.COUNTRY_PATTERNS.items():
            for pattern in patterns:
                if pattern in text:
                    countries.add(country)
                    break

        return countries

    def _detect_regions(self, text: str) -> Set[str]:
        """Detect mentioned regions"""
        regions = set()

        for region, patterns in self.REGION_PATTERNS.items():
            for pattern in patterns:
                if pattern in text:
                    regions.add(region)
                    break

        return regions

    def _has_us_state(self, text: str) -> bool:
        """Check if US state mentioned"""
        # Look for state codes in context (e.g., "Seattle, WA")
        tokens = re.findall(r'\b\w+\b', text)

        for i, token in enumerate(tokens):
            if token in self.US_STATES:
                # Check context - is it after a comma/parenthesis?
                if i > 0 or i < len(tokens) - 1:
                    return True

        return False

    def _has_city_restriction(self, text: str) -> bool:
        """Check if restricted to specific cities"""
        # Multiple US cities = restriction
        us_city_count = sum(1 for city in self.US_CITIES if city in text)
        if us_city_count >= 2:
            return True

        # Canadian cities
        if any(city in text for city in self.CANADIAN_CITIES):
            return True

        # Australian cities
        if any(city in text for city in self.AUSTRALIAN_CITIES):
            return True

        return False

    def _has_restriction_pattern(self, text: str) -> bool:
        """Check for restriction patterns"""
        for pattern in self.RESTRICTION_PATTERNS:
            if re.search(pattern, text):
                return True
        return False


class GeoFilter:
    """Apply geo-policy to parsed locations"""

    def __init__(self, config: dict):
        self.config = config
        self.parser = LocationParser()

        # Policy
        self.allowed_regions = set(r.lower() for r in config.get('allowed_regions', []))
        self.blocked_countries = set(c.lower() for c in config.get('blocked_countries', []))
        self.allow_worldwide_remote = config.get('allow_worldwide_remote', False)
        self.allow_unknown_remote = config.get('allow_unknown_remote', False)

        # EU countries (auto-allow)
        self.eu_countries = {
            'netherlands', 'germany', 'france', 'spain', 'portugal', 'italy',
            'belgium', 'austria', 'poland', 'sweden', 'denmark', 'finland',
            'ireland', 'czech republic', 'united kingdom'
        }

    def check_location(self, raw_location: str, content: str = "") -> Tuple[bool, str, LocationInfo]:
        """
        Check if location passes geo policy

        Returns:
            (passes, reason, location_info)
        """
        loc = self.parser.parse_location(raw_location, content)

        # Not remote? Block if require_remote
        if not loc.is_remote:
            if loc.scope == LocationScope.HYBRID:
                return False, "hybrid (not fully remote)", loc
            return False, "not remote", loc

        # Remote restricted (US state, specific cities, "only" patterns)
        if loc.scope == LocationScope.REMOTE_RESTRICTED:
            return False, "location restriction detected (city/state/only pattern)", loc

        # Remote country-specific (STRICT: most single-country remote = residency requirement!)
        if loc.scope == LocationScope.REMOTE_COUNTRY:
            # Block if any blocked country
            if any(c in self.blocked_countries for c in loc.countries):
                return False, f"blocked country: {loc.countries}", loc

            # CRITICAL: Single country (e.g., "Remote - Poland") usually means residency required
            # Only allow if it's in a small whitelist OR if location explicitly says "EMEA/EU"
            if len(loc.countries) == 1:
                single_country = list(loc.countries)[0]

                # Check if location text ALSO mentions EMEA/EU/Europe (then it's broad)
                location_lower = raw_location.lower()
                if any(r in location_lower for r in ['emea', 'europe', 'european', ' eu ']):
                    return True, f"EU country + EMEA/EU context: {single_country}", loc

                # Otherwise: single-country remote = likely residency requirement = BLOCK
                return False, f"single-country remote (residency likely required): {single_country}", loc

            # Multiple EU countries = probably OK
            if any(c in self.eu_countries for c in loc.countries):
                return True, f"multi-country EU remote: {loc.countries}", loc

            # Unknown multi-country - block by default
            return False, f"unknown countries: {loc.countries}", loc

        # Remote region (EMEA, Europe, EU) - ALLOW
        if loc.scope == LocationScope.REMOTE_REGION:
            if any(r in self.allowed_regions for r in loc.regions):
                return True, f"allowed region: {loc.regions}", loc
            return False, f"region not allowed: {loc.regions}", loc

        # Remote global/worldwide - ALLOW (this is true WFA)
        if loc.scope == LocationScope.REMOTE_GLOBAL:
            if self.allow_worldwide_remote:
                return True, "worldwide remote (work from anywhere)", loc
            return False, "worldwide remote (blocked by policy)", loc

        # Remote unknown (just says "Remote") - BLOCK (be strict!)
        if loc.scope == LocationScope.REMOTE_UNKNOWN:
            return False, "ambiguous remote (no region specified)", loc

        # Fallback
        return False, f"unhandled scope: {loc.scope}", loc

