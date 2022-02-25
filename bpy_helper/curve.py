import bpy


def bezier_spline_from_points(curve: bpy.types.Curve, points):
    """Adds a new bezier spline to curve from points"""
    spline = curve.splines.new(type="BEZIER")
    # NOTE: spline can have points by default
    spline.bezier_points.add(len(points) - len(spline.bezier_points))
    spline.bezier_points.foreach_set("co", tuple(f for co in points for f in co))
    return spline


def create_bezier_circle(name="circle"):
    bezier_circle_points = ((-1, 0, 0), (0, 1, 0), (1, 0, 0), (0, -1, 0))

    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"

    curve.splines.clear()
    spline = bezier_spline_from_points(curve, bezier_circle_points)
    spline.use_cyclic_u = True

    p: bpy.types.BezierSplinePoint
    for p in spline.bezier_points:
        p.handle_right_type = "AUTO"
        p.handle_left_type = "AUTO"

    obj = bpy.data.objects.new(name, curve)
    return obj
