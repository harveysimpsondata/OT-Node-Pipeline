# Kafka

### Install Kafka
```bash
wget https://downloads.apache.org/kafka/3.5.0/kafka_2.13-3.5.0.tgz
```
### Unzip Kafka
```bash
tar -xzf kafka_2.13-3.5.0.tgz
```
### Rename Kafka
```bash
mv kafka_2.13-3.5.0 kafka
```
run this command to configure kafka server and uncomment advertised.listeners=PLAINTEXT://YOUR_PUBLIC_IP:9092 and replace with your IP
```bash
sudo nano kafka/config/server.properties
```

### Start Zookeeper
```bash
cd kafka
bin/zookeeper-server-start.sh config/zookeeper.properties
```

Start Kafka Server
Open another terminal window and ssh into ec2 instance. Run the following command to increase memory for server. This will allocate some amount of memory to kafka server.
```bash
export KAFKA_HEAP_OPTS="-Xmx256M -Xms128M"
```
Then run the following command to start kafka server

```bash
cd kafka
bin/kafka-server-start.sh config/server.properties
```

### Create Topic
```bash
cd kafka
bin/kafka-topics.sh --create --topic otnodelogs --bootstrap-server YOUR_PUBLIC_IP:9092 --replication-factor 1 --partitions 1
```

### List Topics
```bash
export CONFLUENT_USERNAME=your-api-key
export CONFLUENT_PASSWORD=your-api-secret
```