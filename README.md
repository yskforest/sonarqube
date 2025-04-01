# soanrqube

## usage
```bash
sudo sysctl -w vm.max_map_count=262144

docker compose up -d

# set
sudo sh -c 'echo "vm.max_map_count=262144" >> /etc/sysctl.conf'

# check
sysctl vm.max_map_count

wget https://github.com/SonarOpenCommunity/sonar-cxx/releases/download/cxx-2.2.0/sonar-cxx-plugin-2.2.0.1110.jar
```
