import math
import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


def make_pose(navigator, x, y, yaw=0.0):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = math.sin(yaw / 2)
    pose.pose.orientation.w = math.cos(yaw / 2)
    return pose


def main():
    rclpy.init()
    navigator = BasicNavigator()

    # 로봇의 시작 위치(지도 기준)
    navigator.setInitialPose(make_pose(navigator, 0.0, 0.0))
    navigator.waitUntilNav2Active()

    points = [(1.62, 1.80), (-0.35, 0.79), (1.93, -0.84)]
    waypoints = [make_pose(navigator, x, y) for x, y in points]

    navigator.followWaypoints(waypoints)
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback:
            print(f'진행 중: {feedback.current_waypoint + 1}/{len(waypoints)}번째 지점으로 이동')

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('순찰 완료')
    elif result == TaskResult.CANCELED:
        print('취소됨')
    else:
        print('실패')

    navigator.lifecycleShutdown()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
