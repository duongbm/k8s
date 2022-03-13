# Pod

## Giới thiệu Pod

Pod là thành phần trong k8s, dùng để triển khai và chạy các ứng dụng(cụ thể là các container).

Có thể triển khai một hoặc nhiều container trong một pod (nhưng thông thường chỉ nên run pod với 1 container). Những containers trong cùng một pod, cùng chia sẻ network namespace → có thể truy cập với nhau qua `localhost`.

Mỗi pod được tạo ra sẽ có 1 IP(virtual IP), và các pods có thể truy cập với nhau thông qua IP này.

Ví dụ để tạo 1 pod trên k8s cluster.

- Bước 1: Ta cần 1 file pod manifest như sau (giả sử đặt tên là `kubia.yaml`):
        
    ```yaml
    # kubia.yaml
    
    apiVersion: v1
    kind: Pod
    metadata:
        name: kubia
    spec:
        containers:
            - image: luksa/kubia
                name: kubia
                ports:
                    - containerPorts: 8080
    ```

    Đây là một file manifest cơ bản để tạo pod, nó có các thuộc tính cần lưu ý:

    * apiVersion: là version của API Server tạo ra resource(ở đây là pod)

    * kind: là loại resource chúng ta muốn tạo, có thể là Pod, Replicaset, Service,...

    * metadata: chứa các thông tin như name, labels, annotations

    * spec: tuỳ vào loại resource chúng ta cần tạo, ở đây là pod sẽ chứa các thông tin liên quan đến các cấu hình cho pod như image, containers, volume, ...
        
- Tiếp theo, cần dùng câu lệnh sau để submit file pod config lên cluster và cluster sẽ khởi tạo pod có tên là `kubia`:
        
    ```bash
    $ kubectl create -f kubia.yaml

    pod/kubia created
    ```
        
- Bây giờ kiểm tra xem pod đó đã được tạo hay chưa, có bị lỗi không
        
    ```bash
    $ kubectl get pods
    NAME          READY   STATUS    RESTARTS   AGE
    kubia         1/1     Running   0          29h
    ```

    Ở trạng thái `Running`, tức là pod đã được khởi tạo và chạy thành công.
        
- Để kiểm tra log của pod `kubia`, ta sử dụng câu lệnh
    
    ```bash
    $ kubectl logs kubia

    Kubia server starting...
    ```
     
- Bây giờ cần expose port của pod ra ngoài để test, ta sử dụng câu lệnh đơn giản sau(lệnh này chỉ dùng để test, không dùng cho production)
    
    ```bash
    $ kubectl port-forward kubia 8888:8080
    
    Forwarding from 127.0.0.1:8888 -> 8080
    Forwarding from [::1]:8888 -> 8080
    ```
    
- Kiểm tra bằng curl, send request đến địa chỉ `localhost:8888`
    
    ```bash
    $ curl localhost:8888
    
    You've hit kubia
    ```
    

## Pod labels

Labels là metadata(dạng key-value) được gán vào không chỉ Pod mà còn cho các resource khác trong k8s.

Dùng pod labels để phân chia các pod khác nhau tuỳ thuộc vào dự án hoặc môi trường. Một Pod có thể có nhiều hơn 1 labels.

- Ví dụ file manifest, dùng để tạo một pod với labels
    
    ```yaml
    # kubia-label.yaml

    apiVersion: v1
    kind: Pod
    metadata:
        name: kubia-label
        labels:
            env: prod
    spec:
        containers: 
            ...
    ```
    
    Có thể thấy, điểm khác so với ví dụ trước chỉ là có thêm cặp giá trị `env:prod` ở trường `metadata.lables`.

    Submit lên cluster:

    ```bash
    $ kubectl create -f kubia-label.yaml

    pod/kubia-label created
    ```
    
- Bây giờ tạo label cho pod `kubia` (ở ví dụ trước)
    
    ```bash
    $ kubectl label pod kubia env=debug

    pod/kubia labeled
    ```
    
- Overwrite label pod `kubia-label`
    
    ```bash
    $ kubectl label pod kubia-label env=debug --overwrite

    pod/kubia-label labeled
    ```
    
- Show list pod với label selector
    
    ```bash
    $ kubectl get pod -l env=prod # show all pod có label env=prod

    $ kubectl get pod -l env # show all pod có label key là env, không quan tâm giá trị value
    
    $ kubectl get pod -l '!env' # show all pod có mà không có label key là env

    $ kubectl get pod -L env # show all pod thêm colum có label là env

    NAME    READY   STATUS    RESTARTS   AGE   ENV
    kubia   1/1     Running   0          23m   debug
    ```
    

## Pod Annotation

Giống như labels, annotation được gán cho mọi resource trong k8s.

Chỉ có tác dụng lưu trữ các thông tin metadata(author, version, created date, ...) dùng để kết nối với thirdparty tools hoặc cung cấp thông tin cho k8s administrator.

- Để annotate cho pod `kubia`, dùng command sau:
    
    ```bash
    $ kubectl annotate pod kubia com.example/k8s="annotate k8s"

    pod/kubia annotated
    ```
    

## Namespace

Như đã biết, labels dùng để phân chia các pod theo môi trường hoặc dự án nhưng chỉ ở mức định danh. Còn tài nguyên thì vẫn sử dụng chung nhau.

Do đó, namespace, là thành phần sẽ phân chia tài nguyên của các resource trong k8s một cách độc lập, giữa các môi trường hoặc dự án. Ví dụ: ta cần phải chia tài nguyên giữa các môi trường dev, production, QA.

Mặc định các resource được tạo trong namespace `default`

- Show toàn bộ namespace trong cluster
    
    ```bash
    $ kubectl get namespace
    
    # hoặc
    
    $ kubectl get ns

    NAME                   STATUS   AGE
    default                Active   47h
    kube-node-lease        Active   47h
    kube-public            Active   47h
    kube-system            Active   47h
    kubernetes-dashboard   Active   36h
    ```
    
- Show pod trong một namespace cụ thể
    
    ```bash
    $ kubectl get pod --namespace kube-system

    NAME                       READY   STATUS    RESTARTS   AGE
    coredns-55b9c7d86b-bllv6   1/1     Running   0          47h
    kube-proxy-ppf7v           1/1     Running   0          36h
    ```
    
- Tạo namespace có tên là `custom`:
    
    ```bash
    $ kubectl create namespace custom

    namespace/custom created
    ```
    
- Tạo pod trong namespace `custom`:
    
    ```bash
    $ kubectl apply -f kubia.yaml -n custom
    
    pod/kubia created
    ```
    

## Pod Deleting

- Xoá pod theo name
    
    ```bash
    $ kubectl delete pod kubia # xoá pod có tên là kubia

    pod "kubia" deleted
    ```
    
- Xoá pod bằng label
    
    ```bash
    $ kubectl delete pod -l env=debug

    pod "kubia" deleted
    ```
    
- Xoá toàn bộ pod
    
    ```bash
    $ kubectl delete pod --all

    pod "kubia" deleted
    pod "kubia-label" deleted
    ```
