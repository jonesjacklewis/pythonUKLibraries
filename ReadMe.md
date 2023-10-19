# UK Nearest Library

## Description

This is a simple python script that will find the nearest library to a given postcode. It uses the [Postcodes.io](https://postcodes.io/) API to get the latitude and longitude of the postcode and then uses Wikidata SparQL to find the nearest library to that point.

## Usage

The script takes a single argument, the postcode to search for. It will return the name of the nearest library.

```bash
$ python3 nearest_library.py
```

## Requirements

| Package            | Version  |
|--------------------|----------|
| certifi            | 2023.7.22|
| charset-normalizer | 3.3.0    |
| idna               | 3.4      |
| requests           | 2.31.0   |
| urllib3            | 2.0.6    |


Requirements can be found in [requirements.txt](requirements.txt). They can be installed with pip.

```bash
$ pip install -r requirements.txt
```