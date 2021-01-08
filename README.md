# MAS-UAV
Multi agent system to coordinate multiple UAVs

This repository was tested with ubuntu 18.04, ROS melodic and gazebo 9.
## Build
This repository is a ROS package, therefore it is necessary to set up a ROS workspace with the necessary packages and build it.

First, source ROS and create a new workspace:

```
$ source /opt/ros/melodic/setup.bash
$ mkdir -p ~/pi_ros_ws/src
$ cd ~/pi_ros_ws/
$ catkin_make
```

Then, download the necessary packages:
```
$ cd ~/pi_ros_ws/src/
$ git clone https://github.com/eng-Marcio/PI_VANT.git
$ mv PI_VANT mas_uav
```

Download deps and build the workspace:
```
$ cd ~/pi_ros_ws/
$ apt update
$ rosdep install --from-paths src --ignore-src -r -y
$ catkin_make
```

Next step needs root privileges, so we use sudo su then source the setup script
```
$ sudo su
$ source ~/pi_ros_ws/devel/setup.bash
$ rosrun mavros install_geographiclib_datasets.sh
$ exit
$ apt install gradle
```

Also, this experiments use ardupilot SITL to simulate the UAVs so it is necessary to set it up. The instructions for installing it can be found in: https://ardupilot.org/dev/docs/building-setup-linux.html#building-setup-linux

After installing ardupilot add UFSC location into locations.txt

```
$ echo 'UFSC=-27.604033,-48.518363,21,0' >> ~/ardupilot/Tools/autotest/locations.txt
```

It is also possible to use gazebo with ardupilot SITL, in case you do not want to use it you can skip the following instructions.

First, it is necessary to install a plugin to enable ardupilot to communicate with gazebo.

```
$ sudo apt-get install libgazebo9-dev
```

```
$ cd ~/pi_ros_ws/src
$ git clone https://github.com/LucasEOC/ardupilot_gazebo
$ cd ardupilot_gazebo
$ mkdir build
$ cd build
$ cmake ..
$ make -j4
$ sudo make install
```

````
echo 'source /usr/share/gazebo/setup.sh' >> ~/.bashrc
````

Set Path of Gazebo Models (Adapt the path to where to clone the repo)
````
echo 'export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/pi_ros_ws/src/ardupilot_gazebo/models' >> ~/.bashrc
````

Set Path of Gazebo Worlds (Adapt the path to where to clone the repo)
````
echo 'export GAZEBO_RESOURCE_PATH=$GAZEBO_RESOURCE_PATH:~/pi_ros_ws/src/ardupilot_gazebo/worlds' >> ~/.bashrc
````

````
source ~/.bashrc
````

DONE !

## Experiments
### Single UAV

For this experiment a simple mission was performed: the UAV had to (1) takeoff; (2) fly to a predefined waypoint; (3) return to home; and finally (4) land.

#### Start ardupilot:

If you will not use gazebo:
```
$ sim_vehicle.py -v ArduCopter --map --console -L UFSC -I 0
```

If you will use gazebo (optional):
```
$ sim_vehicle.py -v ArduCopter -f gazebo-iris --map --console -L UFSC -I 0
```

If you want to use gazebo run it in another terminal (optional):

```
$ gazebo --verbose iris_arducopter_runway.world
```

#### Run the experiment:
Remeber to source the workspace:

```
$ source ~/pi_ros_ws/devel/setup.bash
$ roslaunch mas_uav single_uav_python.launch
```
You should see this as result:

[![singleUAV video](https://img.youtube.com/vi/5kYMEPmcZ6g/0.jpg)](https://www.youtube.com/watch?v=5kYMEPmcZ6g)
## Future Works
 - A lidar shall be added
 - Dockerfile shall be created/updated for this project
 - Dockerfile-compose shall be created/update for this project
 - It should be possible to run the docker-compose with balena
 - Gazebo world and models shall be improved
 - ardupilot_gazebo should be turned into a ROS package
