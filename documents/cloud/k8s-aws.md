# K8S on AWS(AWS EKS)

## 1. Deploy eks cluster

Dưới đây là hướng dẫn các bước để triển khai k8s cluster bằng eksctl:

Kịch bản: User Alice(IAM User) trong Account A sử dụng role từ Account B để tạo k8s cluster service trên Account B.

![AssumeRole](../images/aws-eks-assume-role.png)

### 1.1 Cài đặt tools:
- aws-cli: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- kubectl: https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html
- eksctl: https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html
- awsume: https://awsu.me/general/quickstart.html

### 1.2 Configure AWS Alice credentials:
- Đầu tiên, trên account A cần tạo một IAM User(ví dụ ở đây tên là Alice), sau đó lấy được aws credentials là `Access Key` và `Access Secret`.
- Tiếp theo ta cần config credentials này vào dưới local để dùng aws-cli, chúng ta dùng command:
    ```bash
    $ aws configure

    AWS Access Key ID [None]: <your_access_key>
    AWS Secret Access Key [None]: <your_access_secret>
    Default region name [None]: ap-southeast-1
    Default output format [None]: json
    ```
    *Note*: Có thể tham khảo các cách config credentials khác [ở đây](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)

-  Sau khi config credentials, ta cần verify aws và aws user
    ```bash
        $ aws --version # check verrsion
        aws-cli/2.4.13 Python/3.8.8 ...

        $ aws sts get-caller-identity # check identity
        {
            "UserId": "XXX",
            "Account": "XXX",
            "Arn": "arn:aws:iam::xxx:user/xxx"
        }
    ```
    Như vậy là OK, chúng ta đã config xong credentials của user Alice trên terminal.

### 1.3 Configure Cross IAM Role:
-  Trên account B, chúng ta tạo một cross account IAM role với external id là Account's ID A.

    *Tips*: không nên enable MFA để dễ dàng cho việc switch role trên cli.

- Bước tiếp theo, chúng ta cần lưu lại ARN Role của Cross IAM Role vừa tạo.

- Lúc này, chúng ta cần mở file aws credentials trên PC tại đường dẫn `~/.aws/credentials`. Chúng ta sẽ thấy nội dung như sau:
    ```
    [default]
    aws_access_key_id = xxx
    aws_secret_access_key = xxx
    ```

    Đây chính là `Access Key` và `Access Secret` của user Alice vừa config ở trên

- Chúng ta sẽ append đoạn config dưới đây vào file credentials
    ```
    [<profile_name>]
    region = ap-southeast-1
    role_arn = <role_arn>
    source_profile = default
    ```
    *profile_name*: đặt tuỳ ý. dùng để khi switch role trên cli.\
    *role_arn*: là ARN Role của Cross IAM Role vừa tạo ở bước trên.\
    *source_profile*: có giá trị là `default`, tức là profile name cross account mà cụ thể là profile name của account user Alice, tức là giá trị `default` như bên trên.

- Switch role trên cli \
    Giả sử đặt profile_name vừa thêm vào là `account-b`. Chúng ta sẽ switch role từ user Alice trong account A sang account B bằng câu lệnh:
    ```
    $ asume account-b
    [account-b] Role credentials will expire 2022-03-10 22:00:17
    ```
    *Lưu ý*: session này chỉ tồn tại trong vòng 1h.

- Kiểm tra identity với command:
    ```
    $ aws sts get-caller-identity # check identity
    {
        "UserId": "<YYYY>",
        "Account": "<YYYY>",
        "Arn": "arn:aws:iam::<yyy>:user/<yyy>"
    }
    ```

    Lúc này đã thực hiện switch role thành công trên cli, chúng ta có thể truy xuất vào các dịch vụ aws trên account B với permission tương ứng.

