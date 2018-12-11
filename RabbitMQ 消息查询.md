RabbitMQ 消息查询

查看消息

```shell
[root@mq ~]# rabbitmqctl list_queues messages name | grep -v ^0
710 notifications.info
```

使用 rabbitmqadmin

```shell
[root@mq ~]# rabbitmqadmin -P 18890 -H 10e131e73e112 get queue=notifications.info
```

清除一个队列

```shell
[root@mq ~]# rabbitmqctl purge_queue notifications.info
```

http://www.rabbitmq.com/management-cli.html