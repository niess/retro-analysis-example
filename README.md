# Example analysis of Retro Monte Carlo events

- The [collect-events.py](scripts/collect-events.py) script collects a set of
  `.voltage.json` files into Python data structures. For instance,

```bash
./scripts/collect-events.py \
    /sps/grand/omartino/data/GRAND/voltageOutput/hotspot-150x67km2/HS1_freespace/jsons/ \
    -o data/HS1.pkl
```

- The [plot-events.py](scripts/plot-events.py) script plots some distributions
  of collected Monte Carlo events. For instance,

```bash
./scripts/plots-events.py data/HS1.pkl
```
