#include <pybind11/eigen.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl_bind.h>

#include <GeographicLib/Geodesic.hpp>
#include <GeographicLib/LocalCartesian.hpp>
#include <GeographicLib/UTMUPS.hpp>

typedef Eigen::Vector3d Point3;
class GeoLocalTransform {
 private:
  GeographicLib::LocalCartesian geo_obj_;

 public:
  GeoLocalTransform() {}

  GeoLocalTransform(double const lat, double const lon, double const height) {
    geo_obj_ = GeographicLib::LocalCartesian(lat, lon, height);
  }

  void Reset(double const lat, double const lon, double const height) {
    geo_obj_.Reset(lat, lon, height);
  }

  Point3 Forward(double const lat, double const lon,
                 double const height) const {
    Point3 xyz;
    geo_obj_.Forward(lat, lon, height, xyz[0], xyz[1], xyz[2]);
    return xyz;
  }

  Point3 Reverse(double const x, double const y, double const height) const {
    Point3 lla;
    geo_obj_.Reverse(x, y, height, lla[0], lla[1], lla[2]);
    return lla;
  }

  static int UTMStandardZone(double const lat, double const lon) {
    return GeographicLib::UTMUPS::StandardZone(lat, lon);
  }

  static Point3 UTMForward(double const lat, double const lon) {
    int zone;
    bool northp;
    double k;
    double gamma;
    Point3 xyz;
    GeographicLib::UTMUPS::Forward(lat, lon, zone, northp, xyz[0], xyz[1],
                                   gamma, k);
    xyz[2] = 0;
    return xyz;
  }

  static Point3 UTMReverse(double const x, double const y, double const lat,
                    double const lon) {
    int zone;
    bool northp;
    double k;
    double gamma;
    Point3 xyz;
    GeographicLib::UTMUPS::Forward(lat, lon, zone, northp, xyz[0], xyz[1],
                                   gamma, k);
    Point3 lla;
    GeographicLib::UTMUPS::Reverse(zone, northp, x, y, lla[0], lla[1], gamma,
                                   k);
    lla[2] = 0;
    return lla;
  }

  static Point3 GeodesicInverse(double const lat1, double const lon1,
                         double const lat2, double const lon2) {
    double s12, azi1, azi2;
    GeographicLib::Geodesic::WGS84().Inverse(lat1, lon1,
        lat2, lon2, s12,
        azi1, azi2);
    return Point3(s12, azi1, azi2);
  }

  static Point3 GeodesicDirect(double const lat1, double const lon1, double const azi1,
                        double const s12) {
    double lat2, lon2, azi2;
    GeographicLib::Geodesic::WGS84().Direct(lat1, lon1, azi1, s12, lat2, lon2,
                                            azi2);
    return Point3(lat2, lon2, azi2);
  }
};

namespace py = pybind11;
using namespace pybind11::literals;
PYBIND11_MODULE(geolocaltransform, m) {
  py::class_<GeoLocalTransform>(m, "GeoLocalTransform")
      .def(py::init<>())
      .def(py::init<double, double, double>())
      .def("Reset", &GeoLocalTransform::Reset)
      .def("Forward", &GeoLocalTransform::Forward)
      .def("Reverse", &GeoLocalTransform::Reverse)
      .def_static("UTMStandardZone", &GeoLocalTransform::UTMStandardZone)
      .def_static("UTMForward", &GeoLocalTransform::UTMForward)
      .def_static("UTMReverse", &GeoLocalTransform::UTMReverse)
      .def_static("GeodesicInverse", &GeoLocalTransform::GeodesicInverse)
      .def_static("GeodesicDirect", &GeoLocalTransform::GeodesicDirect);
}
