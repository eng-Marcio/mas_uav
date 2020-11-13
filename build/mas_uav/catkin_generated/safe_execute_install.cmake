execute_process(COMMAND "/home/richardbarbosa/jason_ros_ws/build/mas_uav/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/richardbarbosa/jason_ros_ws/build/mas_uav/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
