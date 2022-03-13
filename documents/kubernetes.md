# Kubernetes

<font size="5"> Table of contents </font>

<font size="4"> Part 1: Lý thuyết </font>

<font size="3">1. [Architecture](#architecture)</font> 

<font size="3">2. [Pod](#pod)</font>
   <!-- <font size="2">[Pod labels](#pod-labels)</font> \
  <font size="2">[Pod Annotation](#pod-annotation)</font> \
  <font size="2">[Namespace](#namespace)</font> \
  <font size="2">[Pod Deleting](#pod-deleting)</font> \ -->
<font size="3">3. [Controller](#controller)</font>
  <!-- <font size="2">[ReplicationController](#replicationcontroller)</font> \
  <font size="2">[Replicaset](#replicaset)</font> \
  <font size="2">[DaemonSet](#daemonset)</font> \
  <font size="2">[Jobs](#jobs)</font> \
  <font size="2">[CronJob](#cronjob)</font> \ -->
<font size="3">4. [Services](#services)</font>
 <!-- <font size="2"> [ClusterIP](#clusterip)</font> \
  <font size="2">[NodePort](#nodeport)</font> \
  <font size="2">[LoadBalancer](#loadbalancer)</font> \
  <font size="2">[Ingress](#ingress)</font> \ -->
<font size="3">5. [Volume](#volume)</font>
  <!-- <font size="2">[emptyDir](#emptydir)</font> \
  <font size="2">[hostPath](#hostpath)</font> \
  <font size="2">[Cloud Storage](#cloud-storage)</font> \
  <font size="">[PersistentVolumes & PersistentVolumeClaims](#persistentvolumes--persistentvolumeclaims)</font> \
      &nbsp;&nbsp;<font size="2">[Recycling PersistentVolume](#recycling-persistentvolume) </font> \
      &nbsp;&nbsp;<font size="2">[Dynamic Provisioning PersistentVolume](#dynamic-provisioning-persistentvolume) </font> \ -->
<font size="3">6. [ConfigMap & Secret](#configmap--secret)</font>
  <!-- <font size="2">[env](#env)</font> \
  <font size="2">[ConfigMap](#configmap)</font> \
 <font size="2"> [Configmap with file](#configmap-with-file)</font> \
 <font size="2"> [Secret](#secret)</font> \ -->
<font size="3">7. [Automatic scaling](#automatic-scaling)
  <!-- <font size="2">[Horizontal Pod Scaling](#horizontal-pod-scaling) </font>  -->

<font size="4"> Part 2: Triển khai </font> \
8. [Deploy EKS cluster with eksctl](#deploy-eks-cluster-with-eksctl) 

<div class="page"/>


[comment]: <> (End Architecture page)

[comment]: <> (Start Pod page)
<div class="page"/>


[comment]: <> (End Pod page)

[comment]: <> (Start Controller page)

<div class="page"/>



[comment]: <> (End Controller page)


[comment]: <> (Start Service page)
<div class="page"/>


[comment]: <> (End Service page)


[comment]: <> (Start Volume page)
<div class="page"/>



[comment]: <> (End Configmap&Secret page)

[comment]: <> (Start Automatic scaling page)
<div class="page"/>

# Automatic scaling

Khi nói về scaling, chúng ta có 2 kiểu scaling đó là horizontal scaling và vertical scaling

- horizontal scaling: tức là tăng số lượng worker đang xử lý công việc hiện tại lên nhiều hơn.
- vertical scaling: tức là thay vì thêm số lượng thì ta tăng thêm resource của worker node.

Trong K8S, chúng ta có thể horizontal scale bằng cách thay đổi số `replicas` trong Replicaset hoặc Deployment và vertical scale bằng cách tăng resource request và limit khi khởi tạo Pod.  Tuy nhiên, các cách này chúng ta phải xử lý một cách thủ công. Rõ ràng đây không phải là một cách hay bởi vì chúng ta không thể ngồi theo dõi hệ thống cả ngày xong rồi gõ câu lệnh scale khi cần.

→ K8S sẽ hỗ trợ chúng ta monitor và scale up/down hệ thống tự động khi nhận thấy có sự thay đổi về các metrics(CPU, RAM, ...) trong k8s cluster. Ngoài ra, khi sử dụng k8s trên nền tảng cloud, k8s còn hỗ trợ tự động thêm worker node khi cần thiết.

## Horizontal Pod Scaling

- Horizontal pod scaling là cách tự động tăng/giảm số lượng `replicas` trong các scalable controller(Replicaset, Deployment, ...)
- Công việc này được thực hiện bởi Horizontal Controller khi chúng ta tạo ra một HorizontalPodAutoscaler(HPA) resource.
- Controller này sẽ định kỳ kiểm tra các pod metrics và tính toán số lượng `replicas` phù hợp dựa trên giá trị của pod metrics hiện tại và giá trị metrics chúng ta chỉ định trong HPA, sau đó nó thay đổi trường `replicas` trong các resource (Replicaset, Deployment, StatefulSet)
1. Quá trình auto scaling
- Quá trình auto scaling được chia làm 3 giai đoạn:
    - Thu thập metrics của các pod được quản lý bởi resource mà chúng ta chỉ định trong HPA.
    - Tính toán số lượng pod cần thiết dựa vào metrics đã thu thập được
    - Update trường `replicas`
1. Thu thập metrics
    - Horizontal controller sẽ không trực tiếp thu thập các metrics mà nó sẽ lấy qua 1 thằng khác, gọi là metrics server.
    - Ở trên mỗi worker node, sẽ có một thằng agent gọi là cAdvisor, có nhiệm vụ thu thập metrics của pod và worker node, sau đó những metrics này được tổng hợp ở metrics server và Horizontal controller sẽ lấy metrics qua nó.
    
    ![Metric collector](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/3b34fb36-183a-467d-ad3a-579d6bd441ce/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220309%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220309T173107Z&X-Amz-Expires=86400&X-Amz-Signature=53e5b39f6add8d472b757242a18da64f17524f9e475f231dce670fd1c8ca81ad&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)
    
2. Tính toán số pod
- Sau khi có được metrics, Horizontal Controller sẽ tiến hành bước tính toán số pod cần thiết dựa vào các metrics ta define trong HPA.
- Nó sẽ cần tính toán dựa vào 2 thằng metrics phía trên, với input là một nhóm pod metrics và output là số lượng pod cần để scale.
    - Nếu chỉ có 1 single metric, việc tính toán dựa vào công thức
    
    ```yaml
    desiredReplicas = ceil[currentReplicas * ( currentMetricValue / desiredMetricValue )]	
    ```
    
    Ví dụ nếu currentMetric là 200m, giá trị desiredMetric là 100m, currentReplicas là 2 thì 
    
    ```yaml
    disiredReplicas = ceil(2 * (200m/100m)) = 4
    ```
    
    Số `replicas` được scale từ 2 → 4.
    
    - Nếu sử dụng nhiều hơn 1 metrics, việc tính toán cũng khá đơn giản
    
    ```yaml
    disiredReplicas = max(ceil(sum(metric_one,metric_two,...) / disiredMetric), currentReplicas) 
    ```
    
    Ví dụ chúng ta sử dụng CPU và QPS(Queue-per-second)
    
    ![Example cpu and qps](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/718a7086-126b-472d-bd71-39b94ea9d721/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220309%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220309T173031Z&X-Amz-Expires=86400&X-Amz-Signature=684b12692074ba458cce54ed66acb9e2c53bbf2da84e0628c2414eece4569814&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)
    

c. Cập nhật `replicas`

- Bước cuối trong quá trình auto scaling đó là cập nhật lại số replicas theo như tính toán.
- Horizontal Controller sẽ
- Hiện tại, auto scaling mới hỗ trợ các resource sau:
    - Replicaset(ReplicaController)
    - Deployment
    - StatefulSet
1. Scaling theo CPU
- Giờ chúng ta sẽ tạo Deployment và một HPA với cấu hình sử dụng CPU metrics.
    - Tạo deployment với replicas là 3
        
        ```yaml
        # kubia-deployment.yaml
        
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: kubia-deployment
        spec:
          replicas: 3
          selector:
            app: kubia
          template:
            metadata:
              labels:
                app: kubia
            spec:
              containers:
                - image: luksa/kubia:v1
                  name: nodejs
                  resources:
                    requests:
                      cpu: 100m # 100 milicore
        ```
        
    - Tạo HPA, với Utilization
        
        ```yaml
        # hpa.yaml
        
        apiVersion: autoscaling/v2
        kind: HorizontalPodAutoscaler
        metadata:
          name: kubia-hpa
        spec:
          scaleTargetRef:
            apiVersion: apps/v1
            kind: Deployment
            name: kubia-deployment
          minReplicas: 1
          maxReplicas: 3
          metrics:
            - type: Resource
              resource:
                name: cpu
                target: 
                  type: Utilization
                  averageUtilization: 30
        ```
        
    - Kiểm tra thử
        
        ```bash
        $ kubectl create -f kubia-deployment.yaml
        
        $ kubectl get deployment
        NAME               READY   UP-TO-DATE   AVAILABLE   AGE
        kubia-deployment   3/3     3            3           69s
        
        $ kubectl create -f hpa.yaml
        
        $ kubectl get hpa
        NAME        REFERENCE                     TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
        kubia-hpa   Deployment/kubia-deployment   <unknown>/30%   1         3         0          4s
        ```
        
        Nếu thấy Target là `unknow/30%` thì phải chờ để cAdvisor có thể thu thập metrics.
        
    - check lại
        
        ```bash
        NAME        REFERENCE                     TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
        kubia-hpa   Deployment/kubia-deployment   0%/30%    1         3         3          12m
        ```
        
        Lúc này cAdvisor đã report dữ liệu lên metric-server, và Horizontal Controller đã lấy được data. 
        
    - kiểm tra deployment
        
        ```bash
        $ kubectl get deployment
        NAME               READY   UP-TO-DATE   AVAILABLE   AGE
        kubia-deployment   1/1     1            1           18m
        ```
        
        Như chúng ta có thể thấy trước khi tạo HPA, replicas là 3, bây giờ đã scale down xuống 1, do HPA đã kiểm tra thấy không có CPU nào được sử dụng → tự động scale down về minimum để giảm chi phí.
        
    - trigger scale up
        
        Trước tiên, chúng ta phải expose service để client có thể gọi vào
        
        ```bash
        $ kubectl expose deployment kubia --port=80 --target-port=8080
        ```
        
        Lúc này ta sẽ dùng lệnh `watch` để xem quá trình scale up
        
        ```bash
        $ watch -n 1 kubectl get hpa, deployment
        ```
        
        Mở 1 terminal khác rồi chạy command, nó có tác dụng là liên tục send request vào pod.
        
        ```bash
        $ kubectl run -it --rm --restart=Never loadgenerator --image=busybox -- sh -c "while true; do wget -O - -q http://kubia; done"
        ```
        
         Lúc này quay lại terminal có câu lệnh watch, chúng ta có thể thấy `TARGET` đã vượt quá 30% và pod được tự động scale up theo số number tính toán được ở đây là 3.
        
        ```bash
        NAME                                            REFERENCE                     TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
        horizontalpodautoscaler.autoscaling/kubia-hpa   Deployment/kubia-deployment   79%/30%   1         3         3          38m
        
        NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
        deployment.apps/kubia-deployment   3/3     3            3           42m
        ```
[comment]: <> (End Automatic scaling page)

[comment]: <> (Start EKS page)
<div class="page"/>

# Deploy EKS cluster with eksctl

Dưới dây là cách triển khai k8s cluster (eks cluster) trên aws với eksctl

1. Cài đặt kubectl: [https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html)
2. Cài đặt eksctl: [https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html](https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html)
3. Tạo EKS cluster

Để tạo eks cluster với tên `my-cluster` ở region `ap-southeast-1` , chúng ta có thể chạy command sau: (—without-nodegroup: không khởi tạo worker node)

```bash
$ eksctl create cluster --name my-cluster --region ap-southeast-1 --without-nodegroup
```

 Quá trình khởi tạo mất 1 vài phút, khi xuất hiện output log như bên dưới → tạo eks cluster thành công.

```bash
[✓]  EKS cluster "my-cluster" in "ap-southeast-1" region is ready
```

1. Tạo worker node(nodegroup)
Để tạo worker node, chúng ta có thể dùng 2 cách là : dùng qua cli command hoặc tạo file config
    1. Dùng command
        
        ```bash
        $ eksctl create nodegroup \
        				--cluster my-cluster \
        				--region ap-southeast-1 \
        				--name my-workers \
        				--node-type t3.medium \
                --nodes 2 \
        				--ssh-access \
        				--ssh-public-key my-key
        ```
        
        Sau khi chạy command phía trên sẽ tạo 2 worker node(ec2 - t3.medium) cho k8s cluster `my-cluster`
        
    2. Dùng template
        
         Tạo template file `eks-nodegroup.yaml`
        
        ```yaml
        apiVersion: eksctl.io/v1alpha5
        kind: ClusterConfig
        metadata:
        	name: my-cluster
        	region: ap-southeast-1
        managedNodeGroups:
        - name: my-workers
        	amiFamily: Ubuntu2004
        	instanceType: t3.medium
        	desiredCapacity: 2
        	ssh:
        		publicKeyName: my-key
        ```
        
        Chạy command để apply 
        
        ```bash
        $ eksctl create nodegroup --config-file eks-nodegroup.yaml
        ```
        
2. Tạo kubeconfig

Để remote access vào eks cluster → tạo kubeconfig trên PC. Chúng ta chạy lệnh sau:

```bash
$ aws eks update-kubeconfig --region ap-southeast-1 --name my-cluster
```

1. Kiểm tra k8s cluster-info

```bash
# check cluster
$ kubectl cluster-info

# check nodes
$ kubectl get nodes
```
[comment]: <> (End EKS page)