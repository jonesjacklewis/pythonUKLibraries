# Define constants
SPARQL_WIKIDATA_URL: str = "https://query.wikidata.org/sparql"
KNOWN_BAD_LATITUDES: list[float] = [
    53.047014
]
POSTCODE_REGEX: str = r"[A-Z]{1,2}[0-9]{1,2} ?[0-9][A-Z]{2}"
EARTH_RADIUS_KM: float = 6371.0
SIX_MONTHS_IN_DAYS: int = 180
DAYS_TO_REFRESH_DB: int = SIX_MONTHS_IN_DAYS