- Assign permission vào role

    Tiếp theo chúng ta phải add policy vào role này để có quyền deploy trên eks cluster.

    Cần add ít nhất những policy vào role (tham khảo tại đây https://eksctl.io/usage/minimum-iam-policies/). Policy nào không có sẵn thì tạo inline policy.


### 1.4 Deploy eks cluster by eksctl
Sau khi cấu hình, chúng ta sẽ triển khai eks cluster bằng eksctl

- Bước 1: Switch role sang account B
    ```bash
    $ awsume account-b
    ```

- Bước 2: Tạo cluster 

    Tạo eks cluster với name là `my-cluster` ở region `ap-southeast-1` và không khởi tạo nodegroups. Chúng ta có thể chạy command sau:

    ```bash
    $ eksctl create cluster --name my-cluster --region ap-southeast-1 --without-nodegroup
    ```

    Quá trình khởi tạo mất một vài phút, khi terminal xuất hiện output log như bên dưới thì eks cluster đã được khởi tạo thành công
    ```
    [✓]  EKS cluster "my-cluster" in "ap-southeast-1" region is ready
    ```

- Bước 3: Tạo workner node 

    Trong aws, workernode được gọi là nodegroup. Để tạo nodegroups cho cluster, chúng ta có thể sử dụng một trong hai cách sau:\
    -  Dùng command
        ```
        $ eksctl create nodegroup \
                    --cluster my-cluster \
                    --region ap-southeast-1 \
                    --name my-workers \
                    --node-type t3.medium \
                    --nodes 2 \
                    --ssh-access \
                    --ssh-public-key my-key
        ```
    - Dùng file config \
        Đầu tiên tạo file config có tên `eks-nodegroup.yaml`
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
        Chạy command để tạo nodegroup
        ```bash
        $ eksctl create nodegroup --config-file eks-nodegroup.yaml
        ```
    Kết quả đều là tạo ra 2 worker node (là các EC2 instance) có cấu hình `t3.medium`.

- Bước 4: Tạo kubeconfig
Sau khi tạo worker node, một hệ thống k8s đã được triển khai thành công trên aws. Để có thể truy cập vào cluster này, chúng ta cần config dưới máy client bằng câu lệnh:

    ```bash
    $ aws eks update-config --region ap-southeast-1 --name my-cluster
    ```

- Bước 5: Kiểm tra cluster info từ client

    ```bash
    # kiểm tra cluster
    $ kubectl cluster-info

    # kiểm tra số worker node
    $ kubectl get nodes
    ```

## 2. Deploy StorageClass

- Để triển khai StorageClass trên eks, chúng ta có thể sử dụng config sau

    ```yaml
    # gp2-storage-class.yaml

    kind: StorageClass
    apiVersion: storage.k8s.io/v1
    metadata:
        name: gp2
        annotations:
            storageclass.kubernetes.io/is-default-class: "true"
    provisioner: kubernetes.io/aws-ebs
    parameters:
        type: gp2
        fsType: ext4 
    ```

- Tạo storage class

    ```bash
    $ kubectl create -f gp2-storage-class.yaml
    storageclass "gp2" created
    ```
    
- Tiếp theo, chúng ta sẽ sử dụng storage class vừa được khởi tạo để tạo một PersistentVolumeClaim 
    
    ```yaml
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
        name: example
    spec:
        resources:
            requests:
                storage: 5Gi
    accessModes:
        - ReadWriteOnce
    storageClassName: gp2
    ```
- Cuối cùng, PersistentVolumeClaim được sử dụng khi tạo pod.
- Link tài liệu tham khảo: https://docs.aws.amazon.com/eks/latest/userguide/storage-classes.html

## 3. Deploy AWS Load Balancer

- Bước 1: Switch role
    ```bash
    awsume account-b
    ```

- Bước 2: Tạo IAM Policy

    a. Download policy template
    ```bash
    $ curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.4.0/docs/install/iam_policy.json
    ```

    b. Tạo IAM Policy
    ```bash
    aws iam create-policy \
        --policy-name AWSLoadBalancerControllerIAMPolicy \
        --policy-document file://iam_policy.json
    ```

    Save giá trị `arn` để làm bước tiếp theo.

- Bước 3: Tạo 1 OIDC provider

    ```
    $ eksctl utils associate-iam-oidc-provider --cluster <your_cluster_name> --approve
    ```

- Bước 4: Tạo IAM role.
    ```bash
    eksctl create iamserviceaccount \
        --cluster=<your_cluster_name> \
        --namespace=kube-system \
        --name=aws-load-balancer-controller \
        --attach-policy-arn=<arn_policy> \
        --override-existing-serviceaccounts \
        --approve
    ```

- Bước 5: Cài đặt AWS Loadbalancer Controller

    a. Install Helm: https://docs.aws.amazon.com/eks/latest/userguide/helm.html
    
    b. Add repository
    ```
    $ helm repo add eks https://aws.github.io/eks-charts
    ```

    c. Update local repo
    ```
    $ helm repo update
    ```

    d. Cài đặt loadbalancer lên cluster
    ```
    helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
        -n kube-system \
        --set clusterName=<your_cluster_name> \
        --set serviceAccount.create=false \
        --set serviceAccount.name=aws-load-balancer-controller 
    ```

- Bước 6: Verify loadbalancer controller
    ```
    $ kubectl get deployment -n kube-system aws-load-balancer-controller

    NAME                           READY   UP-TO-DATE   AVAILABLE   AGE
    aws-load-balancer-controller   2/2     2            2           84s
    ```

- Bước 7: Bây giờ chúng ta có thể tạo Service resource với LoadBalancer hoặc Ingress

    ```yaml
    apiVersion: v1
    kind: Service
    metadata:
        name: example-loadbalancer
    spec:
        type: LoadBalancer
    ports:
        - port: 80
            targetPort: 8080 
    selector:
        app: example
    ```
- Link tài liệu tham khảo: https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html


## 4. Triển khai K8S Dashboard