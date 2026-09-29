# Ansible OSPF Automation

Automating OSPF configuration on Cisco routers using Ansible, Jinja2 templates, and Ansible roles.

This project was built as a hands-on network automation project to practice moving from manually configuring network devices to managing their configuration with code.

## Project Overview

The goal of this project is to automate the configuration of OSPF across multiple Cisco routers.

The playbook handles:

- Interface configuration
- IP addressing
- OSPF interface configuration
- OSPF router IDs
- OSPF areas
- Passive interfaces
- Hostname configuration
- Configuration templating with Jinja2
- Ansible role structure
- Idempotent configuration

The lab was built and tested in GNS3.

## Technologies Used

- Ansible
- Cisco IOS
- Jinja2
- YAML
- GNS3
- Python

## Lab Topology

The project uses three Cisco routers:

```text
        R1
       /  \
      /    \
    R2------R3

ansible-ospf-automation/
│
├── ansible.cfg
├── inventory/
│   ├── group_vars/
│   │   └── routers.yml
│   ├── host_vars/
│   │   ├── R1.yaml
│   │   ├── R2.yaml
│   │   └── R3.yaml
│   └── hosts.ini
│
├── playbooks/
│   ├── deploy.yaml
│   └── verify.yaml
│ 
└── roles/
    └── ospf_deploy/
        ├── tasks/
        │   └── main.yaml
        ├── templates/
        │   └── ospf_config.j2
        └── ...

How It Works
1. Inventory

The Ansible inventory defines the routers that Ansible will manage.

R1
R2
R3

2. Variables

Router-specific information is stored in variables rather than hard-coded into the configuration template.

Example:

ospf_interface: GigabitEthernet0/2
ip_address: 11.0.0.1
subnet_mask: 255.255.255.0
ospf_process: 1
ospf_area: 0
ospf_router_id: 1.1.1.1

3. Jinja2 Template

The configuration is generated using a Jinja2 template.

hostname {{ inventory_hostname }}

interface {{ ospf_interface }}
 ip address {{ ip_address }} {{ subnet_mask }}
 ip ospf {{ ospf_process }} area {{ ospf_area }}

router ospf {{ ospf_process }}
 router-id {{ ospf_router_id }}

{% for intf in passive_interfaces | default([]) %}
 passive-interface {{ intf }}
{% endfor %}

This allows the same template to be used across multiple routers with different variables.

4. Ansible Role

The OSPF configuration is organized into an Ansible role.

The role is responsible for applying the rendered configuration to the Cisco routers.

5. Idempotency

One of the main things I focused on during this project was idempotency.

After the configuration has been applied, running the playbook again should not continuously report changes if the devices already match the intended configuration.

Example:

R1  changed=0
R2  changed=0
R3  changed=0

This was also one of the more challenging parts of the project because the playbook initially continued reporting configuration changes.

Running the Project
Prerequisites

You will need:

Ansible
- Python 3
- Ansible
- GNS3 or compatible Cisco IOS devices
- SSH connectivity to the routers
- The `cisco.ios` Ansible collection

## Installation

### 1. Install Ansible

Install Ansible using your preferred method.

For example, on Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ansible

Verify the installation:

ansible --version

2. Clone the repository

git clone https://github.com/gbakinde-byte/network-automation/ansible-ospf-automation.git
cd ansible-ospf-automation

3. Install the required Ansible collection

The project uses the cisco.ios collection.

Install it using the included requirements.yml file:

ansible-galaxy collection install -r requirements.yml
4. Configure the inventory

Update the inventory with the IP addresses and connection details for your routers.

5. Test connectivity
ansible all -m ping

6. Run the playbook
ansible-playbook playbooks/deploy.yml

After deployment, OSPF can be verified using the verify.yaml file or directly on the routers.

Useful Cisco IOS commands include:

show ip ospf neighbor
show ip ospf interface
show ip ospf
show ip route ospf
show running-config

The expected result is for the routers to form OSPF neighbor relationships and learn OSPF routes.

What I Learned

This project helped me understand several concepts beyond simply writing an Ansible playbook.

Ansible Roles

I learned how to organize network automation into reusable roles instead of keeping everything inside one large playbook.

Jinja2

I used Jinja2 variables and loops to generate device-specific configurations from a common template.

Network Automation

The project gave me practical experience moving from manually entering Cisco IOS commands to describing the desired configuration and allowing Ansible to apply it.

Idempotency

I learned that a successful playbook run is not enough.

A good automation workflow should also be predictable when it is run repeatedly.

Troubleshooting

I also had to troubleshoot issues involving configuration differences, Ansible behavior, and connectivity within the GNS3 lab.

Future Improvements

Possible improvements include:

Automating more OSPF parameters
Supporting multiple network vendors
Adding configuration validation
Adding automated pre-checks and post-checks
Adding pyATS verification
Adding CI/CD for the Ansible project
Expanding the topology
Automating network documentation
Status

🚧 Work in progress

The project is functional, but I plan to continue improving the automation, verification, and multi-vendor capabilities.

Author

Goodness

Network Engineer | Python & Network Automation