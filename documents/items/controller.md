# Controller

## ReplicationController(RC)

Là controller có nhiệm vụ đảm bảo đủ một số lượng pod nhất định chạy trong cluster không thừa không thiếu. Khi 1 pod bị crash → RC sẽ tạo pod mới thay thế.

Để tạo file manifest cho Replication Controller, cần lưu ý 3 thuộc tính sau: 
- label selector: xác định pod nào sẽ được RC quản lý.
- replica count: số lượng pod.
- pod template: template dùng để tạo pod mới.

Ví dụ tạo Replication Controller với 3 pod luôn available trong hệ thống.

- Đầu tiên tạo file manifest có tên `kubia-rc.yaml`
    
    ```yaml
    # kubia-rc.yaml
    
    apiVersion: v1
    kind: ReplicationController
    metadata:
    	name: kubia-rc
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
    					- name: kubia
    						image: luksa/kubia
    						ports:
    							- containerPort: 8080
    ```
    
- Submit file manifest lên cluster
    
    ```bash
    $ kubectl create -f kubia-rc.yaml

    replicationcontroller/kubia-rc created
    ```

- Kiểm tra replication controller đã chắc chắn được khởi tạo hay chưa bằng câu lệnh

    ```bash
    $ kubectl get rc

    NAME       DESIRED   CURRENT   READY   AGE
    kubia-rc   3         3         3       63s
    ```
- Kiểm tra xem có đúng 3 pod đã được khởi tạo hay chưa.

    ```bash
    $ kubectl get pods

    NAME             READY   STATUS    RESTARTS   AGE
    kubia-rc-4tkzl   1/1     Running   0          2m28s
    kubia-rc-5vbrl   1/1     Running   0          2m29s
    kubia-rc-z79cs   1/1     Running   0          2m28s
    ```

- Thực hiện xoá 1 pod, để xem RC sẽ xử lý như nào

    - Đầu tiên xoá 1 pod
        ```
        $ kubectl delete pod kubia-rc-4tkzl

        pod "kubia-rc-4tkzl" deleted
        ```
    - kiểm tra pods

        ```bash
        $ kubectl get pods

        NAME             READY   STATUS        RESTARTS   AGE
        kubia-rc-4tkzl   1/1     Terminating   0          4m28s
        kubia-rc-5vbrl   1/1     Running       0          4m28s
        kubia-rc-z79cs   1/1     Running       0          4m28s
        kubia-rc-12yt8   1/1     Running       0          9s
        ```

        Ta thấy 1 pod mới `kubia-rc-12yt8` được khởi tạo để thay thế pod `kubia-rc-4tkzl` vừa bị xoá. RC `kubia-rc` tạo pod này và quản lý nó để đảm bảo hệ thống luôn có 3 pods.

- Để scale up/down sô pod, có thể dùng command:
    
    ```bash
    $ kubectl scale rc kubia-rc --replicas=10 # scale up
    replicationcontroller/kubia-rc scaled

    $ kubectl scale rc kubia-rc --replicas=2 # scale down
    replicationcontroller/kubia-rc scaled
    ```
    
- Xoá replication controller
    
    ```bash
    $ kubectl delete rc kubia-rc # xoá controller và xoá luôn pod
    replicationcontroller "kubia-rc" deleted
    
    $ kubectl delete rc kubia-rc --cascade=orphan # xoá controller không xoá pods
    replicationcontroller "kubia-rc" deleted
    ```
    

## Replicaset(RS)

Replicaset là bản nâng cấp của ReplicationController, đó là được tối ưu hơn ở phần label selector.

So với RC, trong phần label selector của RS, có thể dùng các điều kiện và expression nâng cao hơn để select nhiều pod hơn. 

Ví dụ để tạo Replicaset trên k8s

- Đầu tiên, tạo file manifest `kubia-replicaset.yaml`:
    
    ```yaml
    # kubia-replicaset.yaml
    
    apiVersion: apps/v1
    kind: ReplicaSet
    metadata:
      name: kubia-replicaset
    spec:
      replicas: 3
      selector:
        matchExpressions:
          - key: app
            operator: In
            values:
              - kubia-rs
      template:
        ...
    ```
    
- Submit file lên cluster
    
    ```bash
    $ kubectl create -f kubia-replicaset.yaml 

    replicaset.apps/kubia-replicaset created
    ```

- Kiểm tra replicaset đã được khởi tạo hay chưa

    ```bash
    $ kubectl get rs

    NAME               DESIRED   CURRENT   READY   AGE
    kubia-replicaset   3         3         3       61s
    ```

- Kiểm tra số pods

    ```bash
    $ kubectl get pods

    NAME                     READY   STATUS    RESTARTS   AGE
    kubia-replicaset-2xn6r   1/1     Running   0          100s
    kubia-replicaset-cc4sw   1/1     Running   0          100s
    kubia-replicaset-jjwnl   1/1     Running   0          100s
    ```

- Xoá Replicaset
    
    ```bash
    $ kubectl delete rs kubia-replicaset # xoá replicaset và xoá luôn pod
    replicaset.apps "kubia-replicaset" deleted
    
    $ kubectl delete rc kubia-rc --cascade=orphan # xoá replicaset không xoá pods
    replicaset.apps "kubia-replicaset" deleted
    ```
    

