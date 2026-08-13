import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/media/mojarras/Wiwi/droneops/Learning-Projects/Ros2/install/ControlTurtlesim'
