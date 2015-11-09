import boto.ec2


class Ec2(object):
    def __init__(self):
        self.ec2_client = boto.connect_ec2()

    def instances_dns_names(self):
        names = []
        reservations = self.ec2_client.get_all_instances()
        for reservation in reservations:
            for instance in reservation.instances:
                names.append(instance.dns_name)
        return names
