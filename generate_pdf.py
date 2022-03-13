list_file = [
    'documents/items/architecture.md',
    'documents/items/pod.md',
    'documents/items/controller.md',
    'documents/items/service.md',
    'documents/items/volume.md',
    'documents/items/configmap-and-secret.md',
    'documents/items/deployments.md',
    'documents/items/statefulset.md',
    'documents/items/auto-scaling.md',
]

breaker = '<div class="page"/>'

writer = open('documents/docs/kubernetes.md', 'w')

for file in list_file:
    with open(file) as reader:
        content = reader.read()
        content_with_break = '\n\n' + breaker + '\n\n' + content
        writer.write(content_with_break)

writer.close()
