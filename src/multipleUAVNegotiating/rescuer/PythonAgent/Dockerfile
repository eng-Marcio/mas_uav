FROM rezenders/jason-ros

RUN apt-get update && apt-get install -y \
    python-pip \
    && rm -rf /var/lib/apt/lists/

RUN pip install simple-settings


## Copy Agent files
COPY * /uav_agents/

WORKDIR /uav_agents/
