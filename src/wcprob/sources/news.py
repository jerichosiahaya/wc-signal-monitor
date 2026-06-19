from collections import Counter
import re
import xml.etree.ElementTree as ET

import httpx

from wcprob.models import SourceKind, SourceObservation

COUNTRIES = {
    "Argentina",
    "Brazil",
    "England",
    "France",
    "Germany",
    "Italy",
    "Mexico",
    "Netherlands",
    "Portugal",
    "Spain",
    "United States",
    "USA",
}


class NewsSignalSource:
    def __init__(self, name: str, url: str, countries: set[str] | None = None):
        self.name = name
        self.url = url
        self.countries = countries or COUNTRIES

    def fetch(self) -> list[SourceObservation]:
        response = httpx.get(self.url, timeout=20, follow_redirects=True)
        response.raise_for_status()
        titles = _rss_titles(response.text)
        counts = _country_mentions(titles, self.countries)
        if not counts:
            raise ValueError("news payload has no country mentions")

        total = sum(counts.values())
        return [
            SourceObservation(
                source=self.name,
                source_kind=SourceKind.NEWS_SCRAPER,
                country=_canonical_country(country),
                raw_value=f"{count} mentions",
                implied_probability=count / total,
            )
            for country, count in counts.most_common()
        ]


def _rss_titles(xml_text: str) -> list[str]:
    root = ET.fromstring(xml_text)
    titles = []
    for item in root.findall(".//item"):
        title = item.findtext("title")
        if title:
            titles.append(title)
    for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
        title = entry.findtext("{http://www.w3.org/2005/Atom}title")
        if title:
            titles.append(title)
    return titles


def _country_mentions(titles: list[str], countries: set[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    text = "\n".join(titles)
    for country in countries:
        pattern = rf"\b{re.escape(country)}\b"
        match_count = len(re.findall(pattern, text, flags=re.IGNORECASE))
        if match_count:
            counts[country] += match_count
    return counts


def _canonical_country(country: str) -> str:
    if country.upper() == "USA":
        return "United States"
    return country
