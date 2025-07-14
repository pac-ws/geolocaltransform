# geolocaltransform

A Python extension library for geographical coordinate transformations using GeographicLib.

## Installation

```bash
pip install .
```

## Usage

### Creating a GeoLocalTransform Object

```python
import geolocaltransform as glt

# Create transformer with origin at latitude, longitude, height
transform = glt.GeoLocalTransform(37.0, -122.0, 0.0)

# Note: UTM and Geodesic methods are static and can be called without an instance:
# glt.GeoLocalTransform.GeodesicInverse(...)
# glt.GeoLocalTransform.UTMStandardZone(...)
```

## Function Signatures

### Local Coordinate Transformations

#### `Forward(lat, lon, height) -> [x, y, z]`
Convert geographic to local Cartesian coordinates.
```python
local_coords = transform.Forward(37.1, -122.1, 100.0)
# Returns approximately: [-8889.6, 11102.7, 84.1]
```

#### `Reverse(x, y, z) -> [lat, lon, height]`
Convert local Cartesian to geographic coordinates.
```python
geo_coords = transform.Reverse(-8889.6, 11102.7, 84.1)
# Returns approximately: [37.1, -122.1, 100.0]
```

#### `Reset(lat, lon, height)`
Set new local coordinate system origin.
```python
transform.Reset(40.0, -74.0, 10.0)
```

### UTM Coordinate Transformations (Static Methods)

#### `UTMStandardZone(lat, lon) -> zone`
Get standard UTM zone for coordinates.
```python
# Can be called without creating an instance
zone = glt.GeoLocalTransform.UTMStandardZone(37.0, -122.0)
# Returns: 10
```

#### `UTMForward(lat, lon) -> [x, y, zone]`
Convert geographic to UTM coordinates.
```python
utm_coords = glt.GeoLocalTransform.UTMForward(37.0, -122.0)
# Returns: [588977.32, 4095339.69, 0]
```

#### `UTMReverse(x, y, lat, lon) -> [lat, lon, zone]`
Convert UTM to geographic coordinates.
```python
geo_coords = glt.GeoLocalTransform.UTMReverse(588977.32, 4095339.69, 37.0, -122.0)
# Returns: [37.0, -122.0, 0]
```

### Geodesic Calculations (Static Methods)

#### `GeodesicInverse(lat1, lon1, lat2, lon2) -> [distance, bearing1, bearing2]`
Calculate distance and bearings between two points.
```python
# Can be called without creating an instance
result = glt.GeoLocalTransform.GeodesicInverse(37.0, -122.0, 37.1, -122.1)
# Returns: [distance(m), initial bearing, final bearing]
```

#### `GeodesicDirect(lat1, lon1, bearing, distance) -> [lat2, lon2, bearing2]`
Calculate destination point from start point, bearing, and distance.
```python
destination = glt.GeoLocalTransform.GeodesicDirect(37.0, -122.0, 45.0, 10000.0)
# Returns: [lat, lon, final bearing]
```

## Example

```python
import geolocaltransform as glt

# Create transformer with origin at San Francisco
t = glt.GeoLocalTransform(37.0, -122.0, 0.0)

# Convert to local coordinates
local = t.Forward(37.1, -122.1, 100.0)
print("Local coords:", local)

# Convert back to geographic
geo = t.Reverse(local[0], local[1], local[2])
print("Geographic coords:", geo)

# Calculate distance between two points (static method)
dist_bearing = glt.GeoLocalTransform.GeodesicInverse(37.0, -122.0, 37.1, -122.1)
print("Distance:", dist_bearing[0], "meters")
```
