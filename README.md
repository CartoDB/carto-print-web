# carto-print-web

A web service for https://github.com/CartoDB/carto-print

### Run locally

```sh
virtualenv -p python3 env
source env/bin/activate
pip intall -r requirements.txt
honcho start
```

### Run with Docker

See instructions [here](https://hub.docker.com/r/carto/printer/)

### API

```
https://printer.carto.io/export?mapId=6e159dee-cc62-4872-8c87-28c7eb985302&width=30&height=20&dpi=300&user=aromeu&apiKey=default_public&zoom=3&bounds=-135.04614041546196,16.786487115172083,-60.304506557194294,55.41477591055137
```

Where:

- mapId: ID of a Named map (or BUILDER map)
- width: output width in centimeters
- height: output height in centimeters
- dpi: output dots per inch (300 or more for printing)
- user: CARTO username
- apiKey: CARTO API key (use `default_public` for public maps)
- bounds: Bounding box to export an image
- zoom: Zoom level

### UI

Go to `http://localhost:5000/ui`

### Cloud version

Go to `https://printer.carto.io/ui`
