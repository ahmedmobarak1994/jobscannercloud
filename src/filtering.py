"""
Multi-stage filtering with explainability
"""
from typing import Dict, List, Tuple, Optional, Set
import re
from dataclasses import dataclass, field


@dataclass
class FilterResult:
    """Result of filtering a job"""
    passed: bool
    score: int = 0
    drop_reason: Optional[str] = None
    gate_results: Dict[str, bool] = field(default_factory=dict)
    keyword_matches: Dict[str, List[str]] = field(default_factory=dict)
    scoring_breakdown: Dict[str, int] = field(default_factory=dict)


class JobFilter:
    """Multi-stage job filtering with explainability"""

    def __init__(self, config: dict):
        self.config = config

        # Remote patterns
        self.remote_positive = [p.lower() for p in config.get("remote_positive", [])]
        self.remote_negative = [p.lower() for p in config.get("remote_negative", [])]
        self.remote_anywhere = [p.lower() for p in config.get("remote_anywhere_patterns", [])]

        # Region filters
        self.allowed_regions = [r.lower() for r in config.get("allowed_regions", [])]
        self.blocked_regions = [r.lower() for r in config.get("blocked_regions", [])]

        # Title filters
        self.title_allow_patterns = [re.compile(p, re.IGNORECASE) for p in config.get("title_allow_regex_any", [])]
        self.title_block_patterns = [re.compile(p, re.IGNORECASE) for p in config.get("title_block_regex_any", [])]

        # Stack groups
        self.stack_groups = config.get("stack_groups", {})
        self.min_groups_matched = config.get("min_stack_groups", 2)

        # Scoring
        self.include_keywords = config.get("include_keywords", {})
        self.title_bonus = config.get("title_bonus", {})
        self.min_score = config.get("min_score", 10)

    def filter_job(self, job, explain: bool = False) -> FilterResult:
        """Run full filtering pipeline"""
        result = FilterResult(passed=False)

        title_lower = job.title.lower()
        location_lower = job.location.lower()
        content_lower = job.content_text.lower()
        full_text = f"{title_lower} {location_lower} {content_lower}"

        # GATE 1: Remote
        remote_passed, remote_reason = self._check_remote_gate(location_lower, content_lower)
        result.gate_results["remote"] = remote_passed
        if not remote_passed:
            result.drop_reason = f"Remote: {remote_reason}"
            return result

        # GATE 2: Region
        region_passed, region_reason = self._check_region_gate(location_lower, content_lower)
        result.gate_results["region"] = region_passed
        if not region_passed:
            result.drop_reason = f"Region: {region_reason}"
            return result

        # GATE 3: Title
        title_passed, title_reason = self._check_title_gate(title_lower)
        result.gate_results["title"] = title_passed
        if not title_passed:
            result.drop_reason = f"Title: {title_reason}"
            return result

        # GATE 4: Stack
        stack_passed, stack_reason, matched_groups = self._check_stack_gate(full_text)
        result.gate_results["stack"] = stack_passed
        if explain:
            result.keyword_matches["stack_groups"] = matched_groups
        if not stack_passed:
            result.drop_reason = f"Stack: {stack_reason}"
            return result

        # Compute score
        score, breakdown, matches = self._compute_score(title_lower, content_lower)
        result.score = score
        result.scoring_breakdown = breakdown
        if explain:
            result.keyword_matches.update(matches)

        # GATE 5: Min score
        if score < self.min_score:
            result.drop_reason = f"Score {score} < min {self.min_score}"
            return result

        result.passed = True
        return result

    def _check_remote_gate(self, location: str, content: str) -> Tuple[bool, str]:
        text = f"{location} {content}"

        # Check remote_anywhere
        for pattern in self.remote_anywhere:
            if pattern in text:
                return True, f"remote anywhere: '{pattern}'"

        # Check positive
        has_positive = any(p in text for p in self.remote_positive)

        # Check negative
        has_negative = any(n in text for n in self.remote_negative)

        if has_negative:
            return False, "contains remote negative"

        if has_positive:
            return True, "contains remote positive"

        if self.config.get("require_remote", True):
            return False, "no remote keywords (require_remote=true)"

        return True, "remote not required"

    def _check_region_gate(self, location: str, content: str) -> Tuple[bool, str]:
        text = f"{location} {content}"

        # FIRST: Check blocked regions (always!)
        for region in self.blocked_regions:
            if region in text:
                return False, f"blocked region: '{region}'"

        # Check if there's an explicit restriction
        restriction_patterns = [
            "must be located in", "must be based in", "must reside in",
            "only candidates located in", "only within", "must be in"
        ]

        has_restriction = any(p in text for p in restriction_patterns)

        # If restriction found, must match allowed regions
        if has_restriction:
            for region in self.allowed_regions:
                if region in text:
                    return True, f"allowed region: '{region}'"
            return False, "unknown region restriction (strict)"

        # No restriction = pass
        return True, "no region restriction"

    def _check_title_gate(self, title: str) -> Tuple[bool, str]:
        # Check blocks
        for pattern in self.title_block_patterns:
            if pattern.search(title):
                return False, f"blocked: '{pattern.pattern}'"

        # Check allows
        for pattern in self.title_allow_patterns:
            if pattern.search(title):
                return True, f"allowed: '{pattern.pattern}'"

        return False, "no allowed title pattern"

    def _check_stack_gate(self, text: str) -> Tuple[bool, str, List[str]]:
        tokens = self._tokenize(text)

        matched_groups = []
        for group_name, keywords in self.stack_groups.items():
            if self._group_matches(keywords, tokens, text):
                matched_groups.append(group_name)

        if len(matched_groups) >= self.min_groups_matched:
            return True, f"{len(matched_groups)}/{len(self.stack_groups)} groups", matched_groups

        return False, f"only {len(matched_groups)}/{self.min_groups_matched} groups", matched_groups

    def _group_matches(self, keywords: List[str], tokens: Set[str], text: str) -> bool:
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if ' ' in keyword_lower:
                if keyword_lower in text:
                    return True
            else:
                if keyword_lower in tokens:
                    return True
        return False

    def _compute_score(self, title: str, content: str) -> Tuple[int, Dict[str, int], Dict[str, List[str]]]:
        score = 0
        breakdown = {}
        matches = {}

        tokens = self._tokenize(f"{title} {content}")

        # Title bonus
        title_score = 0
        title_matches = []
        for keyword, bonus in self.title_bonus.items():
            if keyword.lower() in title:
                title_score += bonus
                title_matches.append(keyword)

        breakdown["title_bonus"] = title_score
        matches["title_bonus"] = title_matches
        score += title_score

        # Keyword scoring
        keyword_score = 0
        keyword_matches = []
        for keyword, weight in self.include_keywords.items():
            keyword_lower = keyword.lower()

            if ' ' in keyword_lower:
                if keyword_lower in f"{title} {content}":
                    keyword_score += weight
                    keyword_matches.append(keyword)
            else:
                if keyword_lower in tokens:
                    keyword_score += weight
                    keyword_matches.append(keyword)

        breakdown["keywords"] = keyword_score
        matches["keywords"] = keyword_matches
        score += keyword_score

        return score, breakdown, matches

    @staticmethod
    def _tokenize(text: str) -> Set[str]:
        tokens = re.findall(r'\b\w+\b', text.lower())
        return set(tokens)

    def explain_job(self, job) -> str:
        """Generate explanation"""
        result = self.filter_job(job, explain=True)

        lines = [
            f"Job: {job.title} @ {job.company}",
            f"Location: {job.location}",
            f"URL: {job.url}",
            "",
            "GATES:",
        ]

        for gate, passed in result.gate_results.items():
            status = "✓" if passed else "✗"
            lines.append(f"  {gate}: {status}")

        if not result.passed:
            lines.append(f"\nDROP: {result.drop_reason}")
        else:
            lines.append(f"\nSCORE: {result.score}")
            for cat, pts in result.scoring_breakdown.items():
                lines.append(f"  {cat}: +{pts}")

        return "\n".join(lines)

