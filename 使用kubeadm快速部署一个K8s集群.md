## 1. 安装要求

在开始之前，部署Kubernetes集群机器需要满足以下几个条件：

- 硬件配置：2GB或更多RAM，2个CPU或更多CPU，硬盘30GB或更多
- 可以访问外网，需要拉取镜像，如果服务器不能上网，需要提前下载镜像并导入节点
- 禁止swap分区

## 2. 准备环境

| 角色   | IP           |
| ------ | ------------ |
| master | 192.168.1.10 |
| node1  | 192.168.1.11 |
| node2  | 192.168.1.12 |

```
# 关闭防火墙
systemctl stop firewalld
systemctl disable firewalld

# 关闭selinux
sed -i 's/enforcing/disabled/' /etc/selinux/config  # 永久
setenforce 0  # 临时

# 关闭swap
swapoff -a  # 临时
sed -ri 's/.*swap.*/#&/' /etc/fstab    # 永久

# 根据规划设置主机名
hostnamectl set-hostname <hostname>

# 在master添加hosts
cat >> /etc/hosts << EOF
192.168.1.10 master
192.168.1.12 node1
192.168.1.13 node2
EOF

# 禁用iptables
systemctl stop iptables && systemctl disable iptables

# 将桥接的IPv4流量传递到iptables的链
cat > /etc/sysctl.d/k8s.conf << EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
sysctl --system -p # 生效

# 加载网桥过滤模块
modprobe br_netfilter

# 时间同步
ntpdate time.windows.com
```

## 3. 所有节点安装Docker/kubeadm/kubelet

Kubernetes默认CRI（容器运行时）为Docker，因此先安装Docker。

### 3.1 安装Docker

```
$ apt-get install ca-certificates curl gnupg lsb-release
$ curl -fsSL http://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg |apt-key add -
$ add-apt-repository "deb [arch=amd64] http://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"
$ apt-get install docker-ce docker-ce-cli containerd.io
```

#Docker 在默认情况下使用Vgroup Driver为cgroupfs，而Kubernetes推荐使用systemd来替代cgroupfs
```
[root@master ~]# mkdir /etc/docker
[root@master ~]# cat <<EOF> /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "registry-mirrors": ["https://1onbiey9.mirror.aliyuncs.com"]
}
EOF
[root@master ~]# systemctl restart docker
```

### 3.2 添加阿里云软件源

```
$ apt-get update && apt-get install -y ca-certificates curl software-properties-common apt-transport-https curl
$ curl -s https://mirrors.aliyun.com/kubernetes/apt/doc/apt-key.gpg |apt-key add -
$ apt-add-repository "deb https://mirrors.aliyun.com/kubernetes/apt/ kubernetes-xenial main"
```

### 3.3 安装kubeadm，kubelet和kubectl

```
$ apt-get install -y kubelet kubeadm kubectl
$ systemctl enable kubelet
```

# 4. 配置kubelet的cgroup
#编辑/etc/sysconfig/kubelet, 添加下面的配置
```
KUBELET_CGROUP_ARGS="--cgroup-driver=systemd"
```
在安装kubernetes集群之前，必须要提前准备好集群需要的镜像，所需镜像可以通过下面命令查看
```
[root@master ~]# kubeadm config images list
```

## 4. 部署Kubernetes Master

可以加上--v=6获取详细日志,便于排错  
kubeadm config print init-defaults查看默认配置文件  
# 创建集群
```
[root@master ~]# kubeadm init \
--apiserver-advertise-address=192.168.1.10 \
--image-repository registry.aliyuncs.com/google_containers \
--service-cidr=10.96.0.0/12 \
--pod-network-cidr=10.244.0.0/16
```
# 创建必要文件
```
[root@master ~]# mkdir -p $HOME/.kube
[root@master ~]# sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
[root@master ~]# sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

## 5. 加入Kubernetes Node

在192.168.1.11/12（Node）执行。

向集群添加新节点，执行在kubeadm init输出的kubeadm join命令：

```
$ kubeadm join 192.168.1.11:6443 --token esce21.q6hetwm8si29qxwn \
    --discovery-token-ca-cert-hash sha256:00603a05805807501d7181c3d60b478788408cfe6cedefedb1f97569708be9c5
```

默认token有效期为24小时，当过期之后，该token就不可用了。这时就需要重新创建token，操作如下：

```
kubeadm token create --print-join-command
```

## 6. 部署CNI网络插件

```
wget https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

默认镜像地址无法访问，sed命令修改为docker hub镜像仓库。

```
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

kubectl get pods -n kube-system
NAME                          READY   STATUS    RESTARTS   AGE
kube-flannel-ds-amd64-2pc95   1/1     Running   0          72s
```

## 7. 测试kubernetes集群

在Kubernetes集群中创建一个pod，验证是否正常运行：

```
$ kubectl create deployment nginx --image=nginx
$ kubectl expose deployment nginx --port=80 --type=NodePort
$ kubectl get pod,svc
```

访问地址：http://NodeIP:Port  




