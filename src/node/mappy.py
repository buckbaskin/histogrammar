from ..histogrammar import HistogramFilter
from geometry_msgs.msg import Pose, PoseArray
from math import pi
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan

hf = HistogramFilter(field_x = 7.0, field_y=15.0)

last_odom = None

def scan_cb_factory(publisher):
    def scan_cb(scan):
        if last_odom is not None:
            hf.update(last_odom, scan)
            msg = PoseArray()
            for x, y, probability in hf.threshold():
                pose = Pose()
                pose.point.x = x
                pose.point.y = y
                pose.point.z - probability
                msg.poses.append(pose)
            publisher.publish(msg)
    return scan_cb

def odom_cb(odom):
    last_odom = odom

if __name__ == '__main__':
    obstacles_pub = rospy.Publisher('/obstacles', PoseArray, queue_size=1)
    rospy.Subscriber('/odom', Odometry, odom_cb)
    rospy.Subscriber('/scan', LaserScan, scan_cb_factory(obstacles_pub))

    rospy.spin()