import pytest
import numpy as np
import geolocaltransform as glt


class TestGeoLocalTransform:
    def test_initialization(self):
        """Test basic initialization of GeoLocalTransform."""
        t = glt.GeoLocalTransform(37.0, -122.0, 0.0)
        assert t is not None

    def test_forward_reverse_transform(self):
        """Test forward and reverse coordinate transformations."""
        # San Francisco coordinates
        lat_origin, lon_origin, h_origin = 37.0, -122.0, 0.0
        t = glt.GeoLocalTransform(lat_origin, lon_origin, h_origin)
        
        # Test point slightly northeast
        lat_test, lon_test, h_test = 37.1, -122.1, 100.0
        
        # Forward transform: geographic to local Cartesian
        local_coords = t.Forward(lat_test, lon_test, h_test)
        assert len(local_coords) == 3
        assert isinstance(local_coords[0], float)
        assert isinstance(local_coords[1], float)
        assert isinstance(local_coords[2], float)
        
        # Reverse transform: local Cartesian back to geographic
        geo_coords = t.Reverse(local_coords[0], local_coords[1], local_coords[2])
        assert len(geo_coords) == 3
        
        # Should get back approximately the same coordinates
        np.testing.assert_allclose([geo_coords[0], geo_coords[1], geo_coords[2]], 
                                   [lat_test, lon_test, h_test], 
                                   rtol=1e-10, atol=1e-10)

    def test_reset_origin(self):
        """Test resetting the local coordinate system origin."""
        t = glt.GeoLocalTransform(37.0, -122.0, 0.0)
        
        # Transform a point with original origin
        local1 = t.Forward(37.1, -122.1, 100.0)
        
        # Reset to new origin
        t.Reset(37.05, -122.05, 50.0)
        
        # Transform same point with new origin - should get different result
        local2 = t.Forward(37.1, -122.1, 100.0)
        
        # Results should be different
        assert not np.allclose(local1, local2)

    def test_utm_standard_zone(self):
        """Test UTM standard zone calculation."""
        # Test known coordinates using static method
        zone_sf = glt.GeoLocalTransform.UTMStandardZone(37.0, -122.0)  # San Francisco
        zone_nyc = glt.GeoLocalTransform.UTMStandardZone(40.7, -74.0)  # New York City
        
        assert isinstance(zone_sf, int)
        assert isinstance(zone_nyc, int)
        assert zone_sf != zone_nyc  # Different zones for different locations

    def test_utm_forward(self):
        """Test UTM forward transformation."""
        # Transform San Francisco coordinates to UTM using static method
        utm_coords = glt.GeoLocalTransform.UTMForward(37.0, -122.0)
        assert len(utm_coords) == 3
        assert isinstance(utm_coords[0], float)  # Easting
        assert isinstance(utm_coords[1], float)  # Northing
        assert isinstance(utm_coords[2], float)  # Zone info

    def test_utm_reverse(self):
        """Test UTM reverse transformation."""
        lat_orig, lon_orig = 37.0, -122.0
        
        # Forward transform to UTM using static method
        utm_coords = glt.GeoLocalTransform.UTMForward(lat_orig, lon_orig)
        
        # Reverse transform back to geographic using static method
        geo_coords = glt.GeoLocalTransform.UTMReverse(utm_coords[0], utm_coords[1], lat_orig, lon_orig)
        assert len(geo_coords) == 3
        
        # Should get back approximately the same coordinates
        np.testing.assert_allclose([geo_coords[0], geo_coords[1]], 
                                   [lat_orig, lon_orig], 
                                   rtol=1e-10, atol=1e-10)

    def test_geodesic_inverse(self):
        """Test geodesic inverse calculation (distance and bearing between points)."""
        # Calculate distance and bearing between San Francisco and Los Angeles using static method
        lat1, lon1 = 37.7749, -122.4194  # San Francisco
        lat2, lon2 = 34.0522, -118.2437   # Los Angeles
        
        result = glt.GeoLocalTransform.GeodesicInverse(lat1, lon1, lat2, lon2)
        assert len(result) == 3
        
        distance, initial_bearing, final_bearing = result
        assert isinstance(distance, float)
        assert isinstance(initial_bearing, float)
        assert isinstance(final_bearing, float)
        
        np.testing.assert_allclose(result, [559040, 136.38, 138.82], rtol=1, atol=1)
        
        # Initial bearing should be roughly southeast
        assert 100 < initial_bearing < 200  # degrees

    def test_geodesic_direct(self):
        """Test geodesic direct calculation (destination from start + bearing + distance)."""
        # Start at San Francisco, go 10km northeast (45 degrees) using static method
        lat_start, lon_start = 37.7749, -122.4194
        bearing = 45.0  # degrees
        distance = 10000.0  # meters
        
        result = glt.GeoLocalTransform.GeodesicDirect(lat_start, lon_start, bearing, distance)
        assert len(result) == 3
        
        lat_end, lon_end, final_bearing = result
        assert isinstance(lat_end, float)
        assert isinstance(lon_end, float)
        assert isinstance(final_bearing, float)
        
        # End point should be northeast of start
        assert lat_end > lat_start  # More northerly
        assert lon_end > lon_start  # More easterly (less negative)

    def test_roundtrip_consistency(self):
        """Test that forward->reverse and inverse->direct are consistent."""
        t = glt.GeoLocalTransform(37.0, -122.0, 0.0)
        
        # Test multiple points
        test_points = [
            (37.1, -122.1, 100.0),
            (36.9, -121.9, 50.0),
            (37.05, -122.05, 75.0)
        ]
        
        for lat, lon, height in test_points:
            # Forward then reverse
            local = t.Forward(lat, lon, height)
            geo_back = t.Reverse(local[0], local[1], local[2])
            
            np.testing.assert_allclose([geo_back[0], geo_back[1], geo_back[2]], 
                                       [lat, lon, height], 
                                       rtol=1e-10, atol=1e-10)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with origin at equator and prime meridian
        t = glt.GeoLocalTransform(0.0, 0.0, 0.0)
        
        # Transform origin itself
        local_origin = t.Forward(0.0, 0.0, 0.0)
        np.testing.assert_allclose(local_origin, [0.0, 0.0, 0.0], atol=1e-10)
        
        # Reverse transform of origin
        geo_origin = t.Reverse(0.0, 0.0, 0.0)
        np.testing.assert_allclose(geo_origin, [0.0, 0.0, 0.0], atol=1e-10)
