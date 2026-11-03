from pyats.topology import loader
from pprint import pprint

def inspect_device_structures():
    # Load your testbed file
    testbed_path = 'testbed/testbed.yaml'
    testbed = loader.load(testbed_path)
    
    # Pick your primary target device from the testbed
    device_name = list(testbed.devices.keys())[0]
    device = testbed.devices[device_name]
    
    print(f"Connecting to {device_name} for structure inspection...")
    device.connect(init_exec_commands=[], log_stdout=False)
    
    commands = [
        'show ip interface brief',
        'show ip ospf neighbor',
        'show ip route'
    ]
    
    for cmd in commands:
        print(f"\n{'='*20} PARSED STRUCTURE: {cmd} {'='*20}")
        try:
            parsed_output = device.parse(cmd)
            pprint(parsed_output, width=120, indent=2)
        except Exception as e:
            print(f"Could not parse '{cmd}': {e}")
            
    device.disconnect()

if __name__ == '__main__':
    inspect_device_structures()
