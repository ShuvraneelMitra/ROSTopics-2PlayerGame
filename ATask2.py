#!/usr/bin/env

import rospy
from std_msgs.msg import String


publisher = rospy.Publisher('read_from_A', String, queue_size=100)
inp = String()


def callback(data):
    global inp
    if "turn" in data.data:
        print(data.data, end='')
        inp = input()
        publisher.publish(inp)
    else:
        print(data.data)


subscriber = rospy.Subscriber('write_to_A', String, callback)
rospy.init_node('nodeA', anonymous=True)
rospy.spin()
