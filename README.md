# Jaeger HotROD Demo App Charm for Kubernetes

## Description

Example charm that deploys Jaeger demo application and presents an example usage of [Jaeger charm](https://github.com/przemeklal/charm-jaeger) and Juju `jaeger` relation over `distributed-tracing` interface.

## Usage

To build and deploy:

```
charmcraft pack
juju deploy ./jaeger-hotrod.charm --resource hotrod-image=jaegertracing/example-hotrod:latest
```

Ensure that [Jaeger charm](https://github.com/przemeklal/charm-jaeger) is deployed.

Relate with jaeger:
```
juju add-relation jaeger-hotrod:jaeger jaeger:jaeger
```

Open your browser and navigate to address from juju status - in this example `http://10.1.19.185:8080`:
```
jaeger-hotrod/0*      active    idle   10.1.19.185
```

Click on any button to order you ride. You can click on the `[find trace]` link to open Jager Query UI directly.

## Developing

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests
