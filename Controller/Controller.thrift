// namespace py controller
//
//service RobotController {
//   bool registerRobot(1: string robot_id, 2: bool status),
//   bool getRobotStatus(1: string robot_id),
//}

namespace py controller

struct RobotInfo {
    1: string robot_id;
    2: bool status;
}

struct RobotStatus {
    1: bool status;
}

service RobotController {
    bool registerRobot(1: RobotInfo robotInfo);
    RobotStatus getRobotStatus(1: string robot_id);
    void updateRobotStatus(1: string robot_id, 2: bool new_status);
    void notifyLeaderElection(1: string leader_robot_id);
    void startElection();
    void startRegistration();
}