# istio分散トレーシングお試し

参考: https://istio.io/latest/docs/tasks/observability/distributed-tracing/jaeger/

## 準備
### istio導入

```shell
# レポジトリへ移動
cd $REPO_PATH

# istio用namespace
kubectl create namespace istio-system

# istio インストール
helm install istio-base istio/base -n istio-system
helm install istiod istio/istiod -n istio-system -f charts/istiod_values.yaml

# gateway インストール
helm install istio-ingress istio/gateway -n istio-system
```

### Jaeger/Grafana導入
```shell
# 監視用namespace
kubectl create namespace observability

# jaeger インストール
helm install jaeger jaegertracing/jaeger -n observability -f charts/jaeger_cassandra_values.yaml

# Grafana インストール
helm install -n observability graphana grafana/grafana
```

### アプリを実行
- お好きなレジストリへアプリケーションをビルドしてpush
- manifests/manifest.yaml 45, 108行目にimage情報を追記
```shell
kubectl apply -f manifests/manifest.yaml
```

## 動作確認
### アプリへIngress Gateway経由でアクセス
※localの場合はport-forwardしてアクセス
```shell
kubectl -n istio-system port-forward svc/istio-ingressgateway 32494:80
```

### jaeger UIへアクセス
```shell
export POD_NAME=$(kubectl get pods --namespace obserbability -l "app.kubernetes.io/instance=jaeger,app.kubernetes.io/component=query")
kubectl -n istio-system port-forward --namespace obserbability $POD_NAME 8080:16686
```

### Grapanaへアクセス
```shell
kubectl ort-forward -n observability graphana-grafana-7fc4cd9987-gwvdf 3000:3000

# パスワードのsecretを参照
kubectl get secret --namespace observability graphana-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

## 参考
- Istio
  - trace情報伝播参考
    - https://istio.io/latest/docs/tasks/observability/distributed-tracing/overview/
  - Jaeger周り
    - https://istio.io/latest/docs/tasks/observability/distributed-tracing/jaeger/
- Jaeger
  - Storageの選択
    - https://www.jaegertracing.io/docs/1.41/faq/#what-is-the-recommended-storage-backend
  - cassandra schema初期化shell
    - https://github.com/jaegertracing/jaeger/blob/main/plugin/storage/cassandra/schema/create.sh
- helm chart周り
  - istiod
    - https://artifacthub.io/packages/helm/istio-official/istiod
  - jaeger
    - https://artifacthub.io/packages/helm/jaegertracing/jaeger
  - cassandra
    - https://artifacthub.io/packages/helm/riftbit/cassandra
