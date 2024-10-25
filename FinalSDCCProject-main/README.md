# FinalSDCCProject
Il contenuto del seguente repository tratta lo sviluppo di una medesima applicazione distibuita su due architetture diverse: a microservizi mediante un cluster Elastic Kubernetes Service e serverless mediante la AWS Lambda. Lo scopo dello sviluppo è verificare la differenza di costi/prestazioni e la difficoltà di implementazione/sviluppo tra le due architetture. L'applicazione è divisa in tre servizi principali:
1. una Web App che permette di effettuare una login ed inserire una foto su un bucket S3;
2. un servizio di riconoscimento facciale che prende in input la foto precedenetemente inserita in S3 ed esegue il riconoscimento mediante un dataset di immagini statiche inserite in precedenza;
3. un servizio di Email che permette di avvisare le persone all'interno della foto mediante una notifica via email.

- I tre servizi sono completamente distribuiti: nel caso di Kubernetes - Cluster EKS comunicano tra loro mediante gRPC, nel caso di serverless Lambda comunicano tra loro mediante chiamate XML.

## Deploy dell'architettura a microservizi - EKS Cluster

1. Per la creazione di una VPC e cluster EKS rimandiamo alla guida ufficiale: https://docs.aws.amazon.com/it_it/eks/latest/userguide/creating-a-vpc.html.
2. Avere installato kubectl ed AWS CLI in locale sulla propria macchhina.
3. Creare un gruppo di nodi:
-   si raccomanda di utilizzare macchine EC2 t4g.small o superiori (il deployment face_recognition richiede più capacità di calcolo e RAM).
4. Cambiare il contesto di kubectl con il comando:
```bash
>> aws eks update-kubeconfig --region region-code --name my-cluster
```
5. Spostarsi sulla cartella K8s ed eseguire il seguente comando per installare il Metric Server:
```bash
>> kubectl apply -f components.yaml
```
6. Spostarsi nella cartella K8 ed eseguire il seguente comando per fare installare i deployment all'interno del cluster EKS:
```bash
>> kubectl apply -f .
```
7. Installare gli HPA (Horizontal Pod Autoscaler) per tutti i deployment mediante i seguenti comandi:
```bash
>> kubectl autoscale deployment app-deployment --cpu-percent=25 --min=1 --max=10
>> kubectl autoscale deployment face-rec-deployment --cpu-percent=25 --min=1 --max=10
>> kubectl autoscale deployment mail-deployment --cpu-percent=25 --min=1 --max=10
```
Per il corretto funzionamento dell'applicativo bisogna aggiungere un Service Mesh. Nel nostro caso è stato inserito Linkerd. Alleghiamo di seguito i comandi per l'installazione ma rimandiamo alla guida ufficile del sito per ulteriori chiarimenti:
```bash
>> curl --proto '=https' --tlsv1.2 -sSfL https://run.linkerd.io/install | sh
>> linkerd version
>> linkerd check --pre
>> linkerd install --crds | kubectl apply -f -
>> linkerd install | kubectl apply -f -
>> linkerd check
>> kubectl get -n default deploy -o yaml \
  | linkerd inject - \
  | kubectl apply -f -
>> linkerd -n default check --proxy
```
Per verificare il corretto funzionamento di Linkerd è possibile utilizzare il seguente comando:
```bash
>> kubectl -n default get po -o jsonpath='{.items[0].spec.containers[*].name}'
```
Se l'installazione è andata a buon fine, l'ouput  sarà del tipo:
```bash
linkerd-proxy CONTAINER
```
La cartella dash contiene tutti i file necessari per eseguire la dashboard di Kubernetes, utile per monitorare l'andamento del cluster. Rimandiamo alla guida ufficiale ma alleghiamo di seguito i comandi più importanti:
```bash
>> kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
>> kubectl apply -f dashboard-adminuser.yaml
>> kubectl -n kubernetes-dashboard create token admin-user
>> kubectl proxy
```
Ottenuto il token è possibile usarlo al link: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
