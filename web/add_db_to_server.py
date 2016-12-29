#!/usr/bin/env python


def add_db_to_server(filename, task_dict):
    import yaml
    import sys

    with open(filename, 'r') as stream:
        try:
            x = yaml.load(stream)
            for y in x:
                if 'tasks' in y:
                    if task_dict not in y['tasks']:
                        y['tasks'].append(task_dict)
                else:
                    y['tasks'] = [task_dict]

            with open(filename, 'w') as f:
                yaml.dump(x, f, default_flow_style=False)

        except yaml.YAMLError as exc:
            print(exc)

#add_db_to_server('192-test.yaml', {'postgresql_db': 'name=test4345', 'tags':'test4345'} )
