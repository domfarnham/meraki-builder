# Created by Dom Farnham
import requests
import csv
import json
import sys

api_key = {"X-Cisco-Meraki-API-Key": sys.argv[1]}
shard = sys.argv[2]
org_id = sys.argv[3]
api_url = f'https://{shard}.meraki.com/api/v0/organizations/{org_id}/networks'

sites_csv = open('sites.csv')
sites_read = csv.reader(sites_csv)
sites_list = list(sites_read)
sites_list.pop(0)

for site in sites_list:
    appliance_name = site[0]
    clone_from_id = site[1]
    vlan_id = site[2]
    vlan_name = site[3]
    appliance_ip = site[4]
    vlan_subnet = site[5]
    appliance_serial = site[6]
    tags = site[7]
    timeZone = site[8]
    # Create network
    create_network_data = {
        "name": appliance_name,
        "type": "appliance",
        "tags": tags,
        "timeZone": timeZone,
        "copyFromNetworkId": clone_from_id
    }
    try:
        create_network_response = requests.post(f"{api_url}", headers=api_key, json=create_network_data)
        if create_network_response.status_code != 201:
            raise ValueError(f'Create network status is {create_network_response.status_code}')
    except ValueError as err:
        print(err.args)
        sys.exit()
    # Store network id of the new network
    network_id = create_network_response.json()['id']
    # Claim and assign device to the new network
    claim_data = {"serial": appliance_serial}
    try:
        claim_response = requests.post(f"{api_url}/{network_id}/devices/claim", headers=api_key, json=claim_data)
        if claim_response.status_code != 200:
            raise ValueError(f'Claim status is {claim_response.status_code}')
    except ValueError as err:
        print(err.args)
        sys.exit()
    # Update VLAN
    update_vlan_data = {
        "name": vlan_name,
        "applianceIp": appliance_ip,
        "subnet": vlan_subnet
    }
    try:
        update_vlan_response = requests.put(
            f"{api_url}/{network_id}/vlans/{vlan_id}", headers=api_key, json=update_vlan_data)
        if update_vlan_response.status_code != 200:
            raise ValueError(f'Update VLAN status is {update_vlan_response.status_code}')
    except ValueError as err:
        print(err.args)
        sys.exit()
    # Update S2S VPN Settings
    # Add config to dictionary before executing
    update_vpn_data = {}
    try:
        update_vpn_response = requests.put(f"{api_url}/{network_id}/siteToSiteVpn", headers=api_key, json=update_vpn_data)
        if update_vpn_response.status_code != 200:
            raise ValueError(
                f'Update VPN status is {update_vpn_response.status_code}')
    except ValueError as err:
        print(err.args)
        sys.exit()
    print(f"{create_network_data['name']} built successfully")
