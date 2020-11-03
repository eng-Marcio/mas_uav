// Auto-generated. Do not edit!

// (in-package jason_ros_msgs.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;
let std_msgs = _finder('std_msgs');

//-----------------------------------------------------------

class Perception {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.header = null;
      this.perception_name = null;
      this.parameters = null;
      this.update = null;
    }
    else {
      if (initObj.hasOwnProperty('header')) {
        this.header = initObj.header
      }
      else {
        this.header = new std_msgs.msg.Header();
      }
      if (initObj.hasOwnProperty('perception_name')) {
        this.perception_name = initObj.perception_name
      }
      else {
        this.perception_name = '';
      }
      if (initObj.hasOwnProperty('parameters')) {
        this.parameters = initObj.parameters
      }
      else {
        this.parameters = [];
      }
      if (initObj.hasOwnProperty('update')) {
        this.update = initObj.update
      }
      else {
        this.update = false;
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type Perception
    // Serialize message field [header]
    bufferOffset = std_msgs.msg.Header.serialize(obj.header, buffer, bufferOffset);
    // Serialize message field [perception_name]
    bufferOffset = _serializer.string(obj.perception_name, buffer, bufferOffset);
    // Serialize message field [parameters]
    bufferOffset = _arraySerializer.string(obj.parameters, buffer, bufferOffset, null);
    // Serialize message field [update]
    bufferOffset = _serializer.bool(obj.update, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type Perception
    let len;
    let data = new Perception(null);
    // Deserialize message field [header]
    data.header = std_msgs.msg.Header.deserialize(buffer, bufferOffset);
    // Deserialize message field [perception_name]
    data.perception_name = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [parameters]
    data.parameters = _arrayDeserializer.string(buffer, bufferOffset, null)
    // Deserialize message field [update]
    data.update = _deserializer.bool(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += std_msgs.msg.Header.getMessageSize(object.header);
    length += object.perception_name.length;
    object.parameters.forEach((val) => {
      length += 4 + val.length;
    });
    return length + 9;
  }

  static datatype() {
    // Returns string type for a message object
    return 'jason_ros_msgs/Perception';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return '547f6a7c40005d1eac4746fdc9b3ee7b';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    Header header
    string perception_name
    string[] parameters
    bool update
    
    ================================================================================
    MSG: std_msgs/Header
    # Standard metadata for higher-level stamped data types.
    # This is generally used to communicate timestamped data 
    # in a particular coordinate frame.
    # 
    # sequence ID: consecutively increasing ID 
    uint32 seq
    #Two-integer timestamp that is expressed as:
    # * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
    # * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
    # time-handling sugar is provided by the client library
    time stamp
    #Frame this data is associated with
    string frame_id
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new Perception(null);
    if (msg.header !== undefined) {
      resolved.header = std_msgs.msg.Header.Resolve(msg.header)
    }
    else {
      resolved.header = new std_msgs.msg.Header()
    }

    if (msg.perception_name !== undefined) {
      resolved.perception_name = msg.perception_name;
    }
    else {
      resolved.perception_name = ''
    }

    if (msg.parameters !== undefined) {
      resolved.parameters = msg.parameters;
    }
    else {
      resolved.parameters = []
    }

    if (msg.update !== undefined) {
      resolved.update = msg.update;
    }
    else {
      resolved.update = false
    }

    return resolved;
    }
};

module.exports = Perception;
