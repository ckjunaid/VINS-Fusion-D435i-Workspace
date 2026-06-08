import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from rclpy.qos import QoSProfile, ReliabilityPolicy

class ImuMerger(Node):
    def __init__(self):
        super().__init__('imu_merger')
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.pub = self.create_publisher(Imu, '/camera/imu', 10)
        self.gyro_msg = None
        self.accel_msg = None
        self.last_accel_stamp = None
        self.create_subscription(Imu, '/camera/gyro/sample', self.gyro_cb, qos)
        self.create_subscription(Imu, '/camera/accel/sample', self.accel_cb, qos)

    def gyro_cb(self, msg):
        self.gyro_msg = msg
        self.publish()

    def accel_cb(self, msg):
        self.accel_msg = msg
        self.last_accel_stamp = msg.header.stamp

    def publish(self):
        if self.gyro_msg is None or self.accel_msg is None:
            return

        # Check accel is not stale (within 50ms)
        gyro_time = self.gyro_msg.header.stamp.sec + \
                    self.gyro_msg.header.stamp.nanosec * 1e-9
        accel_time = self.accel_msg.header.stamp.sec + \
                     self.accel_msg.header.stamp.nanosec * 1e-9

        if abs(gyro_time - accel_time) > 0.05:
            return  # skip if accel is stale

        imu = Imu()
        imu.header.stamp = self.gyro_msg.header.stamp
        imu.header.frame_id = 'camera_imu_optical_frame'
        imu.angular_velocity = self.gyro_msg.angular_velocity
        imu.angular_velocity_covariance[0] = 0.01
        imu.angular_velocity_covariance[4] = 0.01
        imu.angular_velocity_covariance[8] = 0.01
        imu.linear_acceleration = self.accel_msg.linear_acceleration
        imu.linear_acceleration_covariance[0] = 0.1
        imu.linear_acceleration_covariance[4] = 0.1
        imu.linear_acceleration_covariance[8] = 0.1
        imu.orientation_covariance[0] = -1.0
        self.pub.publish(imu)

def main():
    rclpy.init()
    rclpy.spin(ImuMerger())

if __name__ == '__main__':
    main()
