# UK Nearest Library

## Description

This is a simple python script that will find the nearest library to a given postcode. It uses the [Postcodes.io](https://postcodes.io/) API to get the latitude and longitude of the postcode and then uses Wikidata SparQL to find the nearest library to that point.

## Requirements

| Package             | Version  |
|---------------------|----------|
| blinker             | 1.6.3    |
| certifi             | 2023.7.22|
| charset-normalizer  | 3.3.0    |
| click               | 8.1.7    |
| Flask               | 3.0.0    |
| idna                | 3.4      |
| importlib-metadata  | 6.8.0    |
| itsdangerous        | 2.1.2    |
| Jinja2              | 3.1.2    |
| MarkupSafe          | 2.1.3    |
| requests            | 2.31.0   |
| urllib3             | 2.0.6    |
| Werkzeug            | 3.0.0    |
| zipp                | 3.17.0   |

Requirements can be found in [requirements.txt](requirements.txt). They can be installed with pip.

```bash
$ pip install -r requirements.txt
```

## Usage

### CLI

1. Navigate to the project directory.
2. Run the cli.py script using the command:

```bash
python cli.py
```

*or*

```bash
python3 cli.py
```

3. Follow the on-screen prompts to input your postcode and receive information about the nearest libraries.

### API

1. Navigate to the project directory.
2. Run the main.py script using the command:

```bash
python main.py
```

*or*

```bash
python3 main.py
```

3. Access the application via a web browser or a tool like Postman at `http://127.0.0.1:5000`

#### Endpoints

##### Get Libraries
- **URL**: /postcode/<string:postcode>/count/<int:count>
- **Method**: GET
- **URL** Params:
- **postcode**: The postcode to search from.
- **count**: The number of libraries to return.
- **Success Response**: 
  - **Code**: 200

```json
{
    "success": true,
    "postcode": "sample postcode",
    "count": 5,
    "libraries": [
        // array of library objects
    ]
}
```

- **Failure Response**:
  - **Code**: 400

```json
{
    "success": false,
    "error": "Invalid postcode"
}
```