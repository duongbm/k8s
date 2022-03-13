# K8s Deployment

Deployment là 1 controller resource trong k8s, nó là thành phần giúp chúng ta update apps trên cluster và hiểu được tính năng zero downtime của k8s.

1. Cập nhật app trong pod

    Bắt đầu với ví dụ chúng ta có một app đang chạy trên k8s cluster. App này được deploy bằng Replicaset với số `replicas` là 3 và một Service expose traffic cho client bên ngoài access vào trong pod.

    Sau khi dev team hoàn thành một tính năng mới, chúng ta cần build lại image mới và update lại image của các Pod đang chạy. Có 2 cách để thực hiện việc này, đó là:
        - Xoá toàn bộ các pod cũ, sau đó deploy pod mới với image mới. (Recreate)
        - Deploy pod mới xong xoá mới pod cũ.(Rolling Update)

    1.1 Recreate

    Đối với cách deploy này, chúng ta có thể thực hiện cập nhật lại Pod template bằng cách sửa Replicaset. Sau đó toàn bộ pod cũ sẽ bị xoá, Replicaset sẽ tạo pull image mới về và chạy pod mới.

    ![](../images/recreate-update.png)

    Tuy nhiên, cách này có nhược điểm đó là sẽ có downtime trong quá trình deploy và client không thể sử dụng app. 

    1.2 RollingUpdate
    
    Nếu bạn không chấp nhận downtime trong quá trình deploy, đây là cách giải quyết

    a. Deploy pod mới, xong xoá toàn bộ pod cũ

    Với kịch bản này, chúng ta cần 2 hệ thống phần cứng để chạy song song trong quá trình deploy. Khi pod mới được deploy thành công, ta mới xoá các pod cũ.

    Chiến lược này được gọi là blue-green deployment. Có 2 phần cứng để chạy 2 môi trường production. 
    - Client sẽ sử dụng môi trường (gọi là blue)
    - Phiên bản mới được deploy (gọi là green)
    - Sau khi deploy thành công, client sẽ được route qua môi trường green.

    b. Thay thế từng pod(RollingUpdate)

    Kịch bản này các pod cũ sẽ được thay thế dần dần với các pod mới, quá trình này lặp lại đến khi các pod cũ được thay thế hết. Lúc này Service sẽ route request đến cả pod cũ và mới.
     
    Với cách này, hệ thống sẽ không có downtime trong quá trình deploy nhưng lại tốn thêm tài nguyên cho bản deploy mới.

2. Deployment Controller

    Deployment là một resource trong k8s dùng để deploy và update ứng dụng một cách dễ dàng. Deployment cung cấp cả 2 chiến lược update Recreate và RollingUpdate (như đã nói ở trên). Sẽ có history cho các bản cập nhật, do đó ta có thể dễ dàng rollout hoặc rollback một version bất của ứng dụng.

    Deployment là một high level resource, bởi vì khi tạo Deployment về bản chất nó sẽ tạo một Replicaset bên dưới, Replicaset này sẽ tạo và quản lý các pod.

    2.1 Create deployment
    
    Ví dụ về file manifest

    ```yaml
    # deployment.yaml

    apiVersion: apps/v1
    kind: Deployment
    metadata:
        name: kubia-deployment
    spec:
        replicas: 3
        template:
            metadata:
                name: kubia
                labels:
                    app: kubia
            spec:
                containers:
                    - image: luksa/kubia:v1
                       name: nodejs
    ```

    ```
    $ kubectl apply -f deployment.yaml
    ```

    Khi tạo deployment, nó sẽ tạo một Replicaset bên dưới rồi Replicaset mới tạo Pod, chúng ta dùng câu lệnh để kiểm tra

    ``` 
    # check deployment
    $ kubectl get deploy

    # check status deployment
    $ kubectl rollout status deployment kubia-deployment

    # check replicaset
    $ kubectl get rs

    # check pod
    $ kubectl get pods
    ```

    2.2 Update deploy
    
    Ứng dụng đang được deploy với version là v1, bây giờ chúng ta cần update lên version v2. Do đó cần phải update lại image của các pod đang chạy.

    Khi update ứng dụng bằng deployment, nó sử dụng chiến lược `RollingUpdate` mặc định.

    Ví dụ update lại image của các pod.

    ```
    $ kubectl set image deployment kubia nodejs=luksa/kubia:v2
    ```

    Khi câu lệnh này được thực thi, ngay lập tức các pod v1 bị xoá và được thay thế dần bằng các pod v2.

    Lúc này một replicaset v2 được tạo mới, replicaset v2 sẽ quản lý các pod v2. 

    Mặc dù các pod v1 bị xoá, nhưng replicaset v1 sẽ không bị xoá. Chúng ta không cần quan tâm đến replicaset v1, tuy nhiên cũng không nên xoá nó, bởi vì chúng ta đang tương tác và sử dụng Deployment, hãy để Deployment quản lý các replicaset tự động.

    2.3 Rollback deployment
    
    Sau khi update lên v2, chúng ta thấy v2 này đã xảy ra lỗi, cần phải trở về phiên bản v1 nhanh nhất có thể.

    Deployment sẽ giúp giải quyết vấn đề này với câu lệnh

    ```
    $ kubectl rollout undo deployment kubia-deployment
    ```

    Lúc này ứng dụng đã trở về phiên bản v1. Về bản chất, deployment sử dụng lại replicaset v1 để tạo pod v1. Đó chính là lý do không nên tự ý xoá replicaset của deployment.

    2.4 Rollout rate

    Khi thực hiện rollout hoặc rollback, ở bên dưới sẽ thực hiện việc tạo 1 pod version mới, sau khi tạo và run xong pod mới này thì 1 pod version cũ sẽ được xoá đi và 1 pod version mới được khởi tạo. Quá trình này lặp lại đến khi không còn tồn tại pod version cũ.

    Các pod được thay thế 1-1, tuy nhiên có thể thay đổi tỉ lệ này bằng các properties `maxSurge` và `maxUnavailable`

    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    spec:
        strategy:
            rollingUpdate:
                maxSurge: 1
                maxUnavailable: 0
            type: RollingUpdate
        ...
    ```

    - maxSurge + replicas = Số pod tối đa có thể dùng để deploy.
    - replicas - maxUnavailable = Số pod ở trạng thái available.

        ![](../images/maxsurge-maxunavailable.png)