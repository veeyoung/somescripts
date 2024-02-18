set -o errexit
set -o nounset
set -o pipefail
versions=$(kubeadm config images list)
KUBE_VERSION=$(echo "$versions" |grep kube-apiserver |awk -F ':' '{print $NF}')
KUBE_PAUSE_VERSION=$(echo "$versions" |grep pause |awk -F ':' '{print $NF}')
ETCD_VERSION=$(echo "$versions" |grep etcd |awk -F ':' '{print $NF}')
DNS_VERSION=$(echo "$versions" |grep coredns |awk -F ':v' '{print $NF}')

##这是原始仓库名，最后需要改名成这个
GCR_URL=registry.k8s.io

##镜像仓库
DOCKERHUB_URL=registry.aliyuncs.com/google_containers

##这里是镜像列表
images=(
kube-proxy:${KUBE_VERSION}
kube-scheduler:${KUBE_VERSION}
kube-controller-manager:${KUBE_VERSION}
kube-apiserver:${KUBE_VERSION}
pause:${KUBE_PAUSE_VERSION}
etcd:${ETCD_VERSION}
)

for imageName in ${images[@]} ; do
  docker pull $DOCKERHUB_URL/$imageName
  docker tag $DOCKERHUB_URL/$imageName $GCR_URL/$imageName
  docker rmi $DOCKERHUB_URL/$imageName
done

# coredns需要特殊处理
docker pull coredns/coredns:${DNS_VERSION}
docker tag coredns/coredns:${DNS_VERSION} $GCR_URL/coredns/coredns:v${DNS_VERSION}
docker rmi coredns/coredns:${DNS_VERSION}