## DaemonSet(DS)

![DaemonSet](../images/daemonset.png)

Là controller có nhiệm vụ đảm bảo chỉ có duy nhất một pod được deploy trên mỗi worker node. Khi có 1 worker node được thêm vào cluster, daemonset sẽ tự động deploy pod lên worker node này. DS phù hợp với các ứng dụng log collector hoặc monitor worker node.

Ví dụ tạo Daemonset trên k8s

- Tạo file manifest `daemonset.yaml`:
    
    ```yaml
    # daemonset.yaml
    
    apiVersion: apps/v1
    kind: DaemonSet
    metadata:
      name: ssd-monitor
    spec:
      selector:
        matchLabels:
          app: ssd-monitor
      template:
        metadata:
          labels:
            app: ssd-monitor
        spec:
          containers:
            - image: luksa/ssd-monitor
              name: main
    ```
    
- Submit file lên cluster
    

    ```bash
    $ kubectl create -f daemonset.yaml

    daemonset.apps/ssd-monitor created
    ```

 - Kiểm tra Daemonset

    ```bash
    $ kubectl get ds

    NAME          DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE
    ssd-monitor   1         1         1       1            1
    ```

- Kiểm tra số pods

    ```
    $ kubectl get pods

    NAME                READY   STATUS    RESTARTS   AGE
    ssd-monitor-sf48d   1/1     Running   0          2m28s
    ```

- Sau khi cho thêm 1 worker node join vào cluster, ta kiểm tra

    ```bash
    $ kubectl get ds
    NAME          DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE
    ssd-monitor   2         2         2       2            2

    $ kubectl get pods
    NAME                READY   STATUS    RESTARTS   AGE
    ssd-monitor-kkkvr   1/1     Running   0          72s
    ssd-monitor-sf48d   1/1     Running   0          8m6s
    ```
    
    Như ta đã thấy, khi thêm 1 node mới, DS sẽ tự động deploy pod cho node mới này.

- Xoá daemonset

    ```bash
    $ kubectl delete ds ssd-monitor

    daemonset.apps "ssd-monitor" deleted
    ```

## Job Controller(job)

Ngoài Replicaset, DaemonSet, là những controller hỗ trợ chạy những continous tasks. K8S còn hỗ trợ để chạy những completable tasks qua Job Controller. (job controller phù hợp với những ad-hoc task, initial jobs).

Ví dụ tạo Job controller

- Tạo file manifest `jobs.yaml`
    
    ```yaml
    # jobs.yaml
    
    apiVersion: batch/v1
    kind: Job
    metadata:
      name: batch-job
    spec:
      template:
        metadata:
          labels:
            app: batch-job
        spec:
          restartPolicy: OnFailure
          containers:
            - name: main
              image: luksa/batch-job
    ```

- Submit lên cluster
    
    ```
    $ kubectl create -f jobs.yaml
    job.batch/batch-job created
    ```

- Kiểm tra jobs controller và pods

    ```
    $ kubectl get jobs

    NAME        COMPLETIONS   DURATION   AGE
    batch-job   0/1           30s        30s

    $ kubectl get pods
    NAME              READY   STATUS    RESTARTS   AGE
    batch-job-w9bl9   1/1     Running   0          84s

    # lúc này job chưa chạy xong, vẫn đang ở trạng thái running
    # Sau 2 phút, kiểm tra lại

    $ kubectl get jobs
    NAME        COMPLETIONS   DURATION   AGE
    batch-job   1/1           2m6s       2m42s

    $ kubectl get pods
    NAME              READY   STATUS      RESTARTS   AGE
    batch-job-w9bl9   0/1     Completed   0          3m21s

    # jobs đã completed.
    ```



## CronJob Controller

Kubernetes cũng hỗ trợ schedule task qua Cronjob Controller. Áp dụng những rule giống như cronjob trên linux.

Ví dụ tạo Cronjob controller

- Tạo file manifest `cronjobs.yaml`
    
    ```yaml
    # cronjobs.yaml
    
    apiVersion: batch/v1
    kind: CronJob
    metadata:
      name: schedule-job
    spec:
      schedule: "0,1,2,3 * * * *"
      jobTemplate:
        spec:
          template:
            metadata:
              labels:
                app: schedule-job
            spec:
              restartPolicy: OnFailure
              containers:
                - name: main
                  image: luksa/batch-job
    ```
- Submit file lên cluster

    ```bash
    $ kubectl create -f cronjobs.yaml

    cronjob.batch/schedule-job created
    ```

- Kiểm tra cronjobs và pod

    ```bash
    # kiểm tra cronjobs
    $ kubectl get cj 

    NAME           SCHEDULE          SUSPEND   ACTIVE   LAST SCHEDULE   AGE
    schedule-job   0,1,2,3 * * * *   False     1        22s             7m3s


    # kiểm tra pods
    $ kubectl get pods

    NAME                          READY   STATUS    RESTARTS   AGE
    schedule-job-27451740-6tlv7   1/1     Running   0          66s
    schedule-job-27451741-d842x   1/1     Running   0          6s
    ```

- Xoá cronjob controller

    ```bash
    $ kubectl delete cj schedule-job
    ```