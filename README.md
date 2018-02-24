# OpenStack-Host-Status
通过 zabbix API 获取集群运行记录。
虚拟机的信息从数据库获取，各个节点的运行数据通过zabbix获得。
提供了两种报告格式，一个输出到终端，一个是生成csv文件，可以直接用excel打开。
目前程序的执行效率很低，等待结果的时间有点长，还需要优化。

使用方法：
1. 修改配置文件 conf.cfg
2.  运行
     ```shell
     # python main.py
    ```
3. 查看终端输出，或者report目录下的csv文件
