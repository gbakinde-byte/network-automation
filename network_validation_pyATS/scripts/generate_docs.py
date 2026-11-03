import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pyats.topology import loader

def generate_markdown_docs():
    testbed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../testbed/testbed.yaml'))
    print(f"Loading testbed from: {testbed_path}")
    
    testbed = loader.load(testbed_path)
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../docs'))
    os.makedirs(output_dir, exist_ok=True)

    for name, device in testbed.devices.items():
        print(f"Generating documentation for {name}...")
        try:
            device.connect(init_exec_commands=[], log_stdout=False)
            
            # 1. Parse Interfaces
            try:
                intf_output = device.parse('show ip interface brief')
                interfaces = intf_output.get('interface', {})
            except Exception as e:
                print(f"Warning: Could not parse interfaces for {name}: {e}")
                interfaces = {}

            # 2. Parse Routing Table
            try:
                route_output = device.parse('show ip route')
            except Exception as e:
                print(f"Warning: Could not parse routing table for {name}: {e}")
                route_output = {}

            # Build Markdown Content
            md_content = f"# Network Documentation: {name}\n\n"
            
            # Interfaces Section
            md_content += "## Interface Status\n"
            md_content += "| Interface | IP Address | Status | Protocol |\n"
            md_content += "|-----------|------------|--------|----------|\n"
            
            if interfaces:
                for intf_name, intf_data in interfaces.items():
                    ip = intf_data.get('ip_address', 'Unassigned')
                    status = intf_data.get('status', 'unknown')
                    proto = intf_data.get('protocol', 'unknown')
                    md_content += f"| {intf_name} | {ip} | {status} | {proto} |\n"
            else:
                md_content += "| None Captured | - | - | - |\n"

            # Routing Table Section
            md_content += "\n## Routing Table\n"
            md_content += "| Prefix | Protocol |\n"
            md_content += "|--------|----------|\n"
            
            routes_found = False
            try:
                vrfs = route_output.get('vrf', {})
                for vrf_name, vrf_data in vrfs.items():
                    routes = vrf_data.get('address_family', {}).get('ipv4', {}).get('routes', {})
                    for prefix, r_info in routes.items():
                        proto = r_info.get('source_protocol', 'unknown')
                        md_content += f"| {prefix} | {proto} |\n"
                        routes_found = True
            except Exception:
                pass

            if not routes_found:
                md_content += "| No Routes Captured | - |\n"

            # Write out to docs/{name}.md
            file_path = os.path.join(output_dir, f"{name}.md")
            with open(file_path, 'w') as f:
                f.write(md_content)
                
            print(f"Successfully generated documentation for {name} at {file_path}")
            device.disconnect()
            
        except Exception as e:
            print(f"Failed generating docs for {name}: {e}")

if __name__ == '__main__':
    generate_markdown_docs()