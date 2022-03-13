# ConfigMap & Secret

Hầu hết các ứng dụng của chúng ta cần config để chạy (ví dụ như config cho database, config port, ... )

Trong k8s, để truyền các config vào container trong pod, ta có thể truyền chúng qua:
- Biến môi trường(env)
- K8S configmap

## env

k8s cung cấp cách để truyền các config vào trong container bằng cách thêm qua biến môi trường `env` khi khởi tạo pod.

Ví dụ file pod manifest, ở đây ta cần truyền biến `INTERVAL` vào trong container bằng cách thêm vào field `spec.containers.env`
    
```yaml
apiVersion: v1
kind: Pod
spec:
    containers:
        - image: luksa/fortune:env
          name: html-generator
          env:
            - name: INTERVAL
              value: "30"
```
    
Nhược điểm của phương pháp này:
- env không thể update trong container khi container đã chạy, muốn update phải xoá pod và chạy lại.
- khi số lượng pod lớn → config sẽ bị lặp lại hoặc file manifest tạo sẽ trở nên dài hơn nếu pod sử dụng nhiều config.

## ConfigMap

Đây là loại resource giúp ta tách các configuration của container khi khởi tạo pod. Tức là không cần phải hardcode ở thêm `specs.containers.env` khi tạo file pod manifest. Thay vào đó, ta chỉ việc khai báo sử dụng configmap này trong pod manifest mà thôi.

ConfigMap là dạng key-value. Khi sử dụng, chúng ta khai báo key ở trong file pod manifest, value sẽ tự động được truyền vào trong container như một biến env.

Ưu điểm của phương pháp này là các config được tập trung ở một chỗ và có thể sử dụng lại nhiều lần ở những pod khác nhau.

Ví dụ cách để tạo ConfigMap

- Cách đơn giản nhất là dùng cli
    
    ```bash
    $ kubectl create configmap mongodb-config \
            --from-literal=DATABASE=mongodb \
            --from-literal=ROOT_USER=mongodb \
            --from-literal=ROOT_PASSWORD=123456
    ```
        
- Hoặc dùng file config
    
    ```yaml
    # configmap.yaml

    apiVersion: v1
    kind: ConfigMap
    metadata:
        name: mongodb-config
    data:
        DATABASE: mongodb
        ROOT_USER: mongodb
        ROOT_PASSWORD: "123456"
    ```

    ```bash
    $ kubectl create -f configmap.yaml
    configmap/mongodb created
    ```

- Kiểm tra configmap

    ```bash
    $ kubectl get cm
    NAME               DATA   AGE
    mongodb            3      21m

    $ kubectl describe cm mongodb
    Name:         mongodb
    Namespace:    default
    Labels:       <none>
    Annotations:  <none>

    Data
    ====
    DATABASE:
    ----
    mongodb
    ROOT_PASSWORD:
    ----
    123456
    ROOT_USER:
    ----
    mongodb

    BinaryData
    ====

    Events:  <none>
    ```
        
        
- Sử dụng configmap trong pod
    
    - truyền từng entry trong configmap
        
        ```yaml
        apiVersion: v1
        kind: Pod
        metadata:
            name: mongodb
        spec:
            containers:
                - image: mongodb
                  name: mongodb
                  env:
                    - name: MONGO_INITDB_DATABASE
                      valueFrom:
                        configMapKeyRef:
                            name: mongodb-config
                            key: DATABASE
                    - name: MONGO_INITDB_ROOT_USERNAME
                      valueFrom:
                        configMapKeyRef:
                            name: mongodb-config
                            key: ROOT_USER
                    - name: MONGO_INITDB_ROOT_PASSWORD
                      valueFrom:
                        configMapKeyRef:
                            name: mongodb-config
                            key: ROOT_PASSWORD
        ```
        
    - hoặc truyền nhiều entry một lúc
        
        ```yaml
        apiVersion: v1
        kind: Pod
        metadata:
        	name: mongo-db
        spec:
        	containers:
        		- image: mongodb
        		  name: mongodb
        		  envFrom:
        			- prefix: MONGO_INITDB_
        			  configMapKeyRef:
        				name: mongodb-config
        ```
        

## Configmap với file config

Ngoài việc sử dụng configmap để truyền value dạng text vào pod, thì configmap còn hỗ trợ truyền value ở dạng file config.

Ví dụ về configmap với file config

- Ta có 1 file nginx config `nginx.conf`

    ```
    # nginx.conf
    
    server {
        listen  80;
        server_name _;
        gzip on;
        gzip_types text/plain application/xml;
    
        location / {
            root /usr/share/nginx/html;
            index index.html index.htm;
        }
    }
    ```
        
- Tiêp theo, tạo configmap với file config này. Trong đó, key sẽ là tên file và value sẽ là content của file config
        
    ```
    $ kubectl create configmap nginx-config --from-file nginx.conf
    ```

- Kiểm tra configmap đã được tạo hay chưa

    ```bash
    $ kubectl describe cm nginx-config

    Name:         nginx-config
    Namespace:    default
    Labels:       <none>
    Annotations:  <none>

    Data
    ====
    nginx.conf:
    ----
    server {
    listen  80;
    server_name _;
    gzip on;
    gzip_types text/plain application/xml;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
    }
    }

    BinaryData
    ====

    Events:  <none>

    ```
        
- Tiếp theo tạo 1 pod sử dụng configmap `nginx-config` chúng ta vừa tạo:
        
    ```yaml
    apiVersion: v1
    kind: Pod
    metadata:
        name: nginx-pod
    spec:
        containers:
        - image: nginx:alpine
            name: web-server
            ports:
                - containerPort: 80
            volumeMounts:
                - name: config
                  mountPath: /etc/nginx/conf.d
                  readOnly: true
        volumes:
            - name: config
              configMap:
                name: nginx-config
                defaultMode: "6600"
    ```
        
    Ở đây, configmap được sử dụng như một volume. Lúc này volume sẽ có 1 file tên là `nginx.conf` , sau đó được mount vào folder `/etc/nginx/config` trong container.
        

## Secret

Tương tự như ConfigMap, Secret cũng dùng để lưu trữ config nhưng ở dạng sensitive data. Và không phải ai cũng quyền read Secret.

- Ví dụ tạo secret 
    
    ```bash
    $ kubectl create secret generic mongodb-config \
                    --from-literal DATABASE=mongodb \
                    --from-literal ROOT_USER=mongodb \
                    --from-literal ROOT_PASSWORD=123456
    
    secret/mongodb-config created
    ```

- Kiểm tra secret vừa tạo

    ```bash
    # show list secret
    $ kubectl get secret
    NAME                  TYPE                                  DATA   AGE
    mongodb-config        Opaque                                3      43s

    # describe secret mongodb-config
    $ kubectl describe secret mongodb-config
    Name:         mongodb-config
    Namespace:    default
    Labels:       <none>
    Annotations:  <none>

    Type:  Opaque

    Data
    ====
    DATABASE:       7 bytes
    ROOT_PASSWORD:  6 bytes
    ROOT_USER:      7 bytes
    ```
    
- Cách sử dụng trong pod tương tự như configmap
    
    ```yaml
    apiVersion: v1
    kind: Pod
    metadata:
        name: mongo-db
    spec:
        containers:
            - image: mongodb
              name: mongodb
              envFrom:
                - prefix: MONGO_INITDB_
                  secretRef:
                    name: mongodb-config
    ```