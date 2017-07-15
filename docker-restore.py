import json, os, sys

RESULT_FILE = "start_docker.sh"
DOCKERPATH = "/var/lib/docker/containers"
BASE_RUN_COMMAND = "docker run -d --name {} {} --restart always "

def load_file(path):
    with open(path[0]) as confv2:
        data = json.load(confv2)
    return data

def parse_file(path):
    data = {}
    data['args'] = load_file(path[0])
    data['host'] = load_file(path[1])
    return data

def get_docker_configs():
    return [(DOCKERPATH + "/" + name + "/config.v2.json", DOCKERPATH + "/" + name + "/hostconfig.json") for name in os.listdir(DOCKERPATH)]

def main():
    for conf in get_docker_configs():
        write_command(parse_file(conf))
    print("Done!")

def parse_volumes(data):
    res = ""
    if data['host']['Binds']:
        for entry in data['host']['Binds']:
            res += " -v "+entry
    return res

def parse_ports(data):
    res = ""
    if data['host']['PortBindings']:
        for entry in data['host']['PortBindings']:
            inside_port = entry[:entry.index('/')]
            if data['host']['PortBindings'][entry]:
                i = 0
                for port, ip in data['host']['PortBindings'][entry]:
                    res += " -p "+(data['host']['PortBindings'][entry][i][ip]+":" if data['host']['PortBindings'][entry][i][ip] else "")+data['host']['PortBindings'][entry][i][port]+":"+inside_port
                    i += 1
            else:
                res += " -p "+inside_port+":"+inside_port
    return res

def parse_env(data):
    res = ""
    if data['args']['Config']['Env']:
        for entry in data['args']['Config']['Env']:
            res += " -e "+entry
    return res

def write_command(data):
    with open(RESULT_FILE, 'a') as data_file:
        volumes = parse_volumes(data)
        ports = parse_ports(data)
        env = parse_env(data)
        args = volumes.strip() + ((" " if volumes != "" else "") + ports.strip() if ports != "" else "") + (" " + env.strip() if env != "" else "")
        if len(data['args']['Name'][1:]) < 20:
            if data['host']['Privileged']:
                data_file.write((BASE_RUN_COMMAND+"--privileged {}\n").format(data['args']['Name'][1:], args, data['args']['Config']['Image']))
            else:
                data_file.write((BASE_RUN_COMMAND+"{}\n").format(data['args']['Name'][1:], args, data['args']['Config']['Image']))
    return data

def create_result_file():
    f = open(RESULT_FILE, 'w')
    f.write("#!/bin/bash\n\n")
    f.close()
    os.chmod(RESULT_FILE, 755)

def check_if_docker():
    if not os.path.exists(DOCKERPATH):
        print("Please install docker first")
        sys.exit()

def setup():
    create_result_file()
    check_if_docker()

if __name__ == '__main__':
    setup()
    main()
