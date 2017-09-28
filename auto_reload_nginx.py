import argparse
import os
import sys

import docker

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--nginx-label', default='com.ameyalokare.type=nginx')
    parser.add_argument('--web-label', default='com.ameyalokare.type=web')
    parser.add_argument('--network', default='flaskdockercomposeexample_web_nw')
    parser.add_argument('--template-path', default='conf.d/flaskapp.conf.tmpl')
    parser.add_argument('--destination-path', default='conf.d/flaskapp.conf')
    parser.add_argument('--web-port', type=int, default=5090)
    return parser.parse_args(args)

def reload_nginx(client, web_servers, args):
    web_server_ips = [container.attrs['NetworkSettings']['Networks'][args.network]['IPAddress']
     for container in web_servers.values()]
    render_template(web_server_ips, args)
    nginx_containers = client.containers.list(filters={'label' : args.nginx_label, 'status': 'running'})
    for container in nginx_containers:
        container.kill(signal='SIGHUP')

def render_template(ips, args):
    upstreams = '\n'.join(['server {}:{};'.format(ip, args.web_port) for ip in ips])
    with open(args.template_path, 'r') as f:
        contents = f.read()
        new_contents = contents.replace('__SERVERS__', upstreams)
        tmp_path = args.destination_path + '.tmp'
        with open(tmp_path, 'w') as tmp_file:
            tmp_file.write(new_contents)
            os.rename(tmp_path, args.destination_path)

def get_currently_running_web_servers(client, args):
    web_containers = client.containers.list(filters={'label': args.web_label, 'status': 'running'})
    return dict([(c.id, c) for c in web_containers])

def update_already_running_containers(client, args):
    web_servers = get_currently_running_web_servers(client, args)
    if web_servers:
        reload_nginx(client, web_servers, args)
    return web_servers

def listen_for_events(client, args, web_servers):
    event_filters = {'type': 'container', 'label': args.web_label}
    for event in client.events(filters=event_filters, decode=True):
        if event['status'] == 'start':
            web_servers[event['id']] = client.containers.get(event['id'])
        elif event['status'] == 'stop':
            del web_servers[event['id']]
        else:
            continue
        print "Detected container {} with {} status".format(event['id'], event['status'])
        reload_nginx(client, web_servers, args)

def main(args):
    args = parse_args(args)
    client = docker.from_env()
    web_servers = update_already_running_containers(client, args)
    listen_for_events(client, args, web_servers)

if __name__ == '__main__':
    main(sys.argv[1:])

