# Home Assistant integration for SNAPI devices


<p align="center"><img src="https://snapi.com.au/wp-content/uploads/2020/11/SNAPI_LOGO_Black_Large.png" width="350" alt="SNAPI Logo"/></p>


<p align="center">
    <img src="https://snapi.com.au/wp-content/uploads/2022/03/Round-Black-small-662x1024.jpg" height="150" alt="SNAPI Round black"/>
    <img src="https://snapi.com.au/wp-content/uploads/2022/03/Square-Black-small-753x1024.jpg" height="150" alt="SNAPI Square black"/>
    <img src="https://snapi.com.au/wp-content/uploads/2022/03/Small-Black-1024x981.png" height="150" alt="SNAPI Small black"/>

</p>

Retrieve your [SNAPI](https://snapi.com.au/) devices readings in Home Assistant.

*This integration is not affialiated (nor supported) by SNAPI.*




## Installation
### Add custom component:
- [HACS](https://hacs.xyz/): HACS > Integration
    - In the top right menu: "Custom repositories"
    - Repository: https://github.com/philippegabert/snapi
    - Category: Integration
<p align="center"><img src="https://github.com/philippegabert/snapi/blob/b0ce30731a90e44f53e23c7d2966daef44bed0dc/img/custom_repository.png?raw=true" width="350" alt="Custom repository"/></p>
- Download the custom component

### Retrieve SNAPI devices details:
- Login to https://scc.snapi.com.au/
- Select the device you want to monitor
- Get the "Device name" (*device_name in the configuration file*) by selecting id "Reader ID":
<p align="center"><img src="https://github.com/philippegabert/snapi/blob/b0ce30731a90e44f53e23c7d2966daef44bed0dc/img/readerid.png?raw=true" height="100" alt="Reader ID"/></p>

- Get the "Product key" (*product_key in the configuration file*) from the page URL:
<p align="center"><img src="https://github.com/philippegabert/snapi/blob/b0ce30731a90e44f53e23c7d2966daef44bed0dc/img/productkey.png?raw=true" alt="Product key"/></p>


### Configure Home Assistant:
- In the `configuration.yaml` file:
```yaml
sensor:
  - platform: snapi
    username: <SNAPI user name>
    password: <SNAPI user password>
    refresh_frequency: <Minutes between refreshes>
    devices:
      - product_key: <Device product key>
        device_name: <Device "name" (identifier)>
        type: <"gas" or "water">
        friendly_name: <Friendly name for your device.>
        outlier_threshold: <Any delta above this value will be ignored. (See example below)>
```

Example file:
```yaml
sensor:
  - platform: snapi
    username: john
    password: password123
    refresh_frequency: 10 #The integration will refresh the reading every 10 minutes
    devices:
      - product_key: FoH1YE4IxR
        device_name: 831324564391932
        type: gas
        friendly_name: My gas meter
        outlier_threshold: 10 #Example: If previous reading is "00150" m3 and the current reading is 10151m3 (likely faulty), then the reading is ignored
```

### Restart
- Restart Home Assistant


## Entities created
The integration will create 2 entities per device:
- One sensor for the meter reading
    - This sensor also holds an attribute with the URL of the latest picture coming from the device
- One sensor for the battery level of the device

<p align="center"><img src="https://github.com/philippegabert/snapi/blob/main/img/entities.png?raw=true" height="250" alt="Entities"/></p>

