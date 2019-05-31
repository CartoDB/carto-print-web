var user = 'aromeu';
var apiKey = 'default_public';
var mapId = 'https://team.carto.com/u/aromeu/builder/6e159dee-cc62-4872-8c87-28c7eb985302/embed';
var width = 30;
var height = 20;
var dpi = 300;
var baseLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}.png', {
     maxZoom: 18
  });
const applicationContent = document.querySelector('as-responsive-content');

applicationContent.addEventListener('ready', () => {
  const dropdown = document.querySelector('#paper_size');
  dropdown.options = [
    { text: '30x20', value: '30x20' },
    { text: '60x40', value: '60x40' },
    { text: '100x60', value: '100x60' },
    { text: '200x100', value: '200x100' },
    { text: '20x30', value: '20x30' },
    { text: '40x60', value: '40x60' },
    { text: '60x90', value: '60x90' }
  ];
  dropdown.addEventListener('optionChanged', (event) => {
    let wh = event.detail;
    width = parseInt(wh.split('x')[0], 10);
    height = parseInt(wh.split('x')[1], 10);
  });

  const dropdown_dpi = document.querySelector('#dpi');
  dropdown_dpi.options = [
    { text: '72', value: '72' },
    { text: '300', value: '300' }
  ];
  dropdown_dpi.addEventListener('optionChanged', (event) => {
    dpi = event.detail;
  });

  const userInput = document.querySelector('#user');
  userInput.addEventListener("keyup", () => {
    user = userInput.value;
  });

  const apiKeyInput = document.querySelector('#api_key');
  apiKeyInput.addEventListener("keyup", () => {
    apiKey = apiKeyInput.value;
  });

  const mapIdInput = document.querySelector('#map_id');
  mapIdInput.addEventListener("keyup", () => {
    mapId = mapIdInput.value;
  });

  const loadButton = document.querySelector('#load');
  loadButton.addEventListener("click", () => {
    loadMap();
  });

  const printButton = document.querySelector('#print');
  printButton.addEventListener("click", () => {
    printMap();
  });

  const us = [39.571822, -99.492187];
  const ny = [40.728527, -73.970947];
  const sf = [37.735969,-122.445374];
  const la = [33.838483,-117.960205];
  const es = [40.433360,-3.694153];
  window.map = L.map('map').setView(es, 5);
  baseLayer.addTo(map);
});

function drawRectangle(width_cm, height_cm) {
  ONE_DPI = 0.393701;
  pixels_cm = 37.795275591;

  width_px = cm_to_pixels(width_cm);
  height_px = cm_to_pixels(height_cm);

  rectangle.style.width = width_px + "px";
  rectangle.style.height = height_px + "px";

  rectangle.style.top = (map.getSize().y / 2) - (height_px / 2) + "px";
  rectangle.style.left = (map.getSize().x / 2) - (width_px / 2) + "px";

  bb = map.getPixelBounds();
  or = map.getPixelOrigin();
  dfx = bb.min.x - or.x;
  dfy = bb.min.y - or.y;
  minX = ((bb.max.x - bb.min.x) / 2) - (width_px / 2) + dfx
  maxX = ((bb.max.x - bb.min.x) / 2) + (width_px / 2) + dfx
  minY = ((bb.max.y - bb.min.y) / 2) + (height_px / 2) + dfy
  maxY = ((bb.max.y - bb.min.y) / 2) - (height_px / 2) + dfy

  minCorner = map.layerPointToLatLng(new L.Point(minX, minY))
  maxCorner = map.layerPointToLatLng(new L.Point(maxX, maxY))

  bounds = L.latLngBounds(minCorner, maxCorner);

  _minX = map.getCenter().lng - (width_px / 2 * get_resolution());
  _maxX = map.getCenter().lng + (width_px / 2 * get_resolution());
  _maxY = map.getCenter().lat - (height_px / 2 * get_resolution());
  _minY = map.getCenter().lat + (height_px / 2 * get_resolution());

  var _minCorner = L.latLng(_minY, _minX);
  var _maxCorner = L.latLng(_maxY, _maxX);
  _bounds = L.latLngBounds(_minCorner, _maxCorner);
  window.bbounds = bounds.toBBoxString();
  console.log(bounds.toBBoxString());

  if (window.pra) {
    map.removeLayer(window.pra);
  }

  window.pra = L.rectangle(bounds, {color: "red", weight: 1}).addTo(map);
}

function cm_to_pixels(cm) {
  return cm / 2.54 * getDPI();
}

function get_resolution() {
  return 360 / 256 / Math.pow(2, map.getZoom());
}

function getDPI() {
  let devicePixelRatio = 2
    return 72 / devicePixelRatio / 2;
    var div = document.createElement( "div");
    div.style.height = "1in";
    div.style.width = "1in";
    div.style.top = "-100%";
    div.style.left = "-100%";
    div.style.position = "absolute";

    document.body.appendChild(div);

    var result =  div.offsetHeight;

    document.body.removeChild( div );

    return result / devicePixelRatio;
}

function loadMap() {
  rectangle = document.querySelector('#rect');

  let theMapId = sanitize(getMapId());
  let tileLayer = `https://${user}.carto.com/api/v1/map/named/tpl_${theMapId}/1,0/{z}/{x}/{y}.png`

  if (window.printLayer) {
    map.removeLayer(printLayer);
  } else {
    map.removeLayer(baseLayer);
  }

  window.printLayer = L.tileLayer(tileLayer, {
    maxZoom: 18
  }).addTo(map);

  drawRectangle(width, height);

  map.on('move', () => {
    drawRectangle(width, height);
  });
}

function getMapId() {
  return mapId.split('builder/')[1].split('/embed')[0];
}

function sanitize(anything) {
  return anything.split('-').join('_').trim();
}

function printMap() {
  let theMapId = 'tpl_' + sanitize(getMapId());
  url = `export?mapId=${theMapId}&width=${width}&height=${height}&dpi=${dpi}&user=${user}&apiKey=${apiKey}&zoom=${map.getZoom() + 1}&bounds=${bbounds}&format=RGBA`
  console.log(url);
  window.open(url, '_blank');
}
