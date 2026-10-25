"""Week 3 lab automation. Uses temporary AWS CLI credentials; never prints secrets."""
import argparse
import copy
import datetime as dt
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'evidence/week-03/data'
REGION = 'us-east-1'
ACCOUNT = '217376138299'
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = str(ROOT / 'aws-credentials')
os.environ['AWS_MAX_ATTEMPTS'] = '2'
os.environ['AWS_PAGER'] = ''


def aws(*args, payload=None):
    cmd = ['aws', *args, '--region', REGION, '--output', 'json']
    if payload is not None:
        local = ROOT / '.local/week03-input.json'
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_text(json.dumps(payload), encoding='utf-8')
        cmd += ['--cli-input-json', 'file://' + str(local)]
    result = subprocess.run(cmd, text=True, capture_output=True, check=True)
    return json.loads(result.stdout) if result.stdout.strip() else {}


def save(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (name + '.json')).write_text(json.dumps(value, indent=2), encoding='utf-8')
    return value


def inspect():
    service = aws('ecs', 'describe-services', '--cluster', 'bg-cluster', '--services', 'bg-service')
    if service.get('failures') or service['services'][0]['deploymentController']['type'] != 'CODE_DEPLOY':
        raise RuntimeError('Expected existing CODE_DEPLOY demo service')
    result = {'checkedAt': dt.datetime.now(dt.timezone.utc).isoformat(), 'account': ACCOUNT, 'region': REGION,
              'service': service,
              'group': aws('deploy', 'get-deployment-group', '--application-name', 'bg-app', '--deployment-group-name', 'bg-deployment-group'),
              'targetGroups': aws('elbv2', 'describe-target-groups', '--names', 'bg-tg-blue', 'bg-tg-green'),
              'securityGroups': aws('ec2', 'describe-security-groups', '--group-ids', 'sg-0b2f0910bab760484', 'sg-09c234bb4a8e6fbcf'),
              'logs': aws('logs', 'describe-log-groups', '--log-group-name-prefix', '/ecs/ecs-bluegreen-demo')}
    save('inventory', result)
    print('Verified account, CODE_DEPLOY service, target groups, security groups and log retention')


def configure():
    groups = aws('elbv2', 'describe-target-groups', '--names', 'bg-tg-blue', 'bg-tg-green')['TargetGroups']
    names = []
    for group in groups:
        dimensions = [{'Name': 'LoadBalancer', 'Value': group['LoadBalancerArns'][0].split(':loadbalancer/')[1]},
                      {'Name': 'TargetGroup', 'Value': group['TargetGroupArn'].split(':')[5]}]
        for suffix, metric, threshold, periods, stat in [('unhealthy', 'UnHealthyHostCount', 1, 3, 'Maximum'),
                                                         ('5xx', 'HTTPCode_Target_5XX_Count', 5, 1, 'Sum')]:
            name = group['TargetGroupName'] + '-' + suffix
            names.append({'name': name})
            alarm = {'AlarmName': name, 'AlarmDescription': 'Week 3 real ECS CodeDeploy rollback lab',
                     'Namespace': 'AWS/ApplicationELB', 'MetricName': metric, 'Dimensions': dimensions,
                     'Statistic': stat, 'Period': 60, 'EvaluationPeriods': periods, 'DatapointsToAlarm': periods,
                     'Threshold': threshold, 'ComparisonOperator': 'GreaterThanOrEqualToThreshold',
                     'TreatMissingData': 'notBreaching',
                     'Tags': [{'Key': 'Project', 'Value': 'ecs-bluegreen-demo'}, {'Key': 'Owner', 'Value': 'khoa-dat'}]}
            aws('cloudwatch', 'put-metric-alarm', payload=alarm)
            save(name + '-configuration', alarm)
    update = {'applicationName': 'bg-app', 'currentDeploymentGroupName': 'bg-deployment-group',
              'alarmConfiguration': {'enabled': True, 'ignorePollAlarmFailure': False, 'alarms': names},
              'autoRollbackConfiguration': {'enabled': True, 'events': ['DEPLOYMENT_FAILURE', 'DEPLOYMENT_STOP_ON_ALARM']}}
    save('deployment-group-update', update)
    aws('deploy', 'update-deployment-group', payload=update)
    print('Configured four real ALB alarms and automatic rollback')


def register(image):
    original = aws('ecs', 'describe-task-definition', '--task-definition', 'ecs-bluegreen-demo:2')['taskDefinition']
    allowed = ['family', 'taskRoleArn', 'executionRoleArn', 'networkMode', 'containerDefinitions', 'volumes',
               'placementConstraints', 'requiresCompatibilities', 'cpu', 'memory', 'runtimePlatform', 'ephemeralStorage']
    template = {k: v for k, v in original.items() if k in allowed}
    revisions = {}
    for mode in ['good', 'bad-health', 'bad-app']:
        task = copy.deepcopy(template)
        container = task['containerDefinitions'][0]
        container['image'] = image
        container['environment'] = [{'name': 'PORT', 'value': '8080'}, {'name': 'APP_RELEASE', 'value': 'green'},
                                    {'name': 'FAIL_HEALTH', 'value': '1' if mode == 'bad-health' else '0'},
                                    {'name': 'FAIL_APP', 'value': '1' if mode == 'bad-app' else '0'}]
        task['tags'] = [{'key': 'Project', 'value': 'ecs-bluegreen-demo'}, {'key': 'Owner', 'value': 'khoa-dat'}]
        result = aws('ecs', 'register-task-definition', payload=task)
        revisions[mode] = result['taskDefinition']['taskDefinitionArn']
        save('task-' + mode, result)
    save('revisions', revisions)
    print(json.dumps(revisions, indent=2))


