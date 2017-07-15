# DockerRestore


This script tries to restore the initial launch commands of all existing docker containers on the system. 
This task is done by analyzing the config files in `/var/lib/docker/containers`, like the `runlike` Project does, but this method also works with an malfunctioning / not running docker engine.
