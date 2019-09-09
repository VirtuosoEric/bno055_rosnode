#!/usr/bin/env python

import rospy
from std_msgs.msg import *
from sensor_msgs.msg import *
import BNO055

pub = rospy.Publisher('imu', Imu, queue_size=10)

def imu_pub(wx,wy,wz,ax,ay,az):
    msg = Imu()
    msg.header.stamp = rospy.get_rostime()
    msg.header.frame_id = 'imu_link'
    msg.angular_velocity.x = wx
    msg.angular_velocity.y = wy
    msg.angular_velocity.z = wz
    msg.linear_acceleration.x = ax
    msg.linear_acceleration.y = ay
    msg.linear_acceleration.z = az
    pub.publish(msg)




def imu_driver(device_port):
    bno = BNO055.BNO055(serial_port=device_port)
    initialized = False

    while not initialized and not rospy.is_shutdown():
        try:
            # Enable verbose debug logging if -v is passed as a parameter.
            # if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
            #     logging.basicConfig(level=logging.DEBUG)
            # Initialize the BNO055 and stop if something went wrong.
            if not bno.begin():
                raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
            
            # Print system status and self test result.
            status, self_test, error = bno.get_system_status()
            print('System status: {0}'.format(status))
            print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
            # Print out an error if system status is in error mode.
            if status == 0x01:
                print('System error: {0}'.format(error))
                print('See datasheet section 4.3.59 for the meaning.')

            # Print BNO055 software revision and other diagnostic data.
            sw, bl, accel, mag, gyro = bno.get_revision()
            print('Software version:   {0}'.format(sw))
            print('Bootloader version: {0}'.format(bl))
            print('Accelerometer ID:   0x{0:02X}'.format(accel))
            print('Magnetometer ID:    0x{0:02X}'.format(mag))
            print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))
            initialized = True
        except:
            print 'initialization failed, retrying... '
            pass

    

    while not rospy.is_shutdown():
        try:
            # Gyroscope data (in degrees per second):
            wx,wy,wz = bno.read_gyroscope()

            # Accelerometer data (in meters per second squared):
            ax,ay,az = bno.read_accelerometer()
            # print ('x=',x,' y=',y,' z=',z)

            imu_pub(wx,wy,wz,ax,ay,az)
        except:
            print 'reading failed'
            pass



if __name__ == '__main__':
    rospy.init_node('imu_node', anonymous=False)
    device_port = rospy.get_param('~port', '/dev/ttyUSB0')
    imu_driver(device_port)
    rospy.spin()