def deploy(mode):
    alarms = aws('cloudwatch', 'describe-alarms', '--alarm-name-prefix', 'bg-tg-')['MetricAlarms']
    if len(alarms) != 4 or any(a['StateValue'] != 'OK' for a in alarms):
        raise RuntimeError('All four alarms must be OK before a deployment')
    group = aws('deploy', 'get-deployment-group', '--application-name', 'bg-app', '--deployment-group-name', 'bg-deployment-group')['deploymentGroupInfo']
    if group.get('lastAttemptedDeployment', {}).get('status') in ['Created', 'Queued', 'InProgress', 'Ready', 'Baking']:
        raise RuntimeError('A deployment is already active')
    revisions = json.loads((OUT / 'revisions.json').read_text())
    spec = {'version': 0.0, 'Resources': [{'TargetService': {'Type': 'AWS::ECS::Service', 'Properties': {
        'TaskDefinition': revisions[mode], 'LoadBalancerInfo': {'ContainerName': 'demo-app', 'ContainerPort': 8080}}}}]}
    result = aws('deploy', 'create-deployment', payload={'applicationName': 'bg-app', 'deploymentGroupName': 'bg-deployment-group',
                 'description': 'Week 03 ' + mode + ' real alarm and rollback validation',
                 'revision': {'revisionType': 'AppSpecContent', 'appSpecContent': {'content': json.dumps(spec)}}})
    save('deployment-' + mode, result)
    save('appspec-' + mode, spec)
    print(json.dumps(result))


def status(deployment):
    result = aws('deploy', 'get-deployment', '--deployment-id', deployment)
    save(deployment, result)
    info = result['deploymentInfo']
    print(json.dumps({k: info.get(k) for k in ['deploymentId', 'status', 'errorInformation', 'rollbackInfo', 'createTime', 'completeTime']}, indent=2))
    alarms = aws('cloudwatch', 'describe-alarms', '--alarm-name-prefix', 'bg-tg-')
    save('alarms-latest', alarms)
    print(json.dumps([{k: a[k] for k in ['AlarmName', 'StateValue', 'StateReason']} for a in alarms['MetricAlarms']], indent=2))


def collect():
    inspect()
    save('alarms-final', aws('cloudwatch', 'describe-alarms', '--alarm-name-prefix', 'bg-tg-'))
    for name in ['bg-tg-blue-unhealthy', 'bg-tg-green-unhealthy', 'bg-tg-blue-5xx', 'bg-tg-green-5xx']:
        save(name + '-history', aws('cloudwatch', 'describe-alarm-history', '--alarm-name', name,
                                  '--history-item-type', 'StateUpdate', '--max-records', '30'))
    # CloudWatch can return an empty filtered page with a nextToken. Start at
    # today's experiment and consume those pages instead of claiming no logs.
    health = OUT / 'd-PIW6KA9GM.json'
    start = dt.datetime.fromisoformat(json.loads(health.read_text())['deploymentInfo']['createTime']) if health.exists() else dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=2)
    params = ['logs', 'filter-log-events', '--log-group-name', '/ecs/ecs-bluegreen-demo',
              '--start-time', str(int(start.timestamp()*1000)),
              '--filter-pattern', '{ $.status = 503 || $.status = 500 }', '--limit', '100', '--no-paginate']
    events, token = [], None
    for _ in range(20):
        page = aws(*params, *(['--next-token', token] if token else []))
        events.extend(page.get('events', []))
        new_token = page.get('nextToken')
        if not new_token or new_token == token: break
        token = new_token
    else:
        raise RuntimeError('CloudWatch log pagination exceeded 20 pages')
    save('fault-logs', {'events': events, 'startTime': start.isoformat()})
    groups = aws('elbv2', 'describe-target-groups', '--names', 'bg-tg-blue', 'bg-tg-green')['TargetGroups']
    for group in groups:
        save(group['TargetGroupName'] + '-final-health', aws('elbv2', 'describe-target-health', '--target-group-arn', group['TargetGroupArn']))
    alb = groups[0]['LoadBalancerArns'][0]
    save('listeners-final', aws('elbv2', 'describe-listeners', '--load-balancer-arn', alb))
    inventory_path = OUT / 'inventory.json'
    inventory = json.loads(inventory_path.read_text())
    for group in inventory['securityGroups']['SecurityGroups']:
        if group['GroupName'] == 'bg-alb-sg':
            for rule in group['IpPermissions']:
                for cidr in rule['IpRanges']:
                    cidr['CidrIp'] = '<DEMO_IP>/32'
    inventory['redactions'] = ['Personal demo IPv4 address replaced with <DEMO_IP>/32 in ALB ingress only']
    save('inventory', inventory)
    print('Saved real alarm history, fault logs, target health and listener state')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['inspect', 'configure', 'register', 'deploy', 'status', 'collect'])
    parser.add_argument('value', nargs='?')
    args = parser.parse_args()
    if aws('sts', 'get-caller-identity')['Account'] != ACCOUNT:
        raise RuntimeError('Refusing to operate on another account')
    if args.action == 'inspect': inspect()
    elif args.action == 'configure': configure()
    elif args.action == 'register': register(args.value)
    elif args.action == 'deploy': deploy(args.value)
    elif args.action == 'collect': collect()
    else: status(args.value